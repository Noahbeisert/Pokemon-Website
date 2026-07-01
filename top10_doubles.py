import json

with open("index_dump.json", encoding="utf-8") as f:
    data = json.load(f)

doubles_pokemon = []
for p in data["pokemon"]:
    battle = p.get("summary", {}).get("battleSummary", {}).get("Current", {}).get("Doubles")
    if not battle:
        continue
    top_entry = next((v for v in battle["top"].values() if v and v.get("column_position")), None)
    if not top_entry:
        continue
    position = top_entry["column_position"]
    doubles_pokemon.append((position, p, battle))

doubles_pokemon.sort(key=lambda x: x[0])
top10 = doubles_pokemon[:10]

print(f"Top 10 Doubles Pokemon by usage (Season M-3 / Current)\n{'='*60}")
for rank, (pos, p, battle) in enumerate(top10, 1):
    name = p["name"]
    top = battle["top"]
    moves = battle["values"]["move"][:4]
    item = top["held_item"]["name"]
    nature = top["stat_alignment"]["name"]
    ability = top["ability"]["name"]

    print(f"\n#{rank}  {name}  (position {pos})")
    print(f"    Top moves : {', '.join(moves)}")
    print(f"    Top item  : {item} ({top['held_item']['percentage']})")
    print(f"    Ability   : {ability} ({top['ability']['percentage']})")
    print(f"    Nature    : {nature} ({top['stat_alignment']['percentage']})")
