"""Shared tables for the TeamProfiles / TeamArchetypes generators."""

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

SPREAD_MOVES = {
    "heat-wave", "discharge", "earthquake", "hyper-voice", "muddy-water",
    "blizzard", "surf", "glacial-lance", "rock-slide", "sludge-wave",
    "dazzling-gleam", "petal-blizzard", "clanging-scales", "boomburst",
    "breaking-swipe", "icy-wind", "electroweb",
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


def derive_roles(moves_sig, ability, item):
    roles = {role for ms, role in ROLE_MOVES.items() if ms in moves_sig}
    if set(moves_sig) & SPREAD_MOVES:
        roles.add("spread-attacker")
    ability_lower = (ability or "").lower()
    if ability_lower in SPEED_ABILITIES:
        roles.add(SPEED_ABILITIES[ability_lower])
    if ability_lower in AUTO_WEATHER_ABILITIES:
        roles.add(AUTO_WEATHER_ABILITIES[ability_lower])
    if (item or "").lower() == "choice scarf":
        roles.add("scarf-user")
    return roles


def item_to_stone_slug(name):
    return (name or "").lower().strip().replace(" ", "-").replace("'", "")


def build_megastone_map(conn):
    """stone_slug -> mega base slug, repairing NULL/missing rows in `items`.

    The items table is incomplete (e.g. no Raichunite rows at all, and 19
    stones with mega_pokemon_slug NULL), but every stone name maps to its
    base pokemon by longest-common-prefix against the known mega bases.
    """
    mega_bases = set()
    for (slug,) in conn.execute("SELECT slug FROM pokemon WHERE slug LIKE '%-mega%'"):
        for suffix in ("-mega-x", "-mega-y", "-mega"):
            if slug.endswith(suffix):
                mega_bases.add(slug[: -len(suffix)])
                break

    def infer_base(stone_slug):
        s = stone_slug
        for suffix in ("-x", "-y"):
            if s.endswith(suffix):
                s = s[: -len(suffix)]
        best, best_len = None, 0
        for base in mega_bases:
            n = 0
            for a, b in zip(s, base):
                if a != b:
                    break
                n += 1
            if n >= 5 and n > best_len:
                best, best_len = base, n
        return best

    stones = {}
    for slug, base in conn.execute(
        "SELECT slug, mega_pokemon_slug FROM items WHERE is_megastone=1"
    ):
        stones[slug] = base or infer_base(slug)

    # Stones only seen as held items in team_pokemon (missing from items table)
    for (item,) in conn.execute(
        "SELECT DISTINCT item FROM team_pokemon WHERE item IS NOT NULL AND item != ''"
    ):
        slug = item_to_stone_slug(item)
        if slug in stones or not (slug.endswith("ite") or slug.endswith("ite-x") or slug.endswith("ite-y")):
            continue
        base = infer_base(slug)
        if base:
            stones[slug] = base

    return {s: b for s, b in stones.items() if b}
