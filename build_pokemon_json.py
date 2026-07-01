import json


def build_ev_spread(row):
    return {
        "hp":  row.get("hp_points"),
        "atk": row.get("attack_points"),
        "def": row.get("defense_points"),
        "spa": row.get("sp_atk_points"),
        "spd": row.get("sp_def_points"),
        "spe": row.get("speed_points"),
        "percentage": row.get("percentage_value"),
    }


def build_doubles(battle):
    rows = battle.get("rows", [])

    def category(cat):
        return [r for r in rows if r.get("category") == cat]

    moves = [
        {"rank": r["rank"], "name": r["name"], "percentage": r.get("percentage_value")}
        for r in category("move")
    ]
    items = [
        {"rank": r["rank"], "name": r["name"], "percentage": r.get("percentage_value")}
        for r in category("held_item")
    ]
    abilities = [
        {"rank": r["rank"], "name": r["name"], "percentage": r.get("percentage_value")}
        for r in category("ability")
    ]
    natures = [
        {
            "rank": r["rank"],
            "name": r["name"],
            "percentage": r.get("percentage_value"),
            "stat_up": r.get("stat_up"),
            "stat_down": r.get("stat_down"),
        }
        for r in category("stat_alignment")
    ]
    ev_spreads = [build_ev_spread(r) | {"rank": r["rank"]} for r in category("stat_points")]
    teammates = [
        {"rank": r["rank"], "name": r["name"]}
        for r in category("teammate")
    ]

    top = battle.get("top", {})
    top_move = top.get("move")
    usage_rank = top_move["column_position"] if top_move else None

    return {
        "usage_rank": usage_rank,
        "moves": moves,
        "held_items": items,
        "abilities": abilities,
        "natures": natures,
        "ev_spreads": ev_spreads,
        "teammates": teammates,
    }


def build_form(f):
    return {
        "name": f.get("saved_name") or f.get("form_name"),
        "title": f.get("title"),
        "kind": f.get("form_kind"),
        "types": f.get("types", []),
        "abilities": [a for a in (f.get("abilities") or "").split("|") if a],
        "hidden_ability": f.get("hidden_ability") or None,
        "sprite": f.get("image_path"),
        "base_stats": {
            "hp":    f.get("hp"),
            "atk":   f.get("attack"),
            "def":   f.get("defense"),
            "spa":   f.get("sp_attack"),
            "spd":   f.get("sp_defense"),
            "spe":   f.get("speed"),
            "total": f.get("base_stat_total"),
        },
    }


def build_entry(p):
    summary = p.get("summary", {})
    primary = summary.get("primary", {})
    forms = summary.get("forms", [])
    battle_summary = summary.get("battleSummary", {}).get("Current", {})
    doubles_raw = battle_summary.get("Doubles")

    return {
        "name": p["name"],
        "types": summary.get("types", []),
        "sprite": summary.get("sprite"),
        "base_stats": {
            "hp":    primary.get("hp"),
            "atk":   primary.get("attack"),
            "def":   primary.get("defense"),
            "spa":   primary.get("sp_attack"),
            "spd":   primary.get("sp_defense"),
            "spe":   primary.get("speed"),
            "total": primary.get("base_stat_total"),
        },
        "forms": [build_form(f) for f in forms] if len(forms) > 1 else [],
        "doubles": build_doubles(doubles_raw) if doubles_raw else None,
    }


with open("index_dump.json", encoding="utf-8") as f:
    data = json.load(f)

pokemon = [build_entry(p) for p in data["pokemon"]]

# sort by doubles usage rank, nulls last
pokemon.sort(key=lambda p: p["doubles"]["usage_rank"] if p.get("doubles") and p["doubles"]["usage_rank"] else 9999)

with open("pokemon_data.json", "w", encoding="utf-8") as f:
    json.dump(pokemon, f, indent=2, ensure_ascii=False)

with_doubles = sum(1 for p in pokemon if p["doubles"])
print(f"Written {len(pokemon)} Pokemon to pokemon_data.json")
print(f"  With Doubles data : {with_doubles}")
print(f"  Without           : {len(pokemon) - with_doubles}")
print(f"\nTop 5 by Doubles usage:")
for p in pokemon[:5]:
    d = p["doubles"]
    print(f"  #{d['usage_rank']:>3}  {p['name']}  ({'/'.join(p['types'])})")
    print(f"         moves: {', '.join(m['name'] for m in d['moves'][:4])}")
