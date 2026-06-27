import urllib.request
import urllib.parse
import json

BASE = "https://championsbattledata.com"
FORMAT = "Doubles"
SEASON = "Season M-3"


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "application/json",
}


def get(path):
    url = BASE + path
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())


def fetch_index():
    print("Fetching index...")
    data = get("/api")
    pokemon_list = data.get("pokemon", [])
    print(f"  Total pokemon in index: {len(pokemon_list)}")
    if pokemon_list:
        # print full first entry to reveal all fields (especially summary)
        first = {k: v for k, v in pokemon_list[0].items() if k != "learnableMoveNames"}
        print(f"  First entry (minus learnableMoveNames):\n{json.dumps(first, indent=2)}")
    return pokemon_list


def filter_doubles_top10(pokemon_list):
    doubles_pokemon = []
    for p in pokemon_list:
        csvs = p.get("battleDataCsvs", [])
        for csv in csvs:
            if csv.get("format") == FORMAT:
                doubles_pokemon.append(p)
                break

    print(f"\n  Pokemon with Doubles data: {len(doubles_pokemon)}")

    # Check if there's a usage/rank field
    if doubles_pokemon:
        sample = doubles_pokemon[0]
        print(f"  Sample pokemon keys: {list(sample.keys())}")

    return doubles_pokemon[:10]


def fetch_battle_rows(name):
    encoded = urllib.parse.quote(name)
    return get(f"/api/battle/{FORMAT}/{encoded}")


def summarize(battle_data):
    rows = battle_data.get("rows", [])
    result = {cat: [] for cat in ["move", "held_item", "ability", "stat_alignment"]}
    for row in rows:
        cat = row.get("category")
        if cat in result and row.get("rank", 99) <= 4:
            result[cat].append(f"{row['name']} {row.get('percentage', '')}")
    return result


def main():
    pokemon_list = fetch_index()
    top10 = filter_doubles_top10(pokemon_list)

    print(f"\nTop {len(top10)} Doubles Pokemon:")
    print("-" * 60)

    for i, p in enumerate(top10, 1):
        name = p.get("name") or p.get("battleName") or p.get("saved_name")
        print(f"\n{i}. {name}")

        try:
            battle = fetch_battle_rows(name)
            s = summarize(battle)
            print(f"   Moves:    {', '.join(s['move'][:4])}")
            print(f"   Items:    {', '.join(s['held_item'][:2])}")
            print(f"   Ability:  {', '.join(s['ability'][:1])}")
            print(f"   Nature:   {', '.join(s['stat_alignment'][:1])}")
        except Exception as e:
            print(f"   Battle data error: {e}")


if __name__ == "__main__":
    main()
