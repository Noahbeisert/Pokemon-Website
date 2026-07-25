"""
Fetches curated Champions team pastes from the public VGCPastes Google Sheet
(Team ID + Pokepaste link per row) and scrapes each pokepast.es page for the
full Showdown export — including EVs and nature, which Limitless's API
doesn't expose. Stores into the same teams/team_pokemon/team_move tables
scrape_limitless.py uses, tagged with source='vgcpastes' and prefixed IDs so
they never collide with Limitless-sourced rows.

Usage:
    python scrape_vgcpastes.py               # both tabs, skip already-scraped
    python scrape_vgcpastes.py --dry-run      # list teams only, no DB writes
    python scrape_vgcpastes.py --refetch      # re-import even if already in DB
    python scrape_vgcpastes.py --workers 5    # concurrent pokepaste fetches
"""
import argparse
import csv
import io
import re
import sqlite3
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from scrape_limitless import slugify

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SHEET_ID = "1axlwmzPA49rYkqXh7zHvAtSP-TKbM0ijGYBPRflLSWw"
TABS     = ["Champions M-B", "Champions M-A Featured Teams"]
DB_PATH  = "pokebase_champions.db"
DELAY    = 0.5


# ── Sheet parsing ────────────────────────────────────────────────────────────

def fetch_tab_rows(tab: str) -> list[list[str]]:
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={requests.utils.quote(tab)}"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return list(csv.reader(io.StringIO(r.text)))


def extract_teams(tab: str) -> list[dict]:
    rows = fetch_tab_rows(tab)
    header_idx = next((i for i, row in enumerate(rows) if "Team ID" in row), None)
    if header_idx is None:
        print(f"  [{tab}] no header row found, skipping")
        return []

    header = rows[header_idx]
    col = {name.strip(): i for i, name in enumerate(header) if name.strip()}
    if "Team ID" not in col or "Pokepaste" not in col:
        print(f"  [{tab}] missing Team ID/Pokepaste columns, skipping")
        return []

    def get(row, name):
        i = col.get(name)
        return row[i].strip() if i is not None and i < len(row) else ""

    out = []
    for row in rows[header_idx + 1:]:
        team_id = get(row, "Team ID")
        paste_url = get(row, "Pokepaste")
        if not team_id or not paste_url.startswith("https://pokepast.es/"):
            continue
        out.append({
            "team_id":     team_id,
            "paste_url":   paste_url.rstrip("/"),
            "description": get(row, "Team Description"),
            "owner":       get(row, "Owner"),
            "tournament":  get(row, "Tournament / Event"),
            "rank":        get(row, "Rank"),
            "tab":         tab,
        })
    return out


# ── Pokepaste parsing ────────────────────────────────────────────────────────

EV_KEYS = {"HP": "hp", "Atk": "atk", "Def": "def", "SpA": "spa", "SpD": "spd", "Spe": "spe"}


def parse_species(line: str) -> tuple[str, str | None]:
    """'Nickname (Species) (M) @ Item' -> (species, item)"""
    item = None
    if "@" in line:
        line, item = (s.strip() for s in line.rsplit("@", 1))
    line = re.sub(r"\s*\((M|F)\)\s*$", "", line).strip()
    # Nickname form ends in "(Species)" — locate it without regex backtracking risk.
    if line.endswith(")"):
        open_idx = line.rfind("(")
        if open_idx != -1:
            line = line[open_idx + 1: -1].strip()
    return line, item


def parse_evs(line: str) -> dict:
    evs = {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}
    for part in line.split(":", 1)[1].split("/"):
        part = part.strip()
        if not part:
            continue
        num, stat = part.split()
        evs[EV_KEYS[stat]] = int(num)
    return evs


def parse_pokepaste(text: str) -> list[dict]:
    mons = []
    text = text.replace("\r\n", "\n")
    for block in text.strip().split("\n\n")[:6]:
        lines = [l.strip() for l in block.strip().splitlines() if l.strip()]
        # A real mon block always has an Ability line — filters out stray HTML/error bodies.
        if not lines or not any(l.startswith("Ability:") for l in lines):
            continue
        species, item = parse_species(lines[0])
        mon = {
            "species": species, "item": item, "ability": None, "nature": None,
            "tera": None, "evs": {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
            "moves": [],
        }
        for line in lines[1:]:
            if line.startswith("Ability:"):
                mon["ability"] = line.split(":", 1)[1].strip()
            elif line.startswith("EVs:"):
                mon["evs"] = parse_evs(line)
            elif line.startswith("Tera Type:"):
                mon["tera"] = line.split(":", 1)[1].strip()
            elif line.endswith("Nature"):
                mon["nature"] = line.split()[0]
            elif line.startswith("-"):
                mon["moves"].append(line.lstrip("- ").strip())
        mons.append(mon)
    return mons


def fetch_and_parse_paste(team: dict) -> dict:
    time.sleep(DELAY)
    try:
        r = requests.get(f"{team['paste_url']}/raw", timeout=15)
        r.raise_for_status()
    except requests.RequestException as e:
        return {**team, "error": str(e)}
    if len(r.text) > 10_000:
        return {**team, "error": f"unexpected response size ({len(r.text)} bytes), not a paste"}
    mons = parse_pokepaste(r.text)
    if not mons:
        return {**team, "error": "empty/unparseable paste"}
    return {**team, "mons": mons}


# ── DB ────────────────────────────────────────────────────────────────────────

def migrate_schema(conn: sqlite3.Connection) -> None:
    additions = [
        ("teams",         "source TEXT"),
        ("teams",         "description TEXT"),
        ("teams",         "pokepaste_url TEXT"),
        ("teams",         "tournament_name TEXT"),
        ("team_pokemon",  "nature TEXT"),
        ("team_pokemon",  "ev_hp INTEGER"),
        ("team_pokemon",  "ev_atk INTEGER"),
        ("team_pokemon",  "ev_def INTEGER"),
        ("team_pokemon",  "ev_spa INTEGER"),
        ("team_pokemon",  "ev_spd INTEGER"),
        ("team_pokemon",  "ev_spe INTEGER"),
    ]
    for table, col_def in additions:
        try:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {col_def}")
            print(f"  Schema: added {table}.{col_def.split()[0]}")
        except sqlite3.OperationalError:
            pass
    conn.commit()


def already_scraped(conn: sqlite3.Connection, db_id: str) -> bool:
    return conn.execute("SELECT 1 FROM teams WHERE id=?", (db_id,)).fetchone() is not None


def save_team(conn: sqlite3.Connection, result: dict) -> None:
    db_id = f"vgcpastes_{result['team_id']}"
    conn.execute(
        """INSERT OR REPLACE INTO teams
           (id, tournament_id, player, player_name, placing, source, description, pokepaste_url, tournament_name)
           VALUES (?, NULL, ?, ?, ?, 'vgcpastes', ?, ?, ?)""",
        (db_id, result["team_id"], result["owner"], result["rank"] or None,
         result["description"], result["paste_url"], result["tournament"] or None),
    )
    for pos, mon in enumerate(result["mons"]):
        slug = slugify(mon["species"])
        conn.execute(
            """INSERT OR REPLACE INTO team_pokemon
               (team_id, position, pokemon_slug, ability, item, tera_type, nature,
                ev_hp, ev_atk, ev_def, ev_spa, ev_spd, ev_spe)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (db_id, pos, slug, mon["ability"], mon["item"], mon["tera"], mon["nature"],
             mon["evs"]["hp"], mon["evs"]["atk"], mon["evs"]["def"],
             mon["evs"]["spa"], mon["evs"]["spd"], mon["evs"]["spe"]),
        )
        for move_name in mon["moves"]:
            conn.execute(
                "INSERT OR REPLACE INTO team_move (team_id, position, move_slug) VALUES (?,?,?)",
                (db_id, pos, slugify(move_name)),
            )


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape curated Champions teams from VGCPastes")
    parser.add_argument("--dry-run", action="store_true", help="List teams only, no fetching/DB writes")
    parser.add_argument("--refetch", action="store_true", help="Re-import even if already in DB")
    parser.add_argument("--workers", type=int, default=5, help="Concurrent pokepaste fetches")
    args = parser.parse_args()

    print("Reading VGCPastes sheet tabs...\n")
    all_teams, seen_ids = [], set()
    for tab in TABS:
        teams = extract_teams(tab)
        print(f"  [{tab}] {len(teams)} teams with pokepaste links")
        for t in teams:
            if t["team_id"] not in seen_ids:
                seen_ids.add(t["team_id"])
                all_teams.append(t)

    print(f"\n{len(all_teams)} unique teams total.\n")

    if args.dry_run:
        for t in all_teams[:10]:
            print(f"  {t['team_id']} [{t['tab']}] -> {t['paste_url']}")
        print("  ...")
        return

    conn = sqlite3.connect(DB_PATH)
    migrate_schema(conn)

    to_fetch = all_teams if args.refetch else [
        t for t in all_teams if not already_scraped(conn, f"vgcpastes_{t['team_id']}")
    ]
    n_skipped = len(all_teams) - len(to_fetch)
    print(f"Fetching {len(to_fetch)} pokepastes ({n_skipped} already in DB), {args.workers} worker(s)...\n")

    n_saved = n_errors = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(fetch_and_parse_paste, t) for t in to_fetch]
        for future in as_completed(futures):
            r = future.result()
            if r.get("error"):
                print(f"  {r['team_id']} — {r['error']}")
                n_errors += 1
                continue
            with conn:
                save_team(conn, r)
            n_saved += 1
            print(f"  {r['team_id']} — {len(r['mons'])} pokemon saved")

    conn.close()
    print(f"\nDone.  Saved: {n_saved}  |  Skipped (in DB): {n_skipped}  |  Errors: {n_errors}")


if __name__ == "__main__":
    main()
