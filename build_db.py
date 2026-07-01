"""
Builds the clean application database pokemon_app.db from all scraped sources.

Sources:
  SCRAPER_DIR/pokemon_champions.json  — 268 pokemon: base stats, abilities (with descriptions),
                                         type effectiveness, full movelist
  SCRAPER_DIR/pokebase_champions.db   — moves (937), items (117), tournament/team data,
                                         pokemon_move links, move_usage, item_usage
  pokemon_db.json                     — 52 curated champions: roles, tiers, niche_threat, game8 IDs

Output: pokemon_app.db (this directory)
"""
import json
import math
import re
import sqlite3
from pathlib import Path

SCRAPER_DIR = Path("C:/Users/Admin/PhpStormProjects/untitled/scraper")
POKEMON_JSON = SCRAPER_DIR / "pokemon_champions.json"
SCRAPER_DB   = SCRAPER_DIR / "pokebase_champions.db"
CURATED_JSON = Path("pokemon_db.json")
APP_DB       = Path("pokemon_app.db")

FRAC_TO_FLOAT = {"0": 0.0, "1/4": 0.25, "1/2": 0.5, "1": 1.0, "2": 2.0, "4": 4.0}

NATURES = [
    ("Hardy",    None,       None),
    ("Lonely",   "attack",   "defense"),
    ("Brave",    "attack",   "speed"),
    ("Adamant",  "attack",   "sp_atk"),
    ("Naughty",  "attack",   "sp_def"),
    ("Bold",     "defense",  "attack"),
    ("Docile",   None,       None),
    ("Relaxed",  "defense",  "speed"),
    ("Impish",   "defense",  "sp_atk"),
    ("Lax",      "defense",  "sp_def"),
    ("Timid",    "speed",    "attack"),
    ("Hasty",    "speed",    "defense"),
    ("Serious",  None,       None),
    ("Jolly",    "speed",    "sp_atk"),
    ("Naive",    "speed",    "sp_def"),
    ("Modest",   "sp_atk",   "attack"),
    ("Mild",     "sp_atk",   "defense"),
    ("Quiet",    "sp_atk",   "speed"),
    ("Bashful",  None,       None),
    ("Rash",     "sp_atk",   "sp_def"),
    ("Calm",     "sp_def",   "attack"),
    ("Gentle",   "sp_def",   "defense"),
    ("Sassy",    "sp_def",   "speed"),
    ("Careful",  "sp_def",   "sp_atk"),
    ("Quirky",   None,       None),
]


def slug_from_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def frac(s) -> float:
    if s is None:
        return 1.0
    return FRAC_TO_FLOAT.get(str(s), float(s))


def create_schema(conn: sqlite3.Connection):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS nature (
        name      TEXT PRIMARY KEY,
        plus_stat TEXT,   -- NULL for neutral natures
        minus_stat TEXT
    );

    CREATE TABLE IF NOT EXISTS pokemon (
        slug        TEXT PRIMARY KEY,
        name        TEXT NOT NULL,
        dex_no      INTEGER,
        type1       TEXT,
        type2       TEXT,
        hp          INTEGER,
        attack      INTEGER,
        defense     INTEGER,
        sp_atk      INTEGER,
        sp_def      INTEGER,
        speed       INTEGER,
        image_url   TEXT,
        tier_singles TEXT,
        tier_doubles TEXT,
        game8_id    INTEGER,
        game8_url   TEXT
    );

    CREATE TABLE IF NOT EXISTS champion (
        pokemon_slug  TEXT PRIMARY KEY REFERENCES pokemon(slug),
        roles         TEXT,   -- JSON array
        niche_threat  TEXT    -- JSON object {move, type, note}
    );

    CREATE TABLE IF NOT EXISTS ability (
        slug        TEXT PRIMARY KEY,
        name        TEXT NOT NULL,
        description TEXT
    );

    CREATE TABLE IF NOT EXISTS pokemon_ability (
        pokemon_slug  TEXT REFERENCES pokemon(slug),
        ability_slug  TEXT REFERENCES ability(slug),
        PRIMARY KEY (pokemon_slug, ability_slug)
    );

    CREATE TABLE IF NOT EXISTS move (
        slug         TEXT PRIMARY KEY,
        name         TEXT,
        type         TEXT,
        damage_class TEXT,
        power        INTEGER,
        accuracy     INTEGER,
        pp           INTEGER,
        description  TEXT
    );

    CREATE TABLE IF NOT EXISTS pokemon_move (
        pokemon_slug TEXT REFERENCES pokemon(slug),
        move_slug    TEXT REFERENCES move(slug),
        PRIMARY KEY (pokemon_slug, move_slug)
    );

    CREATE TABLE IF NOT EXISTS item (
        slug              TEXT PRIMARY KEY,
        name              TEXT,
        category          TEXT,
        description       TEXT,
        is_megastone      INTEGER DEFAULT 0,
        mega_pokemon_slug TEXT,
        overall_usage_pct REAL,
        unlock            TEXT
    );

    CREATE TABLE IF NOT EXISTS type_chart (
        pokemon_slug    TEXT REFERENCES pokemon(slug),
        attacking_type  TEXT,
        multiplier      REAL,
        PRIMARY KEY (pokemon_slug, attacking_type)
    );

    CREATE TABLE IF NOT EXISTS tournament_usage (
        pokemon_slug TEXT REFERENCES pokemon(slug),
        category     TEXT CHECK(category IN ('ability','item','move')),
        name         TEXT,
        usage_pct    REAL,
        PRIMARY KEY (pokemon_slug, category, name)
    );

    CREATE TABLE IF NOT EXISTS move_usage (
        move_slug    TEXT REFERENCES move(slug),
        pokemon_slug TEXT REFERENCES pokemon(slug),
        usage_pct    REAL,
        PRIMARY KEY (move_slug, pokemon_slug)
    );

    CREATE TABLE IF NOT EXISTS item_usage (
        item_slug    TEXT REFERENCES item(slug),
        pokemon_slug TEXT REFERENCES pokemon(slug),
        usage_pct    REAL,
        PRIMARY KEY (item_slug, pokemon_slug)
    );

    CREATE TABLE IF NOT EXISTS tournament (
        id           TEXT PRIMARY KEY,
        name         TEXT,
        date         TEXT,
        num_players  INTEGER,
        limitless_id TEXT
    );

    CREATE TABLE IF NOT EXISTS team (
        id            TEXT PRIMARY KEY,
        tournament_id TEXT REFERENCES tournament(id),
        player        TEXT,
        placing       INTEGER,
        wins          INTEGER,
        losses        INTEGER,
        ties          INTEGER
    );

    CREATE TABLE IF NOT EXISTS team_pokemon (
        team_id      TEXT REFERENCES team(id),
        position     INTEGER,
        pokemon_slug TEXT,
        ability      TEXT,
        item         TEXT,
        nature       TEXT,
        PRIMARY KEY (team_id, position)
    );

    CREATE TABLE IF NOT EXISTS team_move (
        team_id      TEXT REFERENCES team(id),
        position     INTEGER,
        move_slug    TEXT,
        PRIMARY KEY (team_id, position, move_slug)
    );
    """)
    conn.commit()


def load_natures(conn: sqlite3.Connection):
    conn.executemany(
        "INSERT OR REPLACE INTO nature (name, plus_stat, minus_stat) VALUES (?,?,?)",
        NATURES,
    )
    conn.commit()
    print(f"  natures: {len(NATURES)} rows")


def load_pokemon_and_abilities(conn: sqlite3.Connection):
    if not POKEMON_JSON.exists():
        print(f"  MISSING: {POKEMON_JSON}")
        return

    with open(POKEMON_JSON, encoding="utf-8") as f:
        data = json.load(f)

    abilities: dict[str, dict] = {}  # slug → {name, description}
    pokemon_count = 0

    for slug, p in data.items():
        types = p.get("types", [])
        s = p.get("base_stats", {})
        conn.execute("""
            INSERT OR REPLACE INTO pokemon
            (slug, name, dex_no, type1, type2, hp, attack, defense, sp_atk, sp_def, speed, image_url)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            slug, p.get("name"), p.get("pokedex_number"),
            types[0] if len(types) > 0 else None,
            types[1] if len(types) > 1 else None,
            s.get("hp"), s.get("attack"), s.get("defense"),
            s.get("specialAttack"), s.get("specialDefense"), s.get("speed"),
            p.get("image_url"),
        ))
        pokemon_count += 1

        # type effectiveness (string fractions → float)
        for atype, mult_str in p.get("type_effectiveness", {}).items():
            conn.execute("""
                INSERT OR REPLACE INTO type_chart (pokemon_slug, attacking_type, multiplier)
                VALUES (?,?,?)
            """, (slug, atype, frac(mult_str)))

        # abilities
        for ab in p.get("abilities", []):
            ab_name = ab.get("name", "").strip()
            if not ab_name:
                continue
            ab_slug = slug_from_name(ab_name)
            if ab_slug not in abilities:
                abilities[ab_slug] = {"name": ab_name, "description": ab.get("description", "")}
            conn.execute("""
                INSERT OR IGNORE INTO pokemon_ability (pokemon_slug, ability_slug) VALUES (?,?)
            """, (slug, ab_slug))

    for ab_slug, ab in abilities.items():
        conn.execute("""
            INSERT OR REPLACE INTO ability (slug, name, description) VALUES (?,?,?)
        """, (ab_slug, ab["name"], ab["description"]))

    conn.commit()
    print(f"  pokemon: {pokemon_count} rows")
    print(f"  abilities: {len(abilities)} rows")
    print(f"  type_chart: (populated from pokemon_champions.json)")


def load_curated(conn: sqlite3.Connection):
    if not CURATED_JSON.exists():
        print(f"  MISSING: {CURATED_JSON}")
        return

    with open(CURATED_JSON, encoding="utf-8") as f:
        data = json.load(f)

    count = 0
    for slug, p in data.items():
        conn.execute("""
            UPDATE pokemon SET tier_singles=?, tier_doubles=?, game8_id=?, game8_url=?
            WHERE slug=?
        """, (p.get("tier_singles"), p.get("tier_doubles"),
              p.get("game8_id"), p.get("game8_url"), slug))

        roles = p.get("roles", [])
        niche = p.get("niche_threat")
        conn.execute("""
            INSERT OR REPLACE INTO champion (pokemon_slug, roles, niche_threat)
            VALUES (?,?,?)
        """, (slug, json.dumps(roles), json.dumps(niche) if niche else None))
        count += 1

    conn.commit()
    print(f"  champion (curated): {count} rows")


def copy_from_scraper(conn: sqlite3.Connection):
    if not SCRAPER_DB.exists():
        print(f"  MISSING: {SCRAPER_DB}")
        return

    src = sqlite3.connect(str(SCRAPER_DB))

    # moves
    rows = src.execute("SELECT slug, name, type, damage_class, power, accuracy, pp, description FROM moves").fetchall()
    conn.executemany("""
        INSERT OR REPLACE INTO move (slug, name, type, damage_class, power, accuracy, pp, description)
        VALUES (?,?,?,?,?,?,?,?)
    """, rows)
    print(f"  moves: {len(rows)} rows")

    # pokemon_move
    rows = src.execute("SELECT pokemon_slug, move_slug FROM pokemon_move").fetchall()
    conn.executemany("INSERT OR IGNORE INTO pokemon_move (pokemon_slug, move_slug) VALUES (?,?)", rows)
    print(f"  pokemon_move: {len(rows)} rows")

    # items
    rows = src.execute(
        "SELECT slug, name, category, description, is_megastone, mega_pokemon_slug, overall_usage_pct, unlock FROM items"
    ).fetchall()
    conn.executemany("""
        INSERT OR REPLACE INTO item
        (slug, name, category, description, is_megastone, mega_pokemon_slug, overall_usage_pct, unlock)
        VALUES (?,?,?,?,?,?,?,?)
    """, rows)
    print(f"  items: {len(rows)} rows")

    # tournament_usage
    rows = src.execute("SELECT pokemon_slug, category, name, usage_pct FROM tournament_usage").fetchall()
    conn.executemany("""
        INSERT OR REPLACE INTO tournament_usage (pokemon_slug, category, name, usage_pct)
        VALUES (?,?,?,?)
    """, rows)
    print(f"  tournament_usage: {len(rows)} rows")

    # move_usage
    rows = src.execute("SELECT move_slug, pokemon_slug, usage_pct FROM move_usage").fetchall()
    conn.executemany("""
        INSERT OR REPLACE INTO move_usage (move_slug, pokemon_slug, usage_pct)
        VALUES (?,?,?)
    """, rows)
    print(f"  move_usage: {len(rows)} rows")

    # item_usage
    rows = src.execute("SELECT item_slug, pokemon_slug, usage_pct FROM item_usage").fetchall()
    conn.executemany("""
        INSERT OR REPLACE INTO item_usage (item_slug, pokemon_slug, usage_pct)
        VALUES (?,?,?)
    """, rows)
    print(f"  item_usage: {len(rows)} rows")

    # tournaments
    rows = src.execute("SELECT id, name, date, num_players, limitless_id FROM tournaments").fetchall()
    conn.executemany("""
        INSERT OR REPLACE INTO tournament (id, name, date, num_players, limitless_id)
        VALUES (?,?,?,?,?)
    """, rows)
    print(f"  tournaments: {len(rows)} rows")

    # teams
    rows = src.execute("SELECT id, tournament_id, player, placing, wins, losses, ties FROM teams").fetchall()
    conn.executemany("""
        INSERT OR REPLACE INTO team (id, tournament_id, player, placing, wins, losses, ties)
        VALUES (?,?,?,?,?,?,?)
    """, rows)
    print(f"  teams: {len(rows)} rows")

    # team_pokemon
    rows = src.execute("SELECT team_id, position, pokemon_slug, ability, item, nature FROM team_pokemon").fetchall()
    conn.executemany("""
        INSERT OR REPLACE INTO team_pokemon (team_id, position, pokemon_slug, ability, item, nature)
        VALUES (?,?,?,?,?,?)
    """, rows)
    print(f"  team_pokemon: {len(rows)} rows")

    # team_move
    rows = src.execute("SELECT team_id, position, move_slug FROM team_move").fetchall()
    conn.executemany("""
        INSERT OR REPLACE INTO team_move (team_id, position, move_slug)
        VALUES (?,?,?)
    """, rows)
    print(f"  team_move: {len(rows)} rows")

    conn.commit()
    src.close()


def sanity_check(conn: sqlite3.Connection):
    print("\n-- Sanity check --")
    tables = [
        "nature", "pokemon", "champion", "ability", "pokemon_ability",
        "move", "pokemon_move", "item", "type_chart",
        "tournament_usage", "move_usage", "item_usage",
        "tournament", "team", "team_pokemon", "team_move",
    ]
    for t in tables:
        n = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t:<22} {n:>7} rows")

    # spot check: Incineroar should exist with base stats
    row = conn.execute(
        "SELECT name, hp, attack, defense, sp_atk, sp_def, speed, type1, type2, tier_singles FROM pokemon WHERE slug='incineroar'"
    ).fetchone()
    if row:
        print(f"\n  Incineroar: HP={row[1]} Atk={row[2]} Def={row[3]} SpA={row[4]} SpD={row[5]} Spe={row[6]}")
        print(f"              types={row[7]}/{row[8]}  tier={row[9]}")
    else:
        print("\n  WARNING: Incineroar not found")

    # spot check: nature multipliers
    print("\n  Nature spot-checks:")
    for name, plus, minus in [("Adamant", "attack", "sp_atk"), ("Timid", "speed", "attack"), ("Hardy", None, None)]:
        row = conn.execute("SELECT plus_stat, minus_stat FROM nature WHERE name=?", (name,)).fetchone()
        print(f"    {name:<10} +{row[0]}  -{row[1]}")

    # spot check: type chart (fire attack vs Ferrothorn = 0.5)
    row = conn.execute(
        "SELECT multiplier FROM type_chart WHERE pokemon_slug='ferrothorn' AND attacking_type='Fire'"
    ).fetchone()
    if row:
        print(f"\n  Fire vs Ferrothorn: {row[0]}x  (expected 2.0 — Steel+Grass: Fire 2x each)")
    else:
        print("\n  WARNING: Ferrothorn type chart missing")

    # spot check: top 5 moves by tournament usage
    print("\n  Top 5 moves by avg tournament usage:")
    rows = conn.execute("""
        SELECT m.name, m.type, ROUND(AVG(mu.usage_pct),1) as avg
        FROM move m
        JOIN move_usage mu ON m.slug = mu.move_slug
        WHERE mu.usage_pct > 0
        GROUP BY m.slug
        ORDER BY avg DESC
        LIMIT 5
    """).fetchall()
    for r in rows:
        print(f"    {r[0]:<22} [{r[1]:<8}] {r[2]}%")


def main():
    if APP_DB.exists():
        APP_DB.unlink()
        print(f"Removed existing {APP_DB}")

    conn = sqlite3.connect(str(APP_DB))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    print("Creating schema...")
    create_schema(conn)

    print("\nLoading natures...")
    load_natures(conn)

    print("\nLoading pokemon + abilities from pokemon_champions.json...")
    load_pokemon_and_abilities(conn)

    print("\nLoading curated data from pokemon_db.json...")
    load_curated(conn)

    print("\nCopying from scraper DB...")
    copy_from_scraper(conn)

    sanity_check(conn)

    conn.close()
    print(f"\nDone — {APP_DB}")


if __name__ == "__main__":
    main()
