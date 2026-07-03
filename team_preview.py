import json
from itertools import combinations

# ---------------------------------------------------------------------------
# Type chart — non-1x matchups only (attacker type -> {defender type: mult})
# ---------------------------------------------------------------------------
_CHART = {
    "Normal":   {"Rock": 0.5, "Ghost": 0,   "Steel": 0.5},
    "Fire":     {"Grass": 2, "Ice": 2, "Bug": 2, "Steel": 2,
                 "Fire": 0.5, "Rock": 0.5, "Water": 0.5, "Dragon": 0.5},
    "Water":    {"Fire": 2, "Ground": 2, "Rock": 2,
                 "Water": 0.5, "Grass": 0.5, "Dragon": 0.5},
    "Electric": {"Water": 2, "Flying": 2,
                 "Electric": 0.5, "Grass": 0.5, "Dragon": 0.5, "Ground": 0},
    "Grass":    {"Water": 2, "Ground": 2, "Rock": 2,
                 "Fire": 0.5, "Grass": 0.5, "Poison": 0.5, "Flying": 0.5,
                 "Bug": 0.5, "Dragon": 0.5, "Steel": 0.5},
    "Ice":      {"Grass": 2, "Ground": 2, "Flying": 2, "Dragon": 2,
                 "Water": 0.5, "Ice": 0.5, "Fire": 0.5, "Steel": 0.5},
    "Fighting": {"Normal": 2, "Rock": 2, "Steel": 2, "Ice": 2, "Dark": 2,
                 "Poison": 0.5, "Flying": 0.5, "Psychic": 0.5, "Bug": 0.5,
                 "Fairy": 0.5, "Ghost": 0},
    "Poison":   {"Grass": 2, "Fairy": 2,
                 "Poison": 0.5, "Ground": 0.5, "Rock": 0.5, "Ghost": 0.5,
                 "Steel": 0},
    "Ground":   {"Fire": 2, "Electric": 2, "Poison": 2, "Rock": 2, "Steel": 2,
                 "Grass": 0.5, "Bug": 0.5, "Flying": 0},
    "Flying":   {"Grass": 2, "Fighting": 2, "Bug": 2,
                 "Electric": 0.5, "Rock": 0.5, "Steel": 0.5},
    "Psychic":  {"Fighting": 2, "Poison": 2,
                 "Psychic": 0.5, "Steel": 0.5, "Dark": 0},
    "Bug":      {"Grass": 2, "Psychic": 2, "Dark": 2,
                 "Fire": 0.5, "Fighting": 0.5, "Flying": 0.5, "Ghost": 0.5,
                 "Steel": 0.5, "Fairy": 0.5, "Poison": 0.5},
    "Rock":     {"Fire": 2, "Ice": 2, "Flying": 2, "Bug": 2,
                 "Fighting": 0.5, "Ground": 0.5, "Steel": 0.5},
    "Ghost":    {"Ghost": 2, "Psychic": 2,
                 "Dark": 0.5, "Normal": 0},
    "Dragon":   {"Dragon": 2,
                 "Steel": 0.5, "Fairy": 0},
    "Dark":     {"Ghost": 2, "Psychic": 2,
                 "Fighting": 0.5, "Dark": 0.5, "Fairy": 0.5},
    "Steel":    {"Ice": 2, "Rock": 2, "Fairy": 2,
                 "Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Steel": 0.5},
    "Fairy":    {"Fighting": 2, "Dragon": 2, "Dark": 2,
                 "Fire": 0.5, "Poison": 0.5, "Steel": 0.5},
}

# Known move -> type (damaging moves that matter for coverage analysis)
MOVE_TYPES = {
    "Dragon Claw": "Dragon", "Draco Meteor": "Dragon", "Dragon Pulse": "Dragon",
    "Outrage": "Dragon", "Dragon Rush": "Dragon", "Breaking Swipe": "Dragon",
    "Scale Shot": "Dragon",
    "Earthquake": "Ground", "Earth Power": "Ground", "Bulldoze": "Ground",
    "High Horsepower": "Ground", "Stomping Tantrum": "Ground", "Scorching Sands": "Ground",
    "Rock Slide": "Rock", "Stone Edge": "Rock", "Rock Tomb": "Rock",
    "Iron Head": "Steel", "Flash Cannon": "Steel", "Gyro Ball": "Steel",
    "Heavy Slam": "Steel", "Steel Roller": "Steel",
    "Close Combat": "Fighting", "Superpower": "Fighting", "Focus Blast": "Fighting",
    "Drain Punch": "Fighting", "Mach Punch": "Fighting", "Body Press": "Fighting",
    "Brick Break": "Fighting", "Cross Chop": "Fighting",
    "Flare Blitz": "Fire", "Fire Blast": "Fire", "Heat Wave": "Fire",
    "Flamethrower": "Fire", "Sacred Fire": "Fire", "Overheat": "Fire",
    "Fire Fang": "Fire", "Flame Charge": "Fire",
    "Moonblast": "Fairy", "Dazzling Gleam": "Fairy", "Play Rough": "Fairy",
    "Draining Kiss": "Fairy",
    "Hyper Voice": "Normal", "Return": "Normal", "Double-Edge": "Normal",
    "Body Slam": "Normal", "Quick Attack": "Normal", "Extreme Speed": "Normal",
    "Facade": "Normal", "Boomburst": "Normal",
    "Brave Bird": "Flying", "Aerial Ace": "Flying", "Air Slash": "Flying",
    "Hurricane": "Flying", "Dual Wingbeat": "Flying",
    "Sucker Punch": "Dark", "Kowtow Cleave": "Dark", "Knock Off": "Dark",
    "Crunch": "Dark", "Night Slash": "Dark", "Dark Pulse": "Dark",
    "Throat Chop": "Dark", "Foul Play": "Dark",
    "Psychic": "Psychic", "Psyshock": "Psychic", "Zen Headbutt": "Psychic",
    "Expanding Force": "Psychic", "Psycho Cut": "Psychic",
    "Shadow Ball": "Ghost", "Poltergeist": "Ghost", "Shadow Sneak": "Ghost",
    "Last Respects": "Ghost", "Hex": "Ghost", "Phantom Force": "Ghost",
    "Spirit Shackle": "Ghost",
    "Surf": "Water", "Hydro Pump": "Water", "Scald": "Water",
    "Aqua Jet": "Water", "Wave Crash": "Water", "Liquidation": "Water",
    "Flip Turn": "Water", "Waterfall": "Water", "Muddy Water": "Water",
    "Origin Pulse": "Water", "Steam Eruption": "Water",
    "Thunderbolt": "Electric", "Thunder": "Electric", "Wild Charge": "Electric",
    "Volt Tackle": "Electric", "Discharge": "Electric", "Volt Switch": "Electric",
    "Blizzard": "Ice", "Ice Beam": "Ice", "Icicle Crash": "Ice",
    "Ice Punch": "Ice", "Icy Wind": "Ice", "Ice Shard": "Ice",
    "Avalanche": "Ice", "Freeze-Dry": "Ice", "Ice Hammer": "Ice",
    "Frost Breath": "Ice",
    "Leaf Storm": "Grass", "Giga Drain": "Grass", "Solar Beam": "Grass",
    "Energy Ball": "Grass", "Power Whip": "Grass", "Wood Hammer": "Grass",
    "Matcha Gotcha": "Grass", "Seed Bomb": "Grass", "Petal Blizzard": "Grass",
    "Flower Trick": "Grass", "Grassy Glide": "Grass",
    "Sludge Bomb": "Poison", "Sludge Wave": "Poison", "Poison Jab": "Poison",
    "Gunk Shot": "Poison", "Dire Claw": "Poison",
    "Bug Buzz": "Bug", "X-Scissor": "Bug", "U-turn": "Bug",
    "Lunge": "Bug",
    "Iron Tail": "Steel",
    "Aura Sphere": "Fighting",
    "Fell Stinger": "Bug",
    "Pollen Puff": "Bug",
    "Weather Ball": "Normal",  # changes type with weather — approximate as Normal
}

# Support moves that signal specific roles
ROLE_SIGNALS = {
    "fake_out":      ["Fake Out"],
    "tailwind":      ["Tailwind"],
    "trick_room":    ["Trick Room"],
    "redirect":      ["Rage Powder", "Follow Me"],
    "speed_control": ["Icy Wind", "Thunder Wave", "Electroweb", "Bulldoze", "Rock Tomb"],
    "setup":         ["Swords Dance", "Nasty Plot", "Quiver Dance", "Dragon Dance",
                      "Calm Mind", "Shell Smash", "Shift Gear"],
    # Separate from "setup": Coil boosts Defense (and accuracy), so it makes the
    # user tankier and more reliable immediately — unlike pure power/speed setup
    # moves, it doesn't need a safe backline turn to pay off.
    "bulk_setup":    ["Coil"],
    "screen":        ["Aurora Veil", "Light Screen", "Reflect"],
    "weather":       ["Sunny Day", "Rain Dance", "Sandstorm", "Snowscape", "Hail"],
    "healing":       ["Life Dew", "Heal Pulse", "Recover", "Roost", "Slack Off"],
    "helping_hand":  ["Helping Hand"],
    "wide_guard":    ["Wide Guard"],
}

# Every doubles mon runs one of these — they don't differentiate a role
PROTECT_MOVES = {"Protect", "Detect", "King's Shield", "Baneful Bunker",
                  "Spiky Shield", "Obstruct"}

# Role tags that mean "does something for the team" rather than "hits things"
SUPPORT_FLAVOR_ROLES = {
    "fake_out", "tailwind", "trick_room", "redirect", "speed_control",
    "screen", "weather", "healing", "helping_hand", "wide_guard",
}


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

_DB = None

def load_db(path="pokemon_data.json"):
    global _DB
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    _DB = {p["name"].lower(): p for p in data}
    return _DB


def find(name):
    db = _DB or load_db()
    key = name.strip().lower()
    if key in db:
        return db[key]
    # fuzzy: match by prefix or substring
    matches = [v for k, v in db.items() if k.startswith(key) or key in k]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        # prefer shorter name (more exact)
        matches.sort(key=lambda p: len(p["name"]))
        return matches[0]
    raise KeyError(f"Pokemon not found: {name!r}")


# ---------------------------------------------------------------------------
# Type matchup helpers
# ---------------------------------------------------------------------------

def type_mult(atk_type, def_type):
    return _CHART.get(atk_type, {}).get(def_type, 1.0)


def move_effectiveness(move_type, def_types):
    m = 1.0
    for dt in def_types:
        m *= type_mult(move_type, dt)
    return m


def stab_coverage(attacker, defender):
    """Best type-effectiveness the attacker can achieve using STAB or known moves."""
    def_types = defender["types"]
    best = 0.0

    # STAB moves
    for at in attacker["types"]:
        best = max(best, move_effectiveness(at, def_types))

    # Non-STAB coverage from top moves
    if attacker.get("doubles"):
        for m in attacker["doubles"]["moves"][:6]:
            mtype = MOVE_TYPES.get(m["name"])
            if mtype and mtype not in attacker["types"]:
                best = max(best, move_effectiveness(mtype, def_types))

    return best


def defensive_weakness(defender, attacker_types):
    """Worst matchup the defender has against attacker's type coverage."""
    return stab_coverage(attacker_types, defender)


# ---------------------------------------------------------------------------
# Role detection
# ---------------------------------------------------------------------------

# A move used by fewer than this % of recorded teams is a tech pick, not a real set.
# Position-based cutoffs (e.g. "top 6") are wrong when a mon has 2+ common builds —
# a move can be a real, common set and still rank 8th because it competes with moves
# from a *different* build (see Milotic: Coil/Hypnosis sit at 25%/24.4%, rank 8-9,
# right behind moves from its separate Scald/Ice Beam damage set).
ROLE_MIN_USAGE = 20.0

def detect_roles(pokemon):
    roles = []
    if not pokemon.get("doubles"):
        return roles
    top_moves = {m["name"] for m in pokemon["doubles"]["moves"] if m["percentage"] >= ROLE_MIN_USAGE}
    for role, signals in ROLE_SIGNALS.items():
        if any(s in top_moves for s in signals):
            roles.append(role)
    return roles


_MOVE_CATEGORIES = None

def load_move_categories(path="moves_data.json"):
    global _MOVE_CATEGORIES
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    _MOVE_CATEGORIES = {m["name"]: m["category"] for m in data.values()}
    return _MOVE_CATEGORIES


def archetype(pokemon):
    """Broad Support / Damage / Hybrid tag from role flavor + how many top moves hit."""
    if not pokemon.get("doubles"):
        return "damage"
    cats = _MOVE_CATEGORIES or load_move_categories()
    support_flavor = bool(set(detect_roles(pokemon)) & SUPPORT_FLAVOR_ROLES)
    if not support_flavor:
        return "damage"
    top_moves = [m["name"] for m in pokemon["doubles"]["moves"]
                 if m["percentage"] >= ROLE_MIN_USAGE and m["name"] not in PROTECT_MOVES]
    dmg_count = sum(1 for name in top_moves if cats.get(name) in ("Physical", "Special"))
    return "hybrid" if dmg_count >= 2 else "support"


def effective_speed(pokemon):
    """Approximate speed after applying most common nature."""
    base = (pokemon["base_stats"].get("spe") or 0)
    if not pokemon.get("doubles"):
        return base
    natures = pokemon["doubles"]["natures"]
    if not natures:
        return base
    top_nature = natures[0]
    if top_nature["stat_up"] == "Speed":
        return base * 1.1
    if top_nature["stat_down"] == "Speed":
        return base * 0.9
    return base


# ---------------------------------------------------------------------------
# Scoring functions
# ---------------------------------------------------------------------------

# Abilities whose value is only realized after the ally has taken damage —
# leading wastes the trigger since both sides start turn 1 at full HP.
_WASTED_LEAD_ABILITIES = {"Hospitality": -2.5}


def lead_affinity(pokemon):
    """How likely this Pokemon is to lead (0–10 scale)."""
    roles = detect_roles(pokemon)
    score = 3.0  # baseline — anyone can lead
    if "fake_out" in roles:
        score += 4
    if "tailwind" in roles:
        score += 2.5
    if "trick_room" in roles:
        score += 2
    if "redirect" in roles:
        score += 2
    if "speed_control" in roles:
        score += 1
    if "screen" in roles:
        score += 1
    if "setup" in roles:
        score -= 1  # setup mons often go in back
    if "bulk_setup" in roles:
        score += 1  # boosts survivability/accuracy right away — a fine lead trait
    if pokemon.get("doubles") and pokemon["doubles"]["abilities"]:
        top_ability = pokemon["doubles"]["abilities"][0]["name"]
        score += _WASTED_LEAD_ABILITIES.get(top_ability, 0)
    # Speed: very fast mons are more often leads
    spe = effective_speed(pokemon)
    if spe >= 110:
        score += 0.5
    return min(score, 10.0)


def synergy_bonus(p1, p2):
    """How often p1 and p2 co-appear as teammates."""
    if not p1.get("doubles") or not p2.get("doubles"):
        return 0
    teammates_of_p1 = {t["name"].lower() for t in p1["doubles"]["teammates"]}
    teammates_of_p2 = {t["name"].lower() for t in p2["doubles"]["teammates"]}
    bonus = 0
    if p2["name"].lower() in teammates_of_p1:
        rank = next(t["rank"] for t in p1["doubles"]["teammates"]
                    if t["name"].lower() == p2["name"].lower())
        bonus += max(0, 4 - rank * 0.3)  # rank 1 = +3.7, rank 10 = +1.0
    if p1["name"].lower() in teammates_of_p2:
        rank = next(t["rank"] for t in p2["doubles"]["teammates"]
                    if t["name"].lower() == p1["name"].lower())
        bonus += max(0, 4 - rank * 0.3)
    return bonus


# Weather ability mappings
_WEATHER_SET = {
    "Drizzle":     "rain",
    "Drought":     "sun",
    "Sand Stream": "sand",
    "Snow Warning": "snow",
}
_WEATHER_BEATS = {"rain": "sun", "sun": "rain", "sand": "rain", "snow": "sun"}
_WEATHER_MOVES = {"Rain Dance", "Sunny Day", "Sandstorm", "Hail", "Snowscape", "Chilly Reception"}


def pokemon_weather(pokemon):
    """Weather this Pokemon sets, checking mega form ability first."""
    for form in pokemon.get("forms", []):
        if form["kind"].startswith("Mega"):
            for ab in form.get("abilities", []):
                if ab in _WEATHER_SET:
                    return _WEATHER_SET[ab]
    if pokemon.get("doubles") and pokemon["doubles"]["abilities"]:
        ab = pokemon["doubles"]["abilities"][0]["name"]
        if ab in _WEATHER_SET:
            return _WEATHER_SET[ab]
    return None


def weather_counter_bonus(pokemon, opp_team):
    """
    Bonus for a Pokemon whose weather ability directly counters the opponent's weather.
    Charizard Y (Drought) vs Pelipper (Drizzle) team → large bonus.
    """
    my_weather = pokemon_weather(pokemon)
    if not my_weather:
        return 0
    opp_weathers = {pokemon_weather(p) for p in opp_team} - {None}
    needed = _WEATHER_BEATS.get(my_weather)
    if needed and needed in opp_weathers:
        return 4.0  # substantial — flips the opponent's entire win condition
    return 0


_MOVE_WEATHER = {
    "Rain Dance": "rain", "Sunny Day": "sun", "Sandstorm": "sand",
    "Hail": "snow", "Snowscape": "snow", "Chilly Reception": "snow",
}


def weather_backup_threats(my_weather_counters, opp_full_team, opp_predicted_bring):
    """
    Opponent Pokemon that can re-set weather after my counter goes up.
    Two vectors: switch-in ability (Pelipper Drizzle), and weather move (Sableye Rain Dance).
    Only flags moves/abilities that set weather which beats mine — opp Sunny Day on a rain
    team is not a threat to my sun, so it's filtered out.
    """
    my_weathers = {pokemon_weather(p) for p in my_weather_counters} - {None}
    if not my_weathers:
        return []

    in_bring = {p["name"] for p in opp_predicted_bring}
    threats = []

    for p in opp_full_team:
        label = "IN bring" if p["name"] in in_bring else "possible bring"
        seen = False

        # 1. Switch-in weather ability that beats mine
        opp_w = pokemon_weather(p)
        if opp_w and any(_WEATHER_BEATS.get(opp_w) == mw for mw in my_weathers):
            ab = p["doubles"]["abilities"][0]["name"] if p.get("doubles") and p["doubles"]["abilities"] else "?"
            threats.append((p["name"], f"switch-in {opp_w} ({ab})", label))
            seen = True

        # 2. Weather move that counters mine — skip if already listed via ability
        if not seen and p.get("doubles"):
            moves = {m["name"] for m in p["doubles"]["moves"][:8]}
            for move in moves & _WEATHER_MOVES:
                move_wx = _MOVE_WEATHER[move]
                if any(_WEATHER_BEATS.get(move_wx) == mw for mw in my_weathers):
                    ab = p["doubles"]["abilities"][0]["name"] if p["doubles"]["abilities"] else "?"
                    priority_tag = " [PRIORITY via Prankster]" if ab == "Prankster" else ""
                    threats.append((p["name"], f"{move}{priority_tag}", label))
                    break

    return threats


def usage_score(pokemon):
    """Lower usage rank = higher score."""
    if not pokemon.get("doubles"):
        return 0
    rank = pokemon["doubles"]["usage_rank"] or 999
    return max(0, 10 - rank * 0.04)


def threat_to_team(attacker, team):
    """How threatening is this attacker against the given team (avg best coverage)."""
    if not team:
        return 0
    return sum(stab_coverage(attacker, d) for d in team) / len(team)


def bring_scores(opp_6, my_6):
    """Score each opponent Pokemon for likelihood of being in their bring-4."""
    scores = []
    for p in opp_6:
        s = usage_score(p) * 1.5
        s += threat_to_team(p, my_6) * 2.0
        # synergy with rest of their own team
        for other in opp_6:
            if other is not p:
                s += synergy_bonus(p, other) * 0.3
        scores.append((s, p))
    scores.sort(reverse=True)
    return scores  # list of (score, pokemon)


def lead_pair_score(p1, p2, vs_team):
    """Score a lead pair: lead affinity + synergy + threat to vs_team + weather denial."""
    s = lead_affinity(p1) + lead_affinity(p2)
    # Low weight: this is teammate co-occurrence (who gets built together),
    # not lead-order data — bring_scores/bring_weight already use it for team
    # selection, so lead_affinity should dominate here, not this.
    s += synergy_bonus(p1, p2) * 0.2
    s += threat_to_team(p1, vs_team) + threat_to_team(p2, vs_team)
    # If either lead can immediately flip the opponent's weather, that's high value
    s += max(weather_counter_bonus(p, vs_team) for p in (p1, p2))
    return s


# ---------------------------------------------------------------------------
# Bring-4 enumeration
# ---------------------------------------------------------------------------

def bring_weight(bring4):
    """Likelihood score for this bring-4 combo (higher = more likely to be played)."""
    s = sum(usage_score(p) for p in bring4)
    for p1, p2 in combinations(bring4, 2):
        s += synergy_bonus(p1, p2) * 0.2
    return s


def best_lead_from(bring4, vs_bring4):
    """Best lead pair from bring4 vs vs_bring4. Returns (score, p1, p2, [back1, back2])."""
    best = (-999, None, None)
    for p1, p2 in combinations(bring4, 2):
        s = lead_pair_score(p1, p2, list(vs_bring4))
        if s > best[0]:
            best = (s, p1, p2)
    score, p1, p2 = best
    back = [p for p in bring4 if p is not p1 and p is not p2]
    return score, p1, p2, back


def matchup_score(my_bring4, opp_bring4):
    """Net score = my best lead score minus their best lead score."""
    my_s,  *_ = best_lead_from(my_bring4,  list(opp_bring4))
    opp_s, *_ = best_lead_from(opp_bring4, list(my_bring4))
    return (my_s or 0) - (opp_s or 0)


# ---------------------------------------------------------------------------
# Mega Evolution  (used for effective types/stats in threat calculations)
# ---------------------------------------------------------------------------

def find_mega_stone(pokemon):
    """Return (stone_name, pct) if this Pokemon has a Mega form and its Mega Stone in item data."""
    has_mega = any(f["kind"].startswith("Mega") for f in pokemon.get("forms", []))
    if not has_mega or not pokemon.get("doubles"):
        return None
    for item in pokemon["doubles"]["held_items"]:
        name = item["name"]
        if name.endswith("ite") and name != "Eviolite":
            return (name, item.get("percentage") or 0)
    return None


def predicted_mega_form(pokemon):
    """Pick which Mega form best matches the Pokemon's predicted playstyle."""
    mega_forms = [f for f in pokemon.get("forms", []) if f["kind"].startswith("Mega")]
    if not mega_forms:
        return None
    if len(mega_forms) == 1:
        return mega_forms[0]
    # Multiple megas (e.g. Charizard X vs Y): use top nature stat_up to decide
    natures = pokemon.get("doubles", {}).get("natures", [])
    stat_up = natures[0].get("stat_up", "") if natures else ""
    if stat_up == "Sp. Atk":
        return max(mega_forms, key=lambda f: f["base_stats"].get("spa") or 0)
    if stat_up == "Attack":
        return max(mega_forms, key=lambda f: f["base_stats"].get("atk") or 0)
    return mega_forms[0]


def apply_mega(pokemon, mega_form):
    """Return a new pokemon dict with mega types and stats, moves unchanged."""
    if not mega_form:
        return pokemon
    return {**pokemon, "types": mega_form["types"], "base_stats": mega_form["base_stats"]}


def mega_candidates(team):
    """Return list of (stone_pct, pokemon, mega_form, stone_name) sorted by likelihood."""
    out = []
    for p in team:
        result = find_mega_stone(p)
        if result:
            stone, pct = result
            if pct < 20:
                continue
            form = predicted_mega_form(p)
            out.append((pct, p, form, stone))
    out.sort(reverse=True)
    return out


def apply_team_mega(team, chosen_mega_pokemon):
    """Return team list with the chosen Pokemon replaced by its mega-applied version."""
    return [
        apply_mega(p, predicted_mega_form(p)) if p is chosen_mega_pokemon else p
        for p in team
    ]


def mega_matchup_matrix(my_candidates, their_candidates, my_team, their_team):
    """
    For every combination of (my mega choice × their mega choice), compute
    net score = my mega's threat to their team  −  their mega's threat to my team.
    Positive = favorable for me.
    Returns list of dicts sorted best-for-me first.
    """
    rows = []
    for my_pct, my_p, my_form, my_stone in my_candidates:
        for their_pct, their_p, their_form, their_stone in their_candidates:
            my_eff_team    = apply_team_mega(my_team,   my_p)
            their_eff_team = apply_team_mega(their_team, their_p)
            my_mega_eff    = apply_mega(my_p,    my_form)
            their_mega_eff = apply_mega(their_p, their_form)

            my_threat    = threat_to_team(my_mega_eff,    their_eff_team)
            their_threat = threat_to_team(their_mega_eff, my_eff_team)
            net = round(my_threat - their_threat, 2)

            rows.append({
                "my_mega":     my_form["name"] if my_form else my_p["name"],
                "their_mega":  their_form["name"] if their_form else their_p["name"],
                "my_pct":      my_pct,
                "their_pct":   their_pct,
                "net":         net,
            })
    rows.sort(key=lambda r: r["net"], reverse=True)
    return rows


# ---------------------------------------------------------------------------
# Main solver
# ---------------------------------------------------------------------------

def solve_preview(my_names, opp_names):
    load_db()
    my_team  = [find(n) for n in my_names]
    opp_team = [find(n) for n in opp_names]

    # Apply predicted megas for threat calculations
    my_megas_list  = mega_candidates(my_team)
    opp_megas_list = mega_candidates(opp_team)
    my_mega_p  = my_megas_list[0][1]  if my_megas_list  else None
    opp_mega_p = opp_megas_list[0][1] if opp_megas_list else None
    my_eff  = apply_team_mega(my_team,  my_mega_p)  if my_mega_p  else my_team
    opp_eff = apply_team_mega(opp_team, opp_mega_p) if opp_mega_p else opp_team

    # All C(6,4)=15 bring combos per side
    my_brings  = list(combinations(my_eff,  4))
    opp_brings = list(combinations(opp_eff, 4))

    opp_brings_weighted = [(bring_weight(b), b) for b in opp_brings]
    total_opp_w = sum(w for w, _ in opp_brings_weighted)

    # Score each of my 15 bring options by expected value vs all 15 opp combos
    # + weather counter bonus (e.g. Charizard Y Drought vs opponent rain)
    my_bring_scores = sorted(
        [
            (
                sum((w / total_opp_w) * matchup_score(my_b, ob) for w, ob in opp_brings_weighted)
                + sum(weather_counter_bonus(p, opp_eff) for p in my_b),
                my_b,
            )
            for my_b in my_brings
        ],
        reverse=True,
        key=lambda x: x[0],
    )

    # Opp bring options sorted by likelihood
    opp_bring_scores = sorted(opp_brings_weighted, reverse=True, key=lambda x: x[0])

    my_best_bring  = my_bring_scores[0][1]
    pred_opp_bring = opp_bring_scores[0][1]

    # Lead options: my best bring vs predicted opp bring
    my_lead_opts = []
    for p1, p2 in combinations(my_best_bring, 2):
        back = [p for p in my_best_bring if p is not p1 and p is not p2]
        s = sum(
            lead_pair_score(p1, p2, [op1, op2]) * (1 / (i + 1))
            for i, (op1, op2) in enumerate(combinations(pred_opp_bring, 2))
        )
        my_lead_opts.append((s, p1, p2, back))
    my_lead_opts.sort(reverse=True)

    opp_lead_opts = []
    for op1, op2 in combinations(pred_opp_bring, 2):
        back = [p for p in pred_opp_bring if p is not op1 and p is not op2]
        s = lead_pair_score(op1, op2, list(my_best_bring))
        opp_lead_opts.append((s, op1, op2, back))
    opp_lead_opts.sort(reverse=True)

    # Counter-lead: for each of opp's top lead pairs, my best response from my best bring
    counter_leads = {}
    for _, op1, op2, oback in opp_lead_opts:
        key = f"{op1['name']} + {op2['name']}"
        best_s, best_p1, best_p2 = max(
            ((lead_pair_score(p1, p2, [op1, op2]), p1, p2)
             for p1, p2 in combinations(my_best_bring, 2)),
            key=lambda x: x[0],
        )
        back = [p for p in my_best_bring if p is not best_p1 and p is not best_p2]
        counter_leads[key] = (round(best_s, 1), best_p1["name"], best_p2["name"],
                              [p["name"] for p in back])

    def fmt(bring4):
        return [p["name"] for p in bring4]

    # Weather matchup summary
    opp_weather_setters = [(p["name"], pokemon_weather(p)) for p in opp_team if pokemon_weather(p)]
    my_weather_counters_list = [p for p in my_eff if weather_counter_bonus(p, opp_team) > 0]
    my_weather_counters = [(p["name"], weather_counter_bonus(p, opp_team)) for p in my_weather_counters_list]
    wx_back_threats = weather_backup_threats(my_weather_counters_list, opp_team, list(pred_opp_bring))

    return {
        "my_megas":            [(round(pct, 1), p["name"], f["name"] if f else "?", stone)
                                for pct, p, f, stone in my_megas_list],
        "opp_megas":           [(round(pct, 1), p["name"], f["name"] if f else "?", stone)
                                for pct, p, f, stone in opp_megas_list],
        "my_brings":           [(round(s, 2), fmt(b)) for s, b in my_bring_scores[:5]],
        "opp_brings":          [(round(w, 2), fmt(b)) for w, b in opp_bring_scores[:5]],
        "my_best_bring":       fmt(my_best_bring),
        "pred_opp_bring":      fmt(pred_opp_bring),
        "my_leads":            [(round(s, 1), p1["name"], p2["name"], [p["name"] for p in back])
                                for s, p1, p2, back in my_lead_opts],
        "opp_leads":           [(round(s, 1), op1["name"], op2["name"], [p["name"] for p in back])
                                for s, op1, op2, back in opp_lead_opts],
        "counter_leads":       counter_leads,
        "roles":               {p["name"]: detect_roles(p) for p in opp_team},
        "archetypes":          {p["name"]: archetype(p) for p in opp_team},
        "speed_tiers":         {p["name"]: round(effective_speed(p), 1) for p in opp_team},
        "opp_weather_setters":  opp_weather_setters,
        "my_weather_counters":  my_weather_counters,
        "wx_back_threats":      wx_back_threats,
        "threats": {
            p["name"]: [
                f"{d['name']} ({stab_coverage(p, d):.1f}x)"
                for d in my_eff
                if stab_coverage(p, d) >= 2
            ]
            for p in opp_eff
        },
    }


def print_analysis(my_names, opp_names):
    r = solve_preview(my_names, opp_names)
    W = 60

    print(f"\n{'='*W}")
    print(f"  TEAM PREVIEW ANALYSIS")
    print(f"{'='*W}")
    print(f"  Your team : {', '.join(my_names)}")
    print(f"  Opp team  : {', '.join(opp_names)}")

    # Mega
    if r["my_megas"] or r["opp_megas"]:
        print(f"\n--- MEGA ---")
        if r["my_megas"]:
            pct, base, form, stone = r["my_megas"][0]
            alts = [f[1] for f in r["my_megas"][1:] if f[0] >= 20]
            alt_str = f"  (alt: {', '.join(alts)})" if alts else ""
            print(f"  You : {base} -> {form}  {stone} {pct}%{alt_str}")
        if r["opp_megas"]:
            pct, base, form, stone = r["opp_megas"][0]
            alts = [f[1] for f in r["opp_megas"][1:] if f[0] >= 20]
            alt_str = f"  (alt: {', '.join(alts)})" if alts else ""
            print(f"  Opp : {base} -> {form}  {stone} {pct}%{alt_str}")

    # Weather
    if r["opp_weather_setters"]:
        weather_names = ", ".join(f"{n} ({w})" for n, w in r["opp_weather_setters"])
        print(f"\n--- WEATHER ---")
        print(f"  Opp sets    : {weather_names}")
        if r["my_weather_counters"]:
            counter_names = ", ".join(n for n, _ in r["my_weather_counters"])
            print(f"  Your counter: {counter_names}  [bring to deny weather]")
        else:
            print(f"  Your counter: (none)")
        if r["wx_back_threats"]:
            print(f"  Back threats (can re-set weather after your counter):")
            for name, desc, label in r["wx_back_threats"]:
                print(f"    {name:<20} {desc}  [{label}]")

    # Roles + speed
    print(f"\n--- OPPONENT ROLES & SPEED ---")
    for name in opp_names:
        roles    = r["roles"].get(name, [])
        arch     = r["archetypes"].get(name, "damage")
        spe      = r["speed_tiers"].get(name, "?")
        role_str = ", ".join(roles) if roles else "-"
        print(f"  {name:<24} spe {str(spe):<7} {arch.upper():<8} [{role_str}]")

    # Threats
    print(f"\n--- OPPONENT THREATS TO YOUR TEAM ---")
    any_threat = False
    for name, threats in r["threats"].items():
        if threats:
            print(f"  {name:<24} {', '.join(threats)}")
            any_threat = True
    if not any_threat:
        print("  (none)")

    # My bring options
    print(f"\n--- YOUR BRING-4 OPTIONS  (expected score vs all 15 opp combos) ---")
    for i, (s, names) in enumerate(r["my_brings"], 1):
        tag = "  <-- BEST" if i == 1 else ""
        print(f"  #{i}  {' / '.join(names):<52} {s:+.2f}{tag}")

    # Opp bring options
    print(f"\n--- OPP LIKELY BRING-4 OPTIONS  (by synergy + usage weight) ---")
    for i, (w, names) in enumerate(r["opp_brings"], 1):
        tag = "  <-- PREDICTED" if i == 1 else ""
        print(f"  #{i}  {' / '.join(names):<52} w={w:.1f}{tag}")

    # Lead analysis
    print(f"\n--- LEAD ANALYSIS ---")
    print(f"  Your best bring : {' / '.join(r['my_best_bring'])}")
    print(f"  Opp likely bring: {' / '.join(r['pred_opp_bring'])}")

    print(f"\n  Your lead options (vs predicted opp bring):")
    for i, (s, n1, n2, back) in enumerate(r["my_leads"], 1):
        print(f"    #{i}  {n1} + {n2:<22}  back: {' / '.join(back)}")

    print(f"\n  Opp likely leads:")
    for i, (s, n1, n2, back) in enumerate(r["opp_leads"], 1):
        print(f"    #{i}  {n1} + {n2:<22}  back: {' / '.join(back)}")

    print(f"\n  Counter-lead for every opp lead:")
    for opp_lead, (s, n1, n2, back) in r["counter_leads"].items():
        print(f"    vs {opp_lead:<34} -> {n1} + {n2}  back: {' / '.join(back)}")

    print()


# ---------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    MY_TEAM  = ["Charizard", "Basculegion Male", "Kingambit", "Aerodactyl", "Garchomp", "Sylveon"]
    OPP_TEAM = ["Raichu", "Milotic", "Ceruledge", "Incineroar", "Floette", "Sinistcha"]
    print_analysis(MY_TEAM, OPP_TEAM)
