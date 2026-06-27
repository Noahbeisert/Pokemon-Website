import urllib.request
import json

BASE = "https://championsbattledata.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "application/json",
}


def get(path):
    req = urllib.request.Request(BASE + path, headers=HEADERS)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())


data = get("/api")

with open("index_dump.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Top-level keys: {list(data.keys())}")
print(f"Pokemon count: {len(data.get('pokemon', []))}")

# Print first pokemon entry in full to reveal all fields
if data.get("pokemon"):
    first = data["pokemon"][0]
    print(f"\nFirst pokemon full entry:\n{json.dumps(first, indent=2)}")
