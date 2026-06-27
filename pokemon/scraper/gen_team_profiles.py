"""
Generates website/data/TeamProfiles.json from pokebase_champions.db.

Per-pokemon output:
  name, types, stats          — base identity
  attack_axis                 — physical / special / mixed (stats + actual move mix)
  bulk_axis                   — physical-wall / special-wall / balanced
  speed_tier                  — fast (101+) / mid (71-100) / slow (≤70)
  roles                       — list of tags: fake-out, tr-setter, tailwind-setter,
                                setup, redirector, spread-attacker, pivot, etc.
  top_moves                   — top 6 [{slug, class}] by usage in tournament teams
  top_item, top_ability       — most common from tournament data
  mega                        — null or {forms: [{slug, name, types, stats,
                                attack_axis, stone, usage_count, defensive}]}
  defensive                   — {weaknesses, resists, immunities}
  stab_types                  — STAB types list
  image_url, team_count
"""

import sqlite3, json
from collections import defaultdict

DB = "pokebase_champions.db"
OUT = "../website/data/TeamProfiles.json"
MIN_TEAMS = 10

ROLE_MOVES = {
    "trick-room":      "tr-setter",
    "tailwind":        "tailwind-setter",
    "icy-wind":        "speed-drop",
    "electroweb":      "speed-drop",
    "scary-face":      "speed-drop",
    "fake-out":        "fake-out",
    "extreme-speed":   "priority",
    "sucker-punch":    "priority",
    "bullet-punch":    "priority",
    "mach-punch":      "priority",
    "water-shuriken":  "priority",
    "aqua-jet":        "priority",
    "ice-shard":       "priority",
    "shadow-sneak":    "priority",
    "quick-attack":    "priority",
    "dragon-dance":    "setup",
    "quiver-dance":    "setup",
    "swords-dance":    "setup",
    "nasty-plot":      "setup",
    "calm-mind":       "setup",
    "shell-smash":     "setup",
    "geomancy":        "setup",
    "coil":            "setup",
    "bulk-up":         "setup",
    "follow-me":       "redirector",
    "rage-powder":     "redirector",
    "helping-hand":    "support",
    "heal-pulse":      "support",
    "wide-guard":      "support",
    "quick-guard":     "support",
    "coaching":        "support",
    "light-screen":    "screen-setter",
    "reflect":         "screen-setter",
    "aurora-veil":     "screen-setter",
    "parting-shot":    "pivot",
    "u-turn":          "pivot",
    "volt-switch":     "pivot",
    "misty-terrain":   "terrain-setter",
    "electric-terrain":"terrain-setter",
    "grassy-terrain":  "terrain-setter",
    "psychic-terrain": "terrain-setter",
    "rain-dance":      "weather-setter",
    "sunny-day":       "weather-setter",
    "sandstorm":       "weather-setter",
    "snowscape":       "weather-setter",
}

# Abilities that override type-chart multipliers (type chart is types-only)
ABILITY_TYPE_OVERRIDES = {
    "levitate":      {"Ground": 0},
    "lightning rod": {"Electric": 0},
    "volt absorb":   {"Electric": 0},
    "motor drive":   {"Electric": 0},
    "storm drain":   {"Water": 0},
    "water absorb":  {"Water": 0},
    "flash fire":    {"Fire": 0},
    "sap sipper":    {"Grass": 0},
    "earth eater":   {"Ground": 0},
    "dry skin":      {"Water": 0},
    "thick fat":     {"Ice": 0.5, "Fire": 0.5},
    "heatproof":     {"Fire": 0.5},
    "wonder guard":  {},   # handled separately if needed
}

SPREAD_MOVES = {
    "heat-wave", "discharge", "earthquake", "hyper-voice", "muddy-water",
    "blizzard", "surf", "glacial-lance", "rock-slide", "sludge-wave",
    "dazzling-gleam", "petal-blizzard", "clanging-scales", "boomburst",
    "breaking-swipe", "icy-wind", "electroweb",
}

# Abilities that double speed under a specific condition (weather / terrain)
SPEED_ABILITIES = {
    "chlorophyll": "weather-speed",   # doubles in Sun
    "swift swim":  "weather-speed",   # doubles in Rain
    "slush rush":  "weather-speed",   # doubles in Snow/Hail
    "sand rush":   "weather-speed",   # doubles in Sandstorm
    "surge surfer":"weather-speed",   # doubles in Electric Terrain
}

# Abilities that auto-set weather — flag the setter role even without the move
AUTO_WEATHER_ABILITIES = {
    "drizzle":     "weather-setter",  # Pelipper, Politoed
    "drought":     "weather-setter",  # Ninetales, Torkoal
    "sand stream": "weather-setter",  # Tyranitar, Hippowdon
    "snow warning":"weather-setter",  # Abomasnow
}

# Only flag a role if the move appears in at least this many team entries
ROLE_MIN_COUNT = 5
# Only scan the top N moves per pokemon for role detection
ROLE_SCAN_DEPTH = 10


def parse_mult(s):
    if "/" in s:
        n, d = s.split("/")
        return int(n) / int(d)
    return float(s)


def classify_attack_stats(atk, spa):
    diff = atk - spa
    if diff >= 20:  return "physical"
    if diff <= -20: return "special"
    return "mixed"


def classify_attack_moves(moves):
    phys = sum(c for _, dc, c in moves if dc == "physical")
    spec = sum(c for _, dc, c in moves if dc == "special")
    total = phys + spec
    if total == 0: return None
    r = phys / total
    if r >= 0.65: return "physical"
    if r <= 0.35: return "special"
    return "mixed"


def classify_bulk(hp, df, spd):
    if hp * df > hp * spd * 1.15: return "physical-wall"
    if hp * spd > hp * df * 1.15: return "special-wall"
    return "balanced"


def speed_tier(spe):
    if spe >= 101: return "fast"
    if spe >= 71:  return "mid"
    return "slow"


def normalize_slug(slug):
    """Strip form suffixes to get the base name for mega validation."""
    for suffix in ("-eternal", "-mega-x", "-mega-y", "-mega"):
        if slug.endswith(suffix):
            return slug[: -len(suffix)]
    return slug


def find_mega_form(stone_slug, mega_pokemon_slug, all_slugs):
    # mega_pokemon_slug already IS the mega form
    if "-mega" in mega_pokemon_slug and mega_pokemon_slug in all_slugs:
        return mega_pokemon_slug
    base = mega_pokemon_slug
    # Charizardite X/Y pattern — stone slug ends in -x or -y
    if stone_slug.endswith("-x"):
        c = f"{base}-mega-x"
        if c in all_slugs: return c
    elif stone_slug.endswith("-y"):
        c = f"{base}-mega-y"
        if c in all_slugs: return c
    c = f"{base}-mega"
    if c in all_slugs: return c
    return None


def base_matches_stone(base_slug, stone_mega_pokemon_slug):
    """Validate that a mega stone is actually for this base pokemon."""
    return normalize_slug(base_slug) == normalize_slug(stone_mega_pokemon_slug)


def apply_ability_overrides(tc_data, ability):
    overrides = ABILITY_TYPE_OVERRIDES.get((ability or "").lower())
    if not overrides:
        return tc_data
    result = dict(tc_data)
    result.update(overrides)
    return result


def defensive_profile(tc_data):
    return {
        "weaknesses":  [t for t, m in tc_data.items() if m > 1],
        "resists":     [t for t, m in tc_data.items() if 0 < m < 1],
        "immunities":  [t for t, m in tc_data.items() if m == 0],
        "chart":       tc_data,   # full {type: multiplier} for coverage matrix
    }


conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

# ── Base pokemon table ────────────────────────────────────────────────────────
all_pokemon = {r["slug"]: dict(r) for r in conn.execute(
    "SELECT slug, name, types, hp, attack, defense, sp_attack, sp_defense, speed, image_url FROM pokemon"
).fetchall()}
all_slugs = set(all_pokemon.keys())

# ── Team appearance counts ─────────────────────────────────────────────────────
team_counts = {r["pokemon_slug"]: r["cnt"] for r in conn.execute("""
    SELECT pokemon_slug, COUNT(DISTINCT team_id) AS cnt
    FROM team_pokemon GROUP BY pokemon_slug
""").fetchall()}

# ── Move usage (from actual tournament teams) ──────────────────────────────────
pokemon_moves = defaultdict(list)
for r in conn.execute("""
    SELECT tp.pokemon_slug, tm.move_slug, m.damage_class, COUNT(*) AS cnt
    FROM team_move tm
    JOIN team_pokemon tp ON tm.team_id = tp.team_id AND tm.position = tp.position
    JOIN moves m ON m.slug = tm.move_slug
    GROUP BY tp.pokemon_slug, tm.move_slug
    ORDER BY tp.pokemon_slug, cnt DESC
""").fetchall():
    pokemon_moves[r["pokemon_slug"]].append((r["move_slug"], r["damage_class"], r["cnt"]))

# ── Items — prefer tournament_usage %, else raw counts ────────────────────────
pokemon_top_item = {}
for r in conn.execute("""
    SELECT pokemon_slug, name FROM tournament_usage
    WHERE category = 'item'
    GROUP BY pokemon_slug HAVING MAX(usage_pct)
    ORDER BY usage_pct DESC
""").fetchall():
    pokemon_top_item[r["pokemon_slug"]] = r["name"]

for r in conn.execute("""
    SELECT pokemon_slug, item, COUNT(*) AS cnt
    FROM team_pokemon WHERE item IS NOT NULL AND item != ''
    GROUP BY pokemon_slug, item ORDER BY cnt DESC
""").fetchall():
    if r["pokemon_slug"] not in pokemon_top_item:
        pokemon_top_item[r["pokemon_slug"]] = r["item"]

# ── Abilities — prefer tournament_usage %, else raw counts ────────────────────
pokemon_top_ability = {}
for r in conn.execute("""
    SELECT pokemon_slug, name FROM tournament_usage
    WHERE category = 'ability'
    GROUP BY pokemon_slug HAVING MAX(usage_pct)
""").fetchall():
    pokemon_top_ability[r["pokemon_slug"]] = r["name"]

for r in conn.execute("""
    SELECT pokemon_slug, ability, COUNT(*) AS cnt
    FROM team_pokemon WHERE ability IS NOT NULL AND ability != ''
    GROUP BY pokemon_slug, ability ORDER BY cnt DESC
""").fetchall():
    if r["pokemon_slug"] not in pokemon_top_ability:
        pokemon_top_ability[r["pokemon_slug"]] = r["ability"]

# ── Mega stones ────────────────────────────────────────────────────────────────
mega_stones = {r["slug"]: {"name": r["name"], "base": r["mega_pokemon_slug"]}
               for r in conn.execute(
                   "SELECT slug, name, mega_pokemon_slug FROM items WHERE is_megastone=1 AND mega_pokemon_slug IS NOT NULL"
               ).fetchall()}

def item_to_stone_slug(name):
    return name.lower().replace(" ", "-")

# base_pokemon_slug → [{stone_name, mega_form_slug, usage_count}]
base_to_megas = defaultdict(list)
seen = set()
for r in conn.execute("""
    SELECT pokemon_slug, item, COUNT(*) AS cnt
    FROM team_pokemon GROUP BY pokemon_slug, item ORDER BY cnt DESC
""").fetchall():
    stone_slug = item_to_stone_slug(r["item"])
    if stone_slug not in mega_stones:
        continue
    base_slug = r["pokemon_slug"]
    key = (base_slug, stone_slug)
    if key in seen:
        continue
    seen.add(key)
    ms = mega_stones[stone_slug]
    if not base_matches_stone(base_slug, ms["base"]):
        continue
    mega_form = find_mega_form(stone_slug, ms["base"], all_slugs)
    if mega_form and mega_form != base_slug:
        base_to_megas[base_slug].append({
            "stone_slug":    stone_slug,
            "stone_name":    ms["name"],
            "mega_form_slug": mega_form,
            "usage_count":   r["cnt"],
        })

# ── Mega form abilities (stored against mega slug in team_pokemon) ────────────
# Top 2 abilities per mega form — needed to detect weather abilities like Drought
mega_form_abilities = defaultdict(list)
for r in conn.execute("""
    SELECT pokemon_slug, ability, COUNT(*) AS cnt
    FROM team_pokemon
    WHERE pokemon_slug LIKE '%-mega%' AND ability IS NOT NULL AND ability != ''
    GROUP BY pokemon_slug, ability ORDER BY pokemon_slug, cnt DESC
""").fetchall():
    if len(mega_form_abilities[r["pokemon_slug"]]) < 2:
        mega_form_abilities[r["pokemon_slug"]].append((r["ability"], r["cnt"]))

# ── Choice Scarf usage per pokemon ───────────────────────────────────────────
scarf_counts = defaultdict(int)
total_item_counts = defaultdict(int)
for r in conn.execute("""
    SELECT pokemon_slug, item, COUNT(*) AS cnt
    FROM team_pokemon WHERE item IS NOT NULL
    GROUP BY pokemon_slug, item
""").fetchall():
    total_item_counts[r["pokemon_slug"]] += r["cnt"]
    if r["item"].lower() == "choice scarf":
        scarf_counts[r["pokemon_slug"]] += r["cnt"]

# ── Type chart ────────────────────────────────────────────────────────────────
type_chart = defaultdict(dict)
for r in conn.execute("SELECT pokemon_slug, attacking_type, multiplier FROM type_chart").fetchall():
    type_chart[r["pokemon_slug"]][r["attacking_type"]] = parse_mult(r["multiplier"])


# ── Build profiles ─────────────────────────────────────────────────────────────
result = {}
skipped = 0

for slug, p in all_pokemon.items():
    tc = team_counts.get(slug, 0)
    has_mega_data = slug in base_to_megas
    if tc < MIN_TEAMS and not has_mega_data:
        skipped += 1
        continue

    types = json.loads(p["types"])
    hp, atk, df, spa, spd, spe = (
        p["hp"], p["attack"], p["defense"], p["sp_attack"], p["sp_defense"], p["speed"]
    )

    moves = pokemon_moves.get(slug, [])
    top_moves = [{"slug": m, "class": dc} for m, dc, _ in moves[:6]]

    stat_axis  = classify_attack_stats(atk, spa)
    move_axis  = classify_attack_moves(moves)
    attack_axis = move_axis if move_axis else stat_axis

    bulk_axis = classify_bulk(hp, df, spd)
    tier = speed_tier(spe)

    # Only scan top moves that clear the minimum count threshold
    top_role_moves = {m for m, _, cnt in moves[:ROLE_SCAN_DEPTH] if cnt >= ROLE_MIN_COUNT}
    roles = set()
    for ms, role in ROLE_MOVES.items():
        if ms in top_role_moves:
            roles.add(role)
    if top_role_moves & SPREAD_MOVES:
        roles.add("spread-attacker")
    roles.add(attack_axis + "-attacker")

    # Ability-based speed control (Chlorophyll, Swift Swim, Drizzle, Drought, etc.)
    ability_lower = (pokemon_top_ability.get(slug) or "").lower()
    if ability_lower in SPEED_ABILITIES:
        roles.add(SPEED_ABILITIES[ability_lower])
    if ability_lower in AUTO_WEATHER_ABILITIES:
        roles.add(AUTO_WEATHER_ABILITIES[ability_lower])

    # Choice Scarf — flag if ≥10% of entries carry it
    total_items = total_item_counts.get(slug, 0)
    scarf_pct   = round(scarf_counts.get(slug, 0) / total_items * 100, 1) if total_items else 0.0
    if scarf_pct >= 10:
        roles.add("scarf-user")

    roles = sorted(roles)

    # Mega forms
    mega_info = None
    if has_mega_data:
        forms = []
        for entry in sorted(base_to_megas[slug], key=lambda x: -x["usage_count"]):
            mf_slug = entry["mega_form_slug"]
            mf = all_pokemon.get(mf_slug)
            if not mf:
                continue
            mf_types = json.loads(mf["types"])
            mf_axis  = classify_attack_stats(mf["attack"], mf["sp_attack"])

            # Ability data for this mega form (must come before type chart override)
            mf_abilities = mega_form_abilities.get(mf_slug, [])
            mf_top_ability = mf_abilities[0][0] if mf_abilities else None
            mf_ability_lower = (mf_top_ability or "").lower()

            mf_tc_raw = type_chart.get(mf_slug) or type_chart.get(slug, {})
            mf_tc     = apply_ability_overrides(mf_tc_raw, mf_top_ability)

            # Weather / speed roles triggered ON mega evolution
            mf_weather_roles = []
            if mf_ability_lower in SPEED_ABILITIES:
                mf_weather_roles.append(SPEED_ABILITIES[mf_ability_lower])
            if mf_ability_lower in AUTO_WEATHER_ABILITIES:
                mf_weather_roles.append(AUTO_WEATHER_ABILITIES[mf_ability_lower])

            forms.append({
                "slug":          mf_slug,
                "name":          mf["name"],
                "types":         mf_types,
                "stats": {
                    "hp": mf["hp"], "atk": mf["attack"], "def": mf["defense"],
                    "spa": mf["sp_attack"], "spd": mf["sp_defense"], "spe": mf["speed"],
                },
                "attack_axis":   mf_axis,
                "stone":         entry["stone_name"],
                "usage_count":   entry["usage_count"],
                "defensive":     defensive_profile(mf_tc),
                "ability":       mf_top_ability,
                "abilities":     [{"name": a, "count": c} for a, c in mf_abilities],
                "weather_roles": mf_weather_roles,
            })
        if forms:
            mega_info = {"forms": forms}

    tc_data = apply_ability_overrides(type_chart.get(slug, {}), pokemon_top_ability.get(slug))
    result[slug] = {
        "name":        p["name"],
        "types":       types,
        "stats":       {"hp": hp, "atk": atk, "def": df, "spa": spa, "spd": spd, "spe": spe},
        "attack_axis": attack_axis,
        "bulk_axis":   bulk_axis,
        "speed_tier":  tier,
        "roles":       roles,
        "top_moves":   top_moves,
        "top_item":    pokemon_top_item.get(slug),
        "top_ability": pokemon_top_ability.get(slug),
        "mega":        mega_info,
        "defensive":   defensive_profile(tc_data),
        "stab_types":  types,
        "image_url":   p.get("image_url") or "",
        "team_count":  tc,
        "scarf_pct":   scarf_pct,
    }

conn.close()

with open(OUT, "w") as f:
    json.dump(result, f, indent=2)

print(f"Wrote {len(result)} profiles  ({skipped} skipped below {MIN_TEAMS} teams)")
