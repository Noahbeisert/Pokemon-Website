"""
Fetches all public VGC tournament data from the Limitless TCG API
and stores it in the local SQLite database.

Usage:
    python scrape_limitless.py               # All VGC formats, skip already-scraped
    python scrape_limitless.py --format M-A  # Current regulation only
    python scrape_limitless.py --dry-run     # Count only, no DB writes
    python scrape_limitless.py --refetch     # Re-fetch even if already in DB
"""
import argparse
import re
import sqlite3
import sys
import time

import requests

# Windows cp1252 consoles can't print é, ñ, etc. — replace rather than crash.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

API_BASE        = "https://play.limitlesstcg.com/api"
DB_PATH         = "pokebase_champions.db"
GAME            = "VGC"
PAGE_SIZE       = 100
DELAY           = 2.0   # seconds between every API call
RETRY_WAIT_BASE = 30    # seconds to wait after first 429
MAX_RETRY       = 6     # retries on 429 (30→60→120→120→120→120 s)


# ── Helpers ───────────────────────────────────────────────────────────────────

_SINGLES_PATTERN = re.compile(r"\bsingles\b", re.IGNORECASE)

def is_doubles(name: str) -> bool:
    """Reject any tournament whose name explicitly says 'singles'."""
    return not _SINGLES_PATTERN.search(name)


def slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"[''']", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


# ── Schema migration ──────────────────────────────────────────────────────────

def migrate_schema(conn: sqlite3.Connection) -> None:
    additions = [
        ("teams",        "player_name TEXT"),
        ("teams",        "country TEXT"),
        ("teams",        "drop_round INTEGER"),
        ("team_pokemon", "tera_type TEXT"),
    ]
    for table, col_def in additions:
        col_name = col_def.split()[0]
        try:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {col_def}")
            print(f"  Schema: added {table}.{col_name}")
        except sqlite3.OperationalError:
            pass  # already exists
    conn.commit()


# ── API calls ─────────────────────────────────────────────────────────────────

def api_get(path: str, params: dict | None = None) -> dict | list:
    """GET with exponential backoff on 429. Raises HTTPError only after MAX_RETRY exhausted."""
    url = f"{API_BASE}{path}"
    wait = RETRY_WAIT_BASE
    for attempt in range(MAX_RETRY):
        r = requests.get(url, params=params, timeout=15)
        if r.status_code == 429:
            actual_wait = float(r.headers.get("Retry-After", wait))
            actual_wait = max(actual_wait, wait)  # never wait less than our backoff
            print(f"\n  429 rate-limited — waiting {actual_wait:.0f}s (attempt {attempt+1}/{MAX_RETRY})...",
                  end="", flush=True)
            time.sleep(actual_wait)
            wait = min(wait * 2, 120)
            continue
        r.raise_for_status()
        return r.json()
    raise requests.HTTPError(f"429 after {MAX_RETRY} retries: {url}")


def fetch_tournament_page(fmt: str | None, page: int) -> list[dict]:
    params = {"game": GAME, "limit": PAGE_SIZE, "page": page}
    if fmt:
        params["format"] = fmt
    return api_get("/tournaments", params)


def fetch_details(tid: str) -> dict:
    return api_get(f"/tournaments/{tid}/details")


def fetch_standings(tid: str) -> list[dict]:
    return api_get(f"/tournaments/{tid}/standings")


# ── DB writes ─────────────────────────────────────────────────────────────────

def already_scraped(conn: sqlite3.Connection, tid: str) -> bool:
    return conn.execute("SELECT 1 FROM tournaments WHERE id=?", (tid,)).fetchone() is not None


def save_tournament(conn: sqlite3.Connection, details: dict, num_players: int) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO tournaments (id, name, date, num_players, limitless_id) VALUES (?,?,?,?,?)",
        (details["id"], details["name"], details["date"], num_players, details["id"]),
    )


def save_standings(conn: sqlite3.Connection, tid: str, standings: list[dict]) -> None:
    for s in standings:
        username = s.get("player") or ""
        team_id  = f"{tid}_{username}"
        rec      = s.get("record") or {}

        conn.execute(
            """INSERT OR REPLACE INTO teams
               (id, tournament_id, player, player_name, country, placing, wins, losses, ties, drop_round)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (team_id, tid, username, s.get("name"), s.get("country"),
             s.get("placing"), rec.get("wins", 0), rec.get("losses", 0),
             rec.get("ties", 0), s.get("drop")),
        )

        for pos, poke in enumerate(s.get("decklist") or []):
            # Limitless 'id' is already a proper slug (e.g. 'arcanine-hisui')
            pslug = poke.get("id") or slugify(poke.get("name", ""))
            conn.execute(
                """INSERT OR REPLACE INTO team_pokemon
                   (team_id, position, pokemon_slug, ability, item, tera_type)
                   VALUES (?,?,?,?,?,?)""",
                (team_id, pos, pslug, poke.get("ability"), poke.get("item"), poke.get("tera")),
            )
            for move_name in poke.get("attacks") or []:
                conn.execute(
                    "INSERT OR REPLACE INTO team_move (team_id, position, move_slug) VALUES (?,?,?)",
                    (team_id, pos, slugify(move_name)),
                )


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape VGC data from Limitless TCG API")
    parser.add_argument("--format",   help="Regulation filter (e.g. M-A, SVG, SVF). Omit for all.")
    parser.add_argument("--dry-run",  action="store_true", help="List tournaments only, no DB writes")
    parser.add_argument("--refetch",  action="store_true", help="Re-import even if already in DB")
    args = parser.parse_args()

    conn = None if args.dry_run else sqlite3.connect(DB_PATH)
    if conn:
        migrate_schema(conn)

    fmt_label = f" format={args.format}" if args.format else " all formats"
    print(f"Fetching VGC tournaments ({fmt_label.strip()}) from Limitless...\n")

    page = 1
    n_found = n_imported = n_skipped = n_no_lists = 0

    while True:
        if page > 1:
            time.sleep(DELAY)
        try:
            batch = fetch_tournament_page(args.format, page)
        except requests.HTTPError as e:
            print(f"\nFailed to fetch page {page}: {e}\nStopping here — re-run to resume.")
            break
        if not batch:
            break

        for t in batch:
            tid     = t["id"]
            name    = t["name"]
            date    = t["date"][:10]
            players = t["players"]
            n_found += 1

            print(f"[{date}] {name} ({players}p)", end="")

            if not is_doubles(name):
                print(" — skipped (singles)")
                continue

            if args.dry_run:
                print()
                continue

            if not args.refetch and already_scraped(conn, tid):
                print(" — skip (already in DB)")
                n_skipped += 1
                continue

            time.sleep(DELAY)
            try:
                details = fetch_details(tid)
            except requests.HTTPError as e:
                print(f" — details failed ({e}), skipping")
                continue

            if not details.get("decklists"):
                print(" — no public decklists")
                n_no_lists += 1
                continue

            time.sleep(DELAY)
            try:
                standings = fetch_standings(tid)
            except requests.HTTPError as e:
                print(f" — standings failed ({e}), skipping")
                continue

            with conn:
                save_tournament(conn, details, players)
                save_standings(conn, tid, standings)

            n_imported += 1
            print(f" — {len(standings)} teams saved")

        page += 1

    if conn:
        conn.close()

    print(f"\nDone.  Found: {n_found}  |  Imported: {n_imported}  |  Skipped (in DB): {n_skipped}  |  No decklists: {n_no_lists}")


if __name__ == "__main__":
    main()
