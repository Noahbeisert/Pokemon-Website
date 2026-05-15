"""
Scrapes all Pokemon Champions doubles replays from Pokemon Showdown.
Covers both regulations: regma (season 1) and regmb (season 2).

Saves to showdown_replays.json. Re-running resumes — already-fetched IDs are skipped.
Saves progress every 50 replays so kills don't lose data.
"""
import requests
import json
import time
import os

FORMATS = [
    "gen9championsvgc2026regma",
    "gen9championsvgc2026regmb",
]
SEARCH_URL = "https://replay.pokemonshowdown.com/search.json"
REPLAY_URL = "https://replay.pokemonshowdown.com/{id}.json"
OUT_FILE = "showdown_replays.json"
SAVE_EVERY = 50
DELAY = 0.5


def load_existing() -> tuple[list, set]:
    if not os.path.exists(OUT_FILE):
        return [], set()
    with open(OUT_FILE, encoding="utf-8") as f:
        replays = json.load(f)
    return replays, {r["id"] for r in replays}


def save(replays: list):
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(replays, f, indent=2, ensure_ascii=False)


def fetch_ids(fmt: str) -> list[str]:
    ids = []
    page = 1
    while True:
        resp = requests.get(SEARCH_URL, params={"format": fmt, "page": page}, timeout=10)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        ids.extend(b["id"] for b in batch)
        print(f"  [{fmt}] page {page}: {len(batch)} (total: {len(ids)})")
        if len(batch) < 51:
            break
        page += 1
        time.sleep(DELAY)
    return ids


def fetch_log(replay_id: str) -> dict | None:
    try:
        resp = requests.get(REPLAY_URL.format(id=replay_id), timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return {
            "id": data.get("id"),
            "format": data.get("format"),
            "players": data.get("players", []),
            "rating": data.get("rating"),
            "uploadtime": data.get("uploadtime"),
            "log": data.get("log", ""),
        }
    except Exception as e:
        print(f"  ERROR {replay_id}: {e}")
        return None


def main():
    replays, seen = load_existing()
    print(f"Resuming — {len(seen)} replays already saved.\n")

    all_ids = []
    for fmt in FORMATS:
        print(f"Fetching ID list for {fmt}...")
        all_ids.extend(fetch_ids(fmt))

    todo = [rid for rid in all_ids if rid not in seen]
    print(f"\n{len(all_ids)} total IDs, {len(todo)} new to fetch.\n")

    since_save = 0
    for i, rid in enumerate(todo, 1):
        print(f"[{i}/{len(todo)}] {rid}")
        data = fetch_log(rid)
        if data:
            replays.append(data)
            since_save += 1
        if since_save >= SAVE_EVERY:
            save(replays)
            print(f"  >> saved ({len(replays)} total)")
            since_save = 0
        time.sleep(DELAY)

    save(replays)
    print(f"\nDone. {len(replays)} replays in {OUT_FILE}")


if __name__ == "__main__":
    main()
