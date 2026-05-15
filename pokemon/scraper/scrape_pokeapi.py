"""
Pulls all Pokemon data from the official PokeAPI (pokeapi.co).
No scraping — pure JSON REST API.

Fills these tables in pokebase_champions.db:
  natures      — all 25 natures with stat boosts/drops
  abilities    — all ~300 abilities with English description
  pokemon      — all 1025+ species (INSERT OR IGNORE so pokebase data wins)
  type_chart   — defensive multipliers for all pokemon types
  moves        — all ~900 moves with full details (INSERT OR IGNORE)

Run:  python scrape_pokeapi.py
Deps: pip install aiohttp
"""
import asyncio
import json
import sqlite3
import re
from pathlib import Path

try:
    import aiohttp
except ImportError:
    raise SystemExit("Missing dependency — run: pip install aiohttp")

BASE      = "https://pokeapi.co/api/v2"
DB_PATH   = "pokebase_champions.db"
SEM_LIMIT = 20          # max concurrent requests
TIMEOUT   = aiohttp.ClientTimeout(total=30)

# ── Type chart constants ──────────────────────────────────────────────────────
# Full 18×18 Gen-6+ type chart.  chart[ATK][DEF] = multiplier (as string "2","0.5","0","1")
TYPES = [
    "Normal","Fire","Water","Electric","Grass","Ice",
    "Fighting","Poison","Ground","Flying","Psychic","Bug",
    "Rock","Ghost","Dragon","Dark","Steel","Fairy",
]

# fmt: off
# Rows = attacking type, Cols = defending type (same order as TYPES list above)
# Values: 2=super, .5=not very, 0=immune, 1=normal
_RAW = [
#  Nor  Fir  Wat  Ele  Gra  Ice  Fig  Poi  Gro  Fly  Psy  Bug  Roc  Gho  Dra  Dar  Ste  Fai
  [ 1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1, 0.5,  0,   1,   1,  0.5,  1  ],  # Normal
  [ 1,  0.5, 0.5,  1,   2,   2,   1,   1,   1,   1,   1,   2,  0.5, 1,  0.5,  1,   2,   1  ],  # Fire
  [ 1,   2,  0.5,  1,  0.5,  1,   1,   1,   2,   1,   1,   1,  2,   1,  0.5,  1,   1,   1  ],  # Water
  [ 1,   1,   2,  0.5, 0.5,  1,   1,   1,   0,   2,   1,   1,  1,   1,  0.5,  1,   1,   1  ],  # Electric
  [ 1,  0.5,  2,   1,  0.5,  1,   1,  0.5,  2,  0.5,  1,  0.5, 2,   1,  0.5,  1,  0.5,  1  ],  # Grass
  [ 1,  0.5, 0.5,  1,   2,  0.5,  1,   1,   2,   2,   1,   1,  1,   1,   2,   1,  0.5,  1  ],  # Ice
  [ 2,   1,   1,   1,   1,   2,   1,  0.5,  1,  0.5, 0.5, 0.5, 2,   0,   1,   2,   2,  0.5 ],  # Fighting
  [ 1,   1,   1,   1,   2,   1,   1,  0.5, 0.5,  1,   1,   1,  1,  0.5,  1,   1,   0,   2  ],  # Poison
  [ 1,   2,   1,   2,  0.5,  1,   1,   2,   1,   0,   1,  0.5, 2,   1,   1,   1,   2,   1  ],  # Ground
  [ 1,   1,   1,  0.5,  2,   1,   2,   1,   1,   1,   1,   2, 0.5,  1,   1,   1,  0.5,  1  ],  # Flying
  [ 1,   1,   1,   1,   1,   1,   2,   2,   1,   1,  0.5,  1,  1,   1,   1,   0,  0.5,  1  ],  # Psychic
  [ 1,  0.5,  1,   1,   2,   1,  0.5, 0.5,  1,  0.5,  2,   1,  1,  0.5,  1,   2,  0.5, 0.5 ],  # Bug
  [ 1,   2,   1,   1,   1,   2,  0.5,  1,  0.5,  2,   1,   2,  1,   1,   1,   1,  0.5,  1  ],  # Rock
  [ 0,   1,   1,   1,   1,   1,   1,   1,   1,   1,   2,   1,  1,   2,   1,  0.5,  1,   1  ],  # Ghost
  [ 1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,  1,   1,   2,   1,  0.5,  0  ],  # Dragon
  [ 1,   1,   1,   1,   1,   1,  0.5,  1,   1,   1,   2,   1,  1,   2,   1,  0.5,  1,  0.5 ],  # Dark
  [ 1,  0.5,  0.5, 0.5,  1,   2,   1,   1,   1,   1,   1,   1,  2,   1,   1,   1,  0.5,  2  ],  # Steel
  [ 1,  0.5,  1,   1,   1,   1,   2,  0.5,  1,   1,   1,   1,  1,   1,   2,   2,  0.5,  1  ],  # Fairy
]
# fmt: on

def _mult_str(v):
    if v == 0:   return "0"
    if v == 0.5: return "1/2"
    if v == 2:   return "2"
    return "1"

TYPE_CHART_LOOKUP = {}   # (atk_type, def_type) -> "0"/"1/2"/"1"/"2"
for _ai, _atype in enumerate(TYPES):
    for _di, _dtype in enumerate(TYPES):
        _v = _RAW[_ai][_di]
        if _v != 1:
            TYPE_CHART_LOOKUP[(_atype, _dtype)] = _mult_str(_v)


def def_multipliers(pokemon_types: list[str]) -> dict:
    """Return {attacking_type: multiplier_str} for a Pokemon's type combo, omitting 1× entries."""
    result = {}
    for atk in TYPES:
        mult = 1.0
        for def_t in pokemon_types:
            raw_row = _RAW[TYPES.index(atk)]
            mult *= raw_row[TYPES.index(def_t)]
        if mult != 1.0:
            result[atk] = _mult_str(mult)
    return result


# ── DB helpers ────────────────────────────────────────────────────────────────

def init_tables(conn: sqlite3.Connection):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS natures (
        slug         TEXT PRIMARY KEY,
        name         TEXT,
        increased    TEXT,   -- stat name or NULL for neutral
        decreased    TEXT    -- stat name or NULL for neutral
    );

    CREATE TABLE IF NOT EXISTS abilities (
        slug        TEXT PRIMARY KEY,
        name        TEXT,
        description TEXT
    );

    -- Extend pokemon table with columns that may not exist yet
    CREATE TABLE IF NOT EXISTS pokemon (
        slug        TEXT PRIMARY KEY,
        name        TEXT,
        types       TEXT,
        hp          INTEGER, attack      INTEGER, defense     INTEGER,
        sp_attack   INTEGER, sp_defense  INTEGER, speed       INTEGER,
        image_url   TEXT
    );
    """)

    # Add columns to moves table if they don't exist yet
    for col, typedef in [
        ("priority",    "INTEGER"),
        ("target",      "TEXT"),
        ("effect",      "TEXT"),
        ("effect_chance", "INTEGER"),
    ]:
        try:
            conn.execute(f"ALTER TABLE moves ADD COLUMN {col} {typedef}")
        except sqlite3.OperationalError:
            pass

    conn.commit()


def _en(entries, field="name"):
    for e in entries:
        if e.get("language", {}).get("name") == "en":
            v = e.get(field) or e.get("text") or e.get("flavor_text") or ""
            return re.sub(r"\s+", " ", v).strip()
    return None


# ── Async fetch helpers ───────────────────────────────────────────────────────

async def get_json(session, sem, url):
    async with sem:
        async with session.get(url) as r:
            if r.status == 404:
                return None
            r.raise_for_status()
            return await r.json()


async def get_all(session, sem, urls):
    tasks = [get_json(session, sem, u) for u in urls]
    return await asyncio.gather(*tasks)


# ── Natures ───────────────────────────────────────────────────────────────────

async def fetch_natures(session, sem):
    index = await get_json(session, sem, f"{BASE}/nature?limit=100")
    urls  = [n["url"] for n in index["results"]]
    data  = await get_all(session, sem, urls)

    rows = []
    for d in data:
        if not d:
            continue
        inc = d.get("increased_stat")
        dec = d.get("decreased_stat")
        rows.append((
            d["name"],
            d["name"].title(),
            inc["name"] if inc else None,
            dec["name"] if dec else None,
        ))
    return rows


# ── Abilities ─────────────────────────────────────────────────────────────────

async def fetch_abilities(session, sem):
    index = await get_json(session, sem, f"{BASE}/ability?limit=500")
    urls  = [a["url"] for a in index["results"]]
    print(f"  Fetching {len(urls)} ability pages …")
    data  = await get_all(session, sem, urls)

    rows = []
    for d in data:
        if not d:
            continue
        desc = _en(d.get("effect_entries", []), "effect") or \
               _en(d.get("flavor_text_entries", []), "flavor_text")
        rows.append((d["name"], d["name"].replace("-", " ").title(), desc))
    return rows


# ── Moves ─────────────────────────────────────────────────────────────────────

async def fetch_moves(session, sem):
    index = await get_json(session, sem, f"{BASE}/move?limit=2000")
    urls  = [m["url"] for m in index["results"]]
    print(f"  Fetching {len(urls)} move pages …")
    data  = await get_all(session, sem, urls)

    rows = []
    for d in data:
        if not d:
            continue
        t    = d.get("type", {})
        dc   = d.get("damage_class", {})
        tgt  = d.get("target", {})
        desc = _en(d.get("effect_entries", []), "effect") or \
               _en(d.get("flavor_text_entries", []), "flavor_text")
        rows.append({
            "slug":          d["name"],
            "name":          d["name"].replace("-", " ").title(),
            "type":          t.get("name", "").title() if t else None,
            "damage_class":  dc.get("name") if dc else None,
            "power":         d.get("power"),
            "accuracy":      d.get("accuracy"),
            "pp":            d.get("pp"),
            "description":   desc,
            "priority":      d.get("priority"),
            "target":        tgt.get("name") if tgt else None,
            "effect_chance": d.get("effect_chance"),
        })
    return rows


# ── Pokemon ───────────────────────────────────────────────────────────────────

async def fetch_pokemon(session, sem):
    # Get all pokemon entries (includes forms like basculegion-male)
    index = await get_json(session, sem, f"{BASE}/pokemon?limit=2000")
    urls  = [p["url"] for p in index["results"]]
    print(f"  Fetching {len(urls)} pokemon pages …")

    # Batch to avoid memory spikes — process in chunks of 200
    all_rows = []
    chunk_size = 200
    for i in range(0, len(urls), chunk_size):
        chunk = urls[i:i+chunk_size]
        data  = await get_all(session, sem, chunk)
        for d in data:
            if not d:
                continue
            stats  = {s["stat"]["name"]: s["base_stat"] for s in d.get("stats", [])}
            types  = [t["type"]["name"].title() for t in d.get("types", [])]
            sprite = (d.get("sprites") or {}).get("front_default")
            all_rows.append({
                "slug":       d["name"],
                "name":       d["name"].replace("-", " ").title(),
                "types":      types,
                "hp":         stats.get("hp"),
                "attack":     stats.get("attack"),
                "defense":    stats.get("defense"),
                "sp_attack":  stats.get("special-attack"),
                "sp_defense": stats.get("special-defense"),
                "speed":      stats.get("speed"),
                "image_url":  sprite,
            })
        print(f"    … {min(i+chunk_size, len(urls))}/{len(urls)}")

    return all_rows


# ── Main ──────────────────────────────────────────────────────────────────────

async def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    init_tables(conn)

    sem = asyncio.Semaphore(SEM_LIMIT)
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:

        # ── Natures ──
        print("\n-- Natures --")
        natures = await fetch_natures(session, sem)
        conn.executemany(
            "INSERT OR REPLACE INTO natures (slug, name, increased, decreased) VALUES (?,?,?,?)",
            natures,
        )
        conn.commit()
        print(f"  {len(natures)} natures saved")

        # ── Abilities ──
        print("\n-- Abilities --")
        abilities = await fetch_abilities(session, sem)
        conn.executemany(
            "INSERT OR REPLACE INTO abilities (slug, name, description) VALUES (?,?,?)",
            abilities,
        )
        conn.commit()
        print(f"  {len(abilities)} abilities saved")

        # ── Moves ──
        print("\n-- Moves --")
        moves = await fetch_moves(session, sem)
        for mv in moves:
            conn.execute("""
                INSERT OR IGNORE INTO moves
                (slug, name, type, damage_class, power, accuracy, pp, description,
                 priority, target, effect_chance)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, (
                mv["slug"], mv["name"], mv["type"], mv["damage_class"],
                mv["power"], mv["accuracy"], mv["pp"], mv["description"],
                mv["priority"], mv["target"], mv["effect_chance"],
            ))
            # Update extra fields even for existing rows (pokebase.app won't have these)
            conn.execute("""
                UPDATE moves SET priority=?, target=?, effect_chance=?
                WHERE slug=? AND priority IS NULL
            """, (mv["priority"], mv["target"], mv["effect_chance"], mv["slug"]))
        conn.commit()
        print(f"  {len(moves)} moves saved")

        # ── Pokemon ──
        print("\n-- Pokemon --")
        pokemon = await fetch_pokemon(session, sem)

        for p in pokemon:
            conn.execute("""
                INSERT OR IGNORE INTO pokemon
                (slug, name, types, hp, attack, defense, sp_attack, sp_defense, speed, image_url)
                VALUES (?,?,?,?,?,?,?,?,?,?)
            """, (
                p["slug"], p["name"], json.dumps(p["types"]),
                p["hp"], p["attack"], p["defense"],
                p["sp_attack"], p["sp_defense"], p["speed"],
                p["image_url"],
            ))

            # type_chart: only insert if not already populated by pokebase.app scraper
            existing = conn.execute(
                "SELECT COUNT(*) FROM type_chart WHERE pokemon_slug=?", (p["slug"],)
            ).fetchone()[0]
            if existing == 0 and p["types"]:
                for atk_type, mult in def_multipliers(p["types"]).items():
                    conn.execute("""
                        INSERT OR IGNORE INTO type_chart (pokemon_slug, attacking_type, multiplier)
                        VALUES (?,?,?)
                    """, (p["slug"], atk_type, mult))

        conn.commit()
        print(f"  {len(pokemon)} pokemon saved")

    # ── Summary ──
    print("\n-- Database summary --")
    for table in ["natures", "abilities", "pokemon", "moves", "type_chart",
                  "items", "move_usage", "item_usage", "tournaments", "teams"]:
        try:
            n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"  {table:<22} {n:>6} rows")
        except sqlite3.OperationalError:
            print(f"  {table:<22}  (table not found)")

    conn.close()
    print(f"\nDone — database: {DB_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
