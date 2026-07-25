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
from collections import Counter, defaultdict

from gen_common import (
    ROLE_MOVES, SPREAD_MOVES, ABILITY_TYPE_OVERRIDES, SPEED_ABILITIES,
    AUTO_WEATHER_ABILITIES, derive_roles, item_to_stone_slug, build_megastone_map,
)

DB = "pokebase_champions.db"
OUT = "../website/data/TeamProfiles.json"
MIN_TEAMS = 10

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

# ── Build clustering — group by the EXACT 4-move signature each real team ran ──
# Tallying moves independently (old approach) blends mutually-exclusive builds
# together (e.g. Milotic's Scald-offense set and Coil-support set), producing
# a "top moves" list no real team ever runs as a single set. Clustering by the
# actual per-team signature keeps each build internally coherent.
move_class = {r["slug"]: r["damage_class"] for r in conn.execute("SELECT slug, damage_class FROM moves")}

team_moves_by_slot = defaultdict(list)
for r in conn.execute("SELECT team_id, position, move_slug FROM team_move").fetchall():
    team_moves_by_slot[(r["team_id"], r["position"])].append(r["move_slug"])

# slug -> {moveset_tuple: {"count": int, "items": Counter, "abilities": Counter}}
pokemon_clusters = defaultdict(dict)
for r in conn.execute("SELECT team_id, position, pokemon_slug, item, ability FROM team_pokemon").fetchall():
    moves = team_moves_by_slot.get((r["team_id"], r["position"]))
    if not moves:
        continue
    sig = tuple(sorted(moves))
    bucket = pokemon_clusters[r["pokemon_slug"]].setdefault(
        sig, {"count": 0, "items": Counter(), "abilities": Counter()}
    )
    bucket["count"] += 1
    if r["item"]:
        bucket["items"][r["item"]] += 1
    if r["ability"]:
        bucket["abilities"][r["ability"]] += 1

# Alt sets must be a real, recurring build — not tech-pick noise.
ALT_SET_MIN_COUNT = ROLE_MIN_COUNT
ALT_SET_MIN_PCT = 10.0
MAX_SETS = 3


def build_set(moves_sig, bucket, total_tc):
    """Derive item/ability/roles/attack_axis from one real per-team moveset cluster."""
    top_item = bucket["items"].most_common(1)
    top_ability = bucket["abilities"].most_common(1)
    item = top_item[0][0] if top_item else None
    ability = top_ability[0][0] if top_ability else None

    phys = sum(1 for m in moves_sig if move_class.get(m) == "physical")
    spec = sum(1 for m in moves_sig if move_class.get(m) == "special")
    move_axis = None
    if phys + spec:
        r = phys / (phys + spec)
        move_axis = "physical" if r >= 0.65 else "special" if r <= 0.35 else "mixed"

    roles = {role for ms, role in ROLE_MOVES.items() if ms in moves_sig}
    if set(moves_sig) & SPREAD_MOVES:
        roles.add("spread-attacker")
    ability_lower = (ability or "").lower()
    if ability_lower in SPEED_ABILITIES:
        roles.add(SPEED_ABILITIES[ability_lower])
    if ability_lower in AUTO_WEATHER_ABILITIES:
        roles.add(AUTO_WEATHER_ABILITIES[ability_lower])
    if item == "Choice Scarf":
        roles.add("scarf-user")

    return {
        "moves":       [{"slug": m, "class": move_class.get(m, "status")} for m in moves_sig],
        "item":        item,
        "ability":     ability,
        "move_axis":   move_axis,
        "roles":       sorted(roles),
        "count":       bucket["count"],
        "pct":         round(100 * bucket["count"] / total_tc, 1) if total_tc else 0,
    }

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

# ── Mega stones — items table repaired by name inference (see gen_common) ─────
stone_names = {r["slug"]: r["name"] for r in conn.execute("SELECT slug, name FROM items").fetchall()}
mega_stones = {
    slug: {"name": stone_names.get(slug) or slug.replace("-", " ").title(), "base": base}
    for slug, base in build_megastone_map(conn).items()
}

# base_pokemon_slug → [{stone_name, mega_form_slug, usage_count}]
base_to_megas = defaultdict(list)
seen = set()
for r in conn.execute("""
    SELECT pokemon_slug, item, COUNT(*) AS cnt
    FROM team_pokemon GROUP BY pokemon_slug, item ORDER BY cnt DESC
""").fetchall():
    if not r["item"]:
        continue
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
        # Item-name case variants ('raichunite y') map to the same form — merge counts
        existing = next((e for e in base_to_megas[base_slug] if e["mega_form_slug"] == mega_form), None)
        if existing:
            existing["usage_count"] += r["cnt"]
        else:
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

# ── Choice Scarf + megastone usage per pokemon ────────────────────────────────
# stone_pct drives the "flex mega" logic client-side: a species that often runs
# non-stone items (Venusaur 44% stone, Aerodactyl 44%) has a battle-worthy base
# form, while a stone-locked one (Floette 99%) is dead weight without its mega.
scarf_counts = defaultdict(int)
stone_held_counts = defaultdict(int)
total_item_counts = defaultdict(int)
for r in conn.execute("""
    SELECT pokemon_slug, item, COUNT(*) AS cnt
    FROM team_pokemon WHERE item IS NOT NULL
    GROUP BY pokemon_slug, item
""").fetchall():
    total_item_counts[r["pokemon_slug"]] += r["cnt"]
    if r["item"].lower() == "choice scarf":
        scarf_counts[r["pokemon_slug"]] += r["cnt"]
    ms = mega_stones.get(item_to_stone_slug(r["item"]))
    if ms and base_matches_stone(r["pokemon_slug"], ms["base"]):
        stone_held_counts[r["pokemon_slug"]] += r["cnt"]

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

    stat_axis = classify_attack_stats(atk, spa)
    bulk_axis = classify_bulk(hp, df, spd)
    tier = speed_tier(spe)

    # Build clusters, largest first — sets[0] is the primary (most common) build.
    clusters = pokemon_clusters.get(slug, {})
    built_sets = sorted(
        (build_set(sig, bucket, tc) for sig, bucket in clusters.items()),
        key=lambda s: -s["count"],
    )
    primary = built_sets[0] if built_sets else None
    alt_sets = [
        s for s in built_sets[1:] if s["count"] >= ALT_SET_MIN_COUNT and s["pct"] >= ALT_SET_MIN_PCT
    ][:MAX_SETS - 1]
    sets_out = [primary] + alt_sets if primary else []

    if primary:
        top_moves = primary["moves"]
        attack_axis = primary["move_axis"] or stat_axis
        roles = set(primary["roles"])
        roles.add(attack_axis + "-attacker")
    else:
        # No per-team moveset data (e.g. mega-only entry) — fall back to stats alone.
        top_moves = []
        attack_axis = stat_axis
        roles = {attack_axis + "-attacker"}

    # Choice Scarf — flag if ≥10% of entries carry it (species-wide, independent of set)
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
        "sets":        sets_out,
        "mega":        mega_info,
        "defensive":   defensive_profile(tc_data),
        "stab_types":  types,
        "image_url":   p.get("image_url") or "",
        "team_count":  tc,
        "scarf_pct":   scarf_pct,
        "stone_pct":   round(stone_held_counts.get(slug, 0) / total_items * 100, 1) if total_items else 0.0,
    }

conn.close()

with open(OUT, "w") as f:
    json.dump(result, f, indent=2)

print(f"Wrote {len(result)} profiles  ({skipped} skipped below {MIN_TEAMS} teams)")
