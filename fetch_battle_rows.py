"""
The bulk /api index now ships a slimmed-down battle summary (name lists under
"values", no percentages) instead of the old per-rank "rows". Full rows with
percentages are still available per-Pokemon at /api/battle/{format}/{name}.
This hydrates index_dump.json's Current/Doubles.rows from that endpoint so
build_pokemon_json.py (unchanged) can keep working the way it always has.
"""
import json
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://championsbattledata.com"
FORMAT = "Doubles"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "application/json",
}
DELAY = 0.15


def get(path):
    req = urllib.request.Request(BASE + path, headers=HEADERS)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())


def fetch_rows(name):
    encoded = urllib.parse.quote(name)
    data = get(f"/api/battle/{FORMAT}/{encoded}")
    return data.get("rows", [])


def main():
    with open("index_dump.json", encoding="utf-8") as f:
        data = json.load(f)

    pokemon = data["pokemon"]
    hydrated, skipped, errors = 0, 0, []

    for i, p in enumerate(pokemon, 1):
        doubles = p.get("summary", {}).get("battleSummary", {}).get("Current", {}).get("Doubles")
        if not doubles or not doubles.get("top"):
            skipped += 1
            continue

        name = p["name"]
        try:
            rows = fetch_rows(name)
            doubles["rows"] = rows
            hydrated += 1
            print(f"[{i}/{len(pokemon)}] {name}: {len(rows)} rows")
        except urllib.error.HTTPError as e:
            errors.append({"name": name, "error": str(e)})
            print(f"[{i}/{len(pokemon)}] {name}: ERROR {e}")
        time.sleep(DELAY)

    with open("index_dump.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nHydrated {hydrated}, skipped {skipped} (no Doubles usage), errors {len(errors)}")
    if errors:
        with open("battle_row_errors.json", "w", encoding="utf-8") as f:
            json.dump(errors, f, indent=2)


if __name__ == "__main__":
    main()
