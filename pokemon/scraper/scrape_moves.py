"""
Scrapes all 937 moves from pokebase.app/pokemon-champions/moves.
For each move: stats (type, power, accuracy, pp, damageClass, description)
               + per-Pokemon tournament usage % from individual move pages.
Builds and populates a SQLite database linking Pokemon, moves, and tournaments.
"""
import requests
import json
import re
import time
import sqlite3
from pathlib import Path

BASE = "https://pokebase.app/pokemon-champions"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; PokeScraper/1.0)"}
DELAY = 0.35
DB_PATH = "pokebase_champions.db"


# -- helpers ------------------------------------------------------------------

def fetch(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.text


def rsc(html: str) -> str:
    parts = []
    for chunk in re.findall(r'self\.__next_f\.push\(\[1,(.*?)\]\s*\)', html, re.DOTALL):
        try:
            parts.append(json.loads(chunk))
        except Exception:
            pass
    return "".join(parts)


def clean(s):
    """Fix Mojibake (Windows-1252 bytes decoded as Latin-1)."""
    if not isinstance(s, str):
        return s
    try:
        return s.encode("latin-1").decode("utf-8")
    except Exception:
        return s


# -- ID → slug map (built once from the moves list page) ----------------------

def build_id_slug_map(payload: str) -> dict:
    """
    Every Pokemon in the RSC payload has nationalNumber + slug as early fields,
    and its own MongoDB id as the LAST \"id\" field before the next nationalNumber.
    """
    id_slug = {}
    for m in re.finditer(
        r'"nationalNumber"\s*:\s*\d+\s*,\s*"slug"\s*:\s*"([a-z0-9\-]+)"',
        payload,
    ):
        slug = m.group(1)
        following = payload[m.end(): m.end() + 5000]
        next_nat = re.search(r'"nationalNumber"', following)
        scope = following[: next_nat.start()] if next_nat else following
        ids = re.findall(r'"id"\s*:\s*"([a-f0-9]{24})"', scope)
        if ids:
            id_slug[ids[-1]] = slug
    return id_slug


# -- move list scrape ----------------------------------------------------------

def scrape_move_list() -> tuple[list, dict]:
    """
    Returns (moves_list, id_slug_map).
    All 937 moves are in a single page (limit=5000 in the API).
    """
    print("Fetching move list …")
    payload = rsc(fetch(f"{BASE}/moves"))

    # Build ID→slug map from the pokemon list page — covers all 268+ pokemon in one request.
    print("  Building ID->slug map from pokemon list page ...")
    pokemon_payload = rsc(fetch(f"{BASE}/pokemon"))
    id_slug = build_id_slug_map(pokemon_payload)
    print(f"  ID->slug map: {len(id_slug)} entries")

    # Find the moves docs array — take the largest totalDocs (navigation has only 3 sites)
    all_totals = list(re.finditer(r'"totalDocs"\s*:\s*(\d+)', payload))
    if not all_totals:
        print("ERROR: Could not find totalDocs in moves payload")
        return [], id_slug
    total_match = max(all_totals, key=lambda m: int(m.group(1)))
    print(f"  totalDocs = {total_match.group(1)}")
    idx = total_match.start()
    doc_start = payload.rfind('"docs":[', 0, idx) + len('"docs":')
    array_end = idx  # safe upper bound
    # walk to find the closing ] of docs
    depth, i = 0, doc_start
    for i in range(doc_start, min(doc_start + 2_000_000, len(payload))):
        if payload[i] == '[':
            depth += 1
        elif payload[i] == ']':
            depth -= 1
            if depth == 0:
                break
    try:
        docs = json.loads(payload[doc_start: i + 1])
    except Exception:
        docs = []

    moves = []
    for d in docs:
        t = d.get("type", {})
        moves.append({
            "slug": d.get("slug"),
            "name": clean(d.get("name", "")),
            "type": t.get("name") if isinstance(t, dict) else None,
            "damage_class": d.get("damageClass"),
            "power": d.get("power"),
            "accuracy": d.get("accuracy"),
            "pp": d.get("pp"),
            "description": clean(d.get("description", "")),
        })

    print(f"  Parsed {len(moves)} moves from list page")
    return moves, id_slug


# -- individual move page scrape -----------------------------------------------

def scrape_move_page(slug: str, id_slug: dict) -> dict:
    """Returns {pokemon_slug: usage_percent} for a single move. Mutates id_slug in-place."""
    payload = rsc(fetch(f"{BASE}/moves/{slug}"))
    id_slug.update(build_id_slug_map(payload))
    usage = {}
    for idx in [m.start() for m in re.finditer(r'"usagePercentByPokemonId"', payload)]:
        obj_start = payload.find("{", idx)
        if obj_start == -1:
            continue
        depth, end = 0, obj_start
        for end in range(obj_start, min(obj_start + 500_000, len(payload))):
            if payload[end] == "{":
                depth += 1
            elif payload[end] == "}":
                depth -= 1
                if depth == 0:
                    break
        try:
            obj = json.loads(payload[obj_start: end + 1])
        except Exception:
            continue
        for pid, pct in obj.items():
            poke_slug = id_slug.get(pid)
            if poke_slug and isinstance(pct, (int, float)):
                usage[poke_slug] = pct
    return usage


# -- database setup ------------------------------------------------------------

def init_db(conn: sqlite3.Connection):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS pokemon (
        slug        TEXT PRIMARY KEY,
        name        TEXT,
        types       TEXT,   -- JSON array
        hp          INTEGER, attack      INTEGER, defense     INTEGER,
        sp_attack   INTEGER, sp_defense  INTEGER, speed       INTEGER,
        image_url   TEXT
    );

    CREATE TABLE IF NOT EXISTS type_chart (
        pokemon_slug    TEXT REFERENCES pokemon(slug),
        attacking_type  TEXT,
        multiplier      TEXT,
        PRIMARY KEY (pokemon_slug, attacking_type)
    );

    CREATE TABLE IF NOT EXISTS moves (
        slug         TEXT PRIMARY KEY,
        name         TEXT,
        type         TEXT,
        damage_class TEXT,
        power        INTEGER,
        accuracy     INTEGER,
        pp           INTEGER,
        description  TEXT,
        overall_usage_pct REAL  -- filled after scraping move pages
    );

    CREATE TABLE IF NOT EXISTS pokemon_move (
        pokemon_slug TEXT REFERENCES pokemon(slug),
        move_slug    TEXT REFERENCES moves(slug),
        PRIMARY KEY (pokemon_slug, move_slug)
    );

    CREATE TABLE IF NOT EXISTS tournament_usage (
        pokemon_slug  TEXT REFERENCES pokemon(slug),
        category      TEXT CHECK(category IN ('ability','item','move')),
        name          TEXT,
        usage_pct     REAL,
        PRIMARY KEY (pokemon_slug, category, name)
    );

    CREATE TABLE IF NOT EXISTS move_usage (
        move_slug     TEXT REFERENCES moves(slug),
        pokemon_slug  TEXT REFERENCES pokemon(slug),
        usage_pct     REAL,
        PRIMARY KEY (move_slug, pokemon_slug)
    );

    CREATE TABLE IF NOT EXISTS tournaments (
        id          TEXT PRIMARY KEY,
        name        TEXT,
        date        TEXT,
        num_players INTEGER,
        limitless_id TEXT
    );

    CREATE TABLE IF NOT EXISTS teams (
        id              TEXT PRIMARY KEY,
        tournament_id   TEXT REFERENCES tournaments(id),
        player          TEXT,
        placing         INTEGER,
        wins            INTEGER,
        losses          INTEGER,
        ties            INTEGER
    );

    CREATE TABLE IF NOT EXISTS team_pokemon (
        team_id      TEXT REFERENCES teams(id),
        position     INTEGER,
        pokemon_slug TEXT,
        ability      TEXT,
        item         TEXT,
        nature       TEXT,
        PRIMARY KEY (team_id, position)
    );

    CREATE TABLE IF NOT EXISTS team_move (
        team_id      TEXT REFERENCES teams(id),
        position     INTEGER,
        move_slug    TEXT,
        PRIMARY KEY (team_id, position, move_slug)
    );
    """)
    conn.commit()


# -- load existing JSON data into DB ------------------------------------------

def load_pokemon(conn: sqlite3.Connection):
    path = Path("pokemon_champions.json")
    if not path.exists():
        print("  pokemon_champions.json not found, skipping")
        return
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    for slug, p in data.items():
        s = p.get("base_stats", {})
        conn.execute("""
            INSERT OR REPLACE INTO pokemon
            (slug, name, types, hp, attack, defense, sp_attack, sp_defense, speed, image_url)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (
            slug, p.get("name"),
            json.dumps(p.get("types", [])),
            s.get("hp"), s.get("attack"), s.get("defense"),
            s.get("specialAttack"), s.get("specialDefense"), s.get("speed"),
            p.get("image_url"),
        ))

        # type chart
        for atype, mult in p.get("type_effectiveness", {}).items():
            conn.execute("""
                INSERT OR REPLACE INTO type_chart (pokemon_slug, attacking_type, multiplier)
                VALUES (?,?,?)
            """, (slug, atype, mult))

        # tournament usage (abilities, items, moves)
        usage = p.get("tournament_usage", {})
        cat_map = {"abilities": "ability", "items": "item", "moves": "move"}
        for category in ("abilities", "items", "moves"):
            for entry in usage.get(category, []):
                conn.execute("""
                    INSERT OR REPLACE INTO tournament_usage
                    (pokemon_slug, category, name, usage_pct)
                    VALUES (?,?,?,?)
                """, (slug, cat_map[category], entry["name"], entry["percent"]))

        # learnable movelist
        for mv in p.get("movelist", []):
            move_slug = mv.get("slug")
            if not move_slug:
                continue
            conn.execute("""
                INSERT OR IGNORE INTO pokemon_move (pokemon_slug, move_slug) VALUES (?,?)
            """, (slug, move_slug))

    conn.commit()
    print(f"  Loaded {len(data)} Pokemon")


def load_tournaments(conn: sqlite3.Connection):
    path = Path("tournament_teams.json")
    if not path.exists():
        print("  tournament_teams.json not found, skipping")
        return
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    for t in data:
        conn.execute("""
            INSERT OR REPLACE INTO tournaments (id, name, date, num_players, limitless_id)
            VALUES (?,?,?,?,?)
        """, (t["id"], t["name"], t["date"], t["numberOfPlayers"], t.get("limitlessId")))

        for team in t.get("teams", []):
            team_id = team["id"]
            conn.execute("""
                INSERT OR REPLACE INTO teams
                (id, tournament_id, player, placing, wins, losses, ties)
                VALUES (?,?,?,?,?,?,?)
            """, (
                team_id, t["id"],
                team.get("limitlessPlayer"), team.get("placing"),
                team.get("wins"), team.get("losses"), team.get("ties"),
            ))

            for pos, poke in enumerate(team.get("pokemon", [])):
                poke_slug = poke.get("slug")
                conn.execute("""
                    INSERT OR REPLACE INTO team_pokemon
                    (team_id, position, pokemon_slug, ability, item, nature)
                    VALUES (?,?,?,?,?,?)
                """, (team_id, pos, poke_slug,
                      poke.get("ability"), poke.get("item"), poke.get("nature")))

                for mv in poke.get("moves", []):
                    move_slug = mv.get("slug")
                    if move_slug:
                        conn.execute("""
                            INSERT OR IGNORE INTO team_move (team_id, position, move_slug)
                            VALUES (?,?,?)
                        """, (team_id, pos, move_slug))

    conn.commit()
    print(f"  Loaded {len(data)} tournaments")


# -- main ----------------------------------------------------------------------

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    init_db(conn)

    print("\n-- Loading existing scraped data --")
    load_pokemon(conn)
    load_tournaments(conn)

    print("\n-- Scraping moves --")
    moves, id_slug = scrape_move_list()

    # Insert move stubs (no usage yet)
    for mv in moves:
        conn.execute("""
            INSERT OR IGNORE INTO moves
            (slug, name, type, damage_class, power, accuracy, pp, description)
            VALUES (?,?,?,?,?,?,?,?)
        """, (mv["slug"], mv["name"], mv["type"], mv["damage_class"],
              mv["power"], mv["accuracy"], mv["pp"], mv["description"]))
    conn.commit()

    # Scrape individual move pages for per-Pokemon usage
    print(f"\n-- Scraping {len(moves)} move pages for per-Pokemon usage --")
    errors = []
    for i, mv in enumerate(moves, 1):
        slug = mv["slug"]
        print(f"[{i:3d}/{len(moves)}] {slug}", end=" ... ", flush=True)
        try:
            usage = scrape_move_page(slug, id_slug)
            total_pct = 0.0
            for poke_slug, pct in usage.items():
                conn.execute("""
                    INSERT OR REPLACE INTO move_usage (move_slug, pokemon_slug, usage_pct)
                    VALUES (?,?,?)
                """, (slug, poke_slug, pct))
                total_pct += pct
            # overall_usage_pct = average across all pokemon using it
            overall = round(total_pct / len(usage), 2) if usage else 0.0
            conn.execute(
                "UPDATE moves SET overall_usage_pct=? WHERE slug=?", (overall, slug)
            )
            conn.commit()
            print(f"OK ({len(usage)} users)")
        except Exception as e:
            print(f"ERROR: {e}")
            errors.append({"slug": slug, "error": str(e)})
        time.sleep(DELAY)

    if errors:
        with open("move_scrape_errors.json", "w") as f:
            json.dump(errors, f, indent=2)
        print(f"\n{len(errors)} errors saved to move_scrape_errors.json")

    # -- summary queries --
    print("\n-- Database summary --")
    for table in ["pokemon", "moves", "pokemon_move", "tournament_usage",
                  "move_usage", "tournaments", "teams", "team_pokemon", "team_move"]:
        n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:<22} {n:>6} rows")

    print("\n-- Top 10 most-used moves in tournaments --")
    rows = conn.execute("""
        SELECT m.name, m.type, m.damage_class, m.power,
               COUNT(DISTINCT mu.pokemon_slug) as num_users,
               ROUND(AVG(mu.usage_pct),1) as avg_usage
        FROM moves m
        JOIN move_usage mu ON m.slug = mu.move_slug
        WHERE mu.usage_pct > 0
        GROUP BY m.slug
        ORDER BY avg_usage DESC
        LIMIT 10
    """).fetchall()
    for r in rows:
        print(f"  {r[0]:<22} [{r[1]:<8}] {r[2]:<10} pwr={str(r[3]):<5} users={r[4]} avg={r[5]}%")

    print("\n-- Sneasler full tournament profile --")
    rows = conn.execute("""
        SELECT category, name, usage_pct FROM tournament_usage
        WHERE pokemon_slug='sneasler' ORDER BY category, usage_pct DESC
    """).fetchall()
    for r in rows:
        print(f"  [{r[0]:<7}] {r[1]:<25} {r[2]}%")

    conn.close()
    print(f"\nDatabase saved to {DB_PATH}")


if __name__ == "__main__":
    main()
