"""
Pokemon Champions — Data Layer
Each champion has:
  - moves: up to 10 competitively-run moves with name + type
  - niche_threat: one rare/tech move the opponent might surprise you with
  - roles: tags used for lead-probability scoring (fake_out, tailwind, etc.)
  - tier_singles / tier_doubles
  - type matchups (computed)
"""

import json

ALL_TYPES = ["Normal","Fire","Water","Electric","Grass","Ice","Fighting","Poison",
             "Ground","Flying","Psychic","Bug","Rock","Ghost","Dragon","Dark","Steel","Fairy"]

DEF = {
    "Normal":   {"weak":["Fighting"],"immune":["Ghost"],"resist":[]},
    "Fire":     {"weak":["Water","Ground","Rock"],"immune":[],"resist":["Fire","Grass","Ice","Bug","Steel","Fairy"]},
    "Water":    {"weak":["Electric","Grass"],"immune":[],"resist":["Fire","Water","Ice","Steel"]},
    "Electric": {"weak":["Ground"],"immune":[],"resist":["Electric","Flying","Steel"]},
    "Grass":    {"weak":["Fire","Ice","Poison","Flying","Bug"],"immune":[],"resist":["Water","Electric","Grass","Ground"]},
    "Ice":      {"weak":["Fire","Fighting","Rock","Steel"],"immune":[],"resist":["Ice"]},
    "Fighting": {"weak":["Flying","Psychic","Fairy"],"immune":[],"resist":["Bug","Rock","Dark"]},
    "Poison":   {"weak":["Ground","Psychic"],"immune":[],"resist":["Grass","Fighting","Poison","Bug","Fairy"]},
    "Ground":   {"weak":["Water","Grass","Ice"],"immune":["Electric"],"resist":["Poison","Rock"]},
    "Flying":   {"weak":["Electric","Ice","Rock"],"immune":["Ground"],"resist":["Grass","Fighting","Bug"]},
    "Psychic":  {"weak":["Bug","Ghost","Dark"],"immune":[],"resist":["Fighting","Psychic"]},
    "Bug":      {"weak":["Fire","Flying","Rock"],"immune":[],"resist":["Grass","Fighting","Ground"]},
    "Rock":     {"weak":["Water","Grass","Fighting","Ground","Steel"],"immune":[],"resist":["Normal","Fire","Poison","Flying"]},
    "Ghost":    {"weak":["Ghost","Dark"],"immune":["Normal","Fighting"],"resist":["Poison","Bug"]},
    "Dragon":   {"weak":["Ice","Dragon","Fairy"],"immune":[],"resist":["Fire","Water","Electric","Grass"]},
    "Dark":     {"weak":["Fighting","Bug","Fairy"],"immune":["Psychic"],"resist":["Ghost","Dark"]},
    "Steel":    {"weak":["Fire","Fighting","Ground"],"immune":["Poison"],"resist":["Normal","Grass","Ice","Flying","Psychic","Bug","Rock","Dragon","Steel","Fairy"]},
    "Fairy":    {"weak":["Poison","Steel"],"immune":["Dragon"],"resist":["Fighting","Bug","Dark"]},
}


def compute_matchups(types):
    m = {t: 1.0 for t in ALL_TYPES}
    for ptype in types:
        if ptype not in DEF:
            continue
        for t in DEF[ptype]["weak"]:   m[t] *= 2
        for t in DEF[ptype]["resist"]: m[t] *= 0.5
        for t in DEF[ptype]["immune"]: m[t]  = 0
    return {
        "weak4x":  [t for t in ALL_TYPES if m[t] == 4],
        "weak2x":  [t for t in ALL_TYPES if m[t] == 2],
        "resist":  [t for t in ALL_TYPES if 0 < m[t] < 1],
        "immune":  [t for t in ALL_TYPES if m[t] == 0],
    }


# ── Master Roster ─────────────────────────────────────────────────────────────
# roles: tags used for lead prediction
#   fake_out          → almost always leads (priority disruption)
#   intimidate        → leads to weaken physical attackers
#   tailwind          → speed control lead
#   trick_room        → TR setter lead
#   weather_setter    → rain/sun/sand setter (almost always leads)
#   redirection       → Follow Me / Rage Powder support
#   hazard_setter     → Stealth Rock / Spikes
#   sweeper           → pure damage dealer, rarely leads
#   pivot             → flexible, mid-game entry

ROSTER = [
    # ─ S Tier ────────────────────────────────────────────────────────────────
    {
        "name": "Incineroar", "dex_id": 727,
        "types": ["Fire","Dark"], "pokeapi_slug": "incineroar",
        "game8_id": 592493, "tier_singles": "S", "tier_doubles": "S",
        "roles": ["fake_out","intimidate","pivot"],
        "moves": [
            {"name": "Fake Out",       "type": "Normal"},
            {"name": "Flare Blitz",    "type": "Fire"},
            {"name": "Knock Off",      "type": "Dark"},
            {"name": "Close Combat",   "type": "Fighting"},
            {"name": "Darkest Lariat", "type": "Dark"},
            {"name": "Parting Shot",   "type": "Dark"},
            {"name": "Snarl",          "type": "Dark"},
            {"name": "Body Press",     "type": "Fighting"},
            {"name": "Will-O-Wisp",    "type": "Fire"},
            {"name": "U-turn",         "type": "Bug"},
        ],
        "niche_threat": {"move": "Earthquake", "type": "Ground",
                         "note": "Rare tech vs Poison/Steel opponents"},
    },
    {
        "name": "Kingambit", "dex_id": 983,
        "types": ["Dark","Steel"], "pokeapi_slug": "kingambit",
        "game8_id": 594120, "tier_singles": "S", "tier_doubles": "A+",
        "roles": ["sweeper"],
        "moves": [
            {"name": "Kowtow Cleave",  "type": "Dark"},
            {"name": "Iron Head",      "type": "Steel"},
            {"name": "Sucker Punch",   "type": "Dark"},
            {"name": "Low Kick",       "type": "Fighting"},
            {"name": "Swords Dance",   "type": "Normal"},
            {"name": "Thunder Wave",   "type": "Electric"},
            {"name": "Brick Break",    "type": "Fighting"},
            {"name": "Night Slash",    "type": "Dark"},
            {"name": "Sacred Sword",   "type": "Fighting"},
            {"name": "Laser Focus",    "type": "Normal"},
        ],
        "niche_threat": {"move": "Taunt", "type": "Dark",
                         "note": "Shuts down Trick Room and status moves"},
    },
    {
        "name": "Eternal Flower Floette", "dex_id": 670,
        "types": ["Fairy"], "pokeapi_slug": "floette",
        "game8_id": 593395, "tier_singles": "S", "tier_doubles": "S",
        "roles": ["sweeper","redirection"],
        "moves": [
            {"name": "Moonblast",      "type": "Fairy"},
            {"name": "Draining Kiss",  "type": "Fairy"},
            {"name": "Psychic",        "type": "Psychic"},
            {"name": "Calm Mind",      "type": "Psychic"},
            {"name": "Light Screen",   "type": "Psychic"},
            {"name": "Aromatherapy",   "type": "Grass"},
            {"name": "Misty Terrain",  "type": "Fairy"},
            {"name": "Protect",        "type": "Normal"},
            {"name": "Moonlight",      "type": "Fairy"},
            {"name": "Dazzling Gleam", "type": "Fairy"},
        ],
        "niche_threat": {"move": "Shadow Ball", "type": "Ghost",
                         "note": "Covers Steel types that wall Fairy moves"},
    },
    {
        "name": "Delphox", "dex_id": 655,
        "types": ["Fire","Psychic"], "pokeapi_slug": "delphox",
        "game8_id": 593808, "tier_singles": "S", "tier_doubles": "S",
        "roles": ["sweeper"],
        "moves": [
            {"name": "Fire Blast",     "type": "Fire"},
            {"name": "Psychic",        "type": "Psychic"},
            {"name": "Psyshock",       "type": "Psychic"},
            {"name": "Shadow Ball",    "type": "Ghost"},
            {"name": "Calm Mind",      "type": "Psychic"},
            {"name": "Mystical Fire",  "type": "Fire"},
            {"name": "Will-O-Wisp",    "type": "Fire"},
            {"name": "Dazzling Gleam", "type": "Fairy"},
            {"name": "Trick",          "type": "Psychic"},
            {"name": "Overheat",       "type": "Fire"},
        ],
        "niche_threat": {"move": "Dark Pulse", "type": "Dark",
                         "note": "Mirrors opposing Psychic/Ghost types"},
    },
    {
        "name": "Sneasler", "dex_id": 903,
        "types": ["Poison","Fighting"], "pokeapi_slug": "sneasler",
        "game8_id": 593918, "tier_singles": "S", "tier_doubles": "A+",
        "roles": ["sweeper","fake_out"],
        "moves": [
            {"name": "Close Combat",   "type": "Fighting"},
            {"name": "Poison Jab",     "type": "Poison"},
            {"name": "Dire Claw",      "type": "Poison"},
            {"name": "Shadow Claw",    "type": "Ghost"},
            {"name": "Swords Dance",   "type": "Normal"},
            {"name": "Throat Chop",    "type": "Dark"},
            {"name": "Ice Punch",      "type": "Ice"},
            {"name": "Acrobatics",     "type": "Flying"},
            {"name": "Fake Out",       "type": "Normal"},
            {"name": "U-turn",         "type": "Bug"},
        ],
        "niche_threat": {"move": "Rock Slide", "type": "Rock",
                         "note": "Surprise coverage vs Flying types"},
    },
    # ─ A Tier (with game8 IDs) ────────────────────────────────────────────────
    {
        "name": "Whimsicott", "dex_id": 547,
        "types": ["Grass","Fairy"], "pokeapi_slug": "whimsicott",
        "game8_id": 593176, "tier_singles": "A", "tier_doubles": "A",
        "roles": ["tailwind","pivot"],
        "moves": [
            {"name": "Moonblast",      "type": "Fairy"},
            {"name": "Tailwind",       "type": "Flying"},
            {"name": "Encore",         "type": "Normal"},
            {"name": "Stun Spore",     "type": "Grass"},
            {"name": "Dazzling Gleam", "type": "Fairy"},
            {"name": "Grass Knot",     "type": "Grass"},
            {"name": "U-turn",         "type": "Bug"},
            {"name": "Leech Seed",     "type": "Grass"},
            {"name": "Charm",          "type": "Fairy"},
            {"name": "Hurricane",      "type": "Flying"},
        ],
        "niche_threat": {"move": "Memento", "type": "Dark",
                         "note": "Sacrificial play to heavily debuff the opponent"},
    },
    {
        "name": "Greninja", "dex_id": 658,
        "types": ["Water","Dark"], "pokeapi_slug": "greninja",
        "game8_id": 593885, "tier_singles": "A+", "tier_doubles": "A+",
        "roles": ["sweeper","hazard_setter"],
        "moves": [
            {"name": "Surf",           "type": "Water"},
            {"name": "Dark Pulse",     "type": "Dark"},
            {"name": "Ice Beam",       "type": "Ice"},
            {"name": "U-turn",         "type": "Bug"},
            {"name": "Water Shuriken", "type": "Water"},
            {"name": "Night Slash",    "type": "Dark"},
            {"name": "Spikes",         "type": "Ground"},
            {"name": "Toxic Spikes",   "type": "Poison"},
            {"name": "Extrasensory",   "type": "Psychic"},
            {"name": "Flip Turn",      "type": "Water"},
        ],
        "niche_threat": {"move": "Gunk Shot", "type": "Poison",
                         "note": "Catches Fairy types off guard"},
    },
    {
        "name": "Meowscarada", "dex_id": 908,
        "types": ["Grass","Dark"], "pokeapi_slug": "meowscarada",
        "game8_id": 594015, "tier_singles": "A+", "tier_doubles": "A+",
        "roles": ["sweeper","hazard_setter"],
        "moves": [
            {"name": "Flower Trick",   "type": "Grass"},
            {"name": "Knock Off",      "type": "Dark"},
            {"name": "U-turn",         "type": "Bug"},
            {"name": "Low Kick",       "type": "Fighting"},
            {"name": "Play Rough",     "type": "Fairy"},
            {"name": "Shadow Sneak",   "type": "Ghost"},
            {"name": "Leaf Storm",     "type": "Grass"},
            {"name": "Spikes",         "type": "Ground"},
            {"name": "Toxic Spikes",   "type": "Poison"},
            {"name": "Nasty Plot",     "type": "Dark"},
        ],
        "niche_threat": {"move": "Poison Jab", "type": "Poison",
                         "note": "Specifically to handle Fairy types"},
    },
    # ─ A+ Tier ───────────────────────────────────────────────────────────────
    {
        "name": "Garchomp", "dex_id": 445,
        "types": ["Dragon","Ground"], "pokeapi_slug": "garchomp",
        "game8_id": 593731, "tier_singles": "A+", "tier_doubles": "A+",
        "roles": ["sweeper"],
        "moves": [
            {"name": "Earthquake",       "type": "Ground"},
            {"name": "Dragon Claw",      "type": "Dragon"},
            {"name": "Scale Shot",       "type": "Dragon"},
            {"name": "Iron Head",        "type": "Steel"},
            {"name": "Poison Jab",       "type": "Poison"},
            {"name": "Swords Dance",     "type": "Normal"},
            {"name": "Rock Slide",       "type": "Rock"},
            {"name": "Fire Fang",        "type": "Fire"},
            {"name": "Stomping Tantrum", "type": "Ground"},
            {"name": "Outrage",          "type": "Dragon"},
        ],
        "niche_threat": {"move": "Stone Edge", "type": "Rock",
                         "note": "Hard counter to Flying types"},
    },
    {
        "name": "Sinistcha", "dex_id": 1004,
        "types": ["Grass","Ghost"], "pokeapi_slug": "sinistcha",
        "game8_id": 593735, "tier_singles": "A+", "tier_doubles": "A+",
        "roles": ["sweeper","pivot"],
        "moves": [
            {"name": "Shadow Ball",    "type": "Ghost"},
            {"name": "Matcha Gotcha",  "type": "Grass"},
            {"name": "Giga Drain",     "type": "Grass"},
            {"name": "Calm Mind",      "type": "Psychic"},
            {"name": "Strength Sap",   "type": "Grass"},
            {"name": "Will-O-Wisp",    "type": "Fire"},
            {"name": "Energy Ball",    "type": "Grass"},
            {"name": "Hex",            "type": "Ghost"},
            {"name": "Dazzling Gleam", "type": "Fairy"},
            {"name": "Nasty Plot",     "type": "Dark"},
        ],
        "niche_threat": {"move": "Psychic", "type": "Psychic",
                         "note": "Hits Fighting and Poison types that resist Grass"},
    },
    {
        "name": "Tyranitar", "dex_id": 248,
        "types": ["Rock","Dark"], "pokeapi_slug": "tyranitar",
        "game8_id": 593895, "tier_singles": "A+", "tier_doubles": "A+",
        "roles": ["sweeper","weather_setter"],
        "moves": [
            {"name": "Stone Edge",     "type": "Rock"},
            {"name": "Crunch",         "type": "Dark"},
            {"name": "Earthquake",     "type": "Ground"},
            {"name": "Ice Punch",      "type": "Ice"},
            {"name": "Dragon Dance",   "type": "Dragon"},
            {"name": "Fire Punch",     "type": "Fire"},
            {"name": "Stealth Rock",   "type": "Rock"},
            {"name": "Thunder Wave",   "type": "Electric"},
            {"name": "Low Kick",       "type": "Fighting"},
            {"name": "Rock Blast",     "type": "Rock"},
        ],
        "niche_threat": {"move": "Superpower", "type": "Fighting",
                         "note": "Punishes Steel types expecting a free switch"},
    },
    {
        "name": "Wash Rotom", "dex_id": 479,
        "types": ["Electric","Water"], "pokeapi_slug": "rotom-wash",
        "game8_id": 593994, "tier_singles": "A+", "tier_doubles": "A",
        "roles": ["pivot","sweeper"],
        "moves": [
            {"name": "Thunderbolt",    "type": "Electric"},
            {"name": "Hydro Pump",     "type": "Water"},
            {"name": "Volt Switch",    "type": "Electric"},
            {"name": "Will-O-Wisp",    "type": "Fire"},
            {"name": "Thunder Wave",   "type": "Electric"},
            {"name": "Shadow Ball",    "type": "Ghost"},
            {"name": "Pain Split",     "type": "Normal"},
            {"name": "Discharge",      "type": "Electric"},
            {"name": "Trick",          "type": "Psychic"},
            {"name": "Nasty Plot",     "type": "Dark"},
        ],
        "niche_threat": {"move": "Blizzard", "type": "Ice",
                         "note": "Grass/Dragon coverage in hail teams"},
    },
    {
        "name": "Frost Rotom", "dex_id": 479,
        "types": ["Electric","Ice"], "pokeapi_slug": "rotom-frost",
        "game8_id": 594148, "tier_singles": "A", "tier_doubles": "A",
        "roles": ["sweeper","pivot"],
        "moves": [
            {"name": "Blizzard",       "type": "Ice"},
            {"name": "Thunderbolt",    "type": "Electric"},
            {"name": "Volt Switch",    "type": "Electric"},
            {"name": "Will-O-Wisp",    "type": "Fire"},
            {"name": "Thunder Wave",   "type": "Electric"},
            {"name": "Shadow Ball",    "type": "Ghost"},
            {"name": "Discharge",      "type": "Electric"},
            {"name": "Trick",          "type": "Psychic"},
            {"name": "Nasty Plot",     "type": "Dark"},
            {"name": "Pain Split",     "type": "Normal"},
        ],
        "niche_threat": {"move": "Hydro Pump", "type": "Water",
                         "note": "Fire/Rock coverage that opponents won't expect"},
    },
    {
        "name": "Dragonite", "dex_id": 149,
        "types": ["Dragon","Flying"], "pokeapi_slug": "dragonite",
        "game8_id": 593969, "tier_singles": "A+", "tier_doubles": "A+",
        "roles": ["sweeper"],
        "moves": [
            {"name": "Extreme Speed",  "type": "Normal"},
            {"name": "Dragon Dance",   "type": "Dragon"},
            {"name": "Earthquake",     "type": "Ground"},
            {"name": "Thunder Punch",  "type": "Electric"},
            {"name": "Fire Punch",     "type": "Fire"},
            {"name": "Ice Punch",      "type": "Ice"},
            {"name": "Outrage",        "type": "Dragon"},
            {"name": "Dragon Claw",    "type": "Dragon"},
            {"name": "Dual Wingbeat",  "type": "Flying"},
            {"name": "Aqua Tail",      "type": "Water"},
        ],
        "niche_threat": {"move": "Superpower", "type": "Fighting",
                         "note": "Punishes Steel types that switch in to wall Dragon moves"},
    },
    {
        "name": "Archaludon", "dex_id": 1018,
        "types": ["Steel","Dragon"], "pokeapi_slug": "archaludon",
        "game8_id": 593940, "tier_singles": "A+", "tier_doubles": "A",
        "roles": ["sweeper"],
        "moves": [
            {"name": "Flash Cannon",   "type": "Steel"},
            {"name": "Dragon Pulse",   "type": "Dragon"},
            {"name": "Electro Shot",   "type": "Electric"},
            {"name": "Body Press",     "type": "Fighting"},
            {"name": "Thunder Wave",   "type": "Electric"},
            {"name": "Draco Meteor",   "type": "Dragon"},
            {"name": "Iron Defense",   "type": "Steel"},
            {"name": "Dragon Dance",   "type": "Dragon"},
            {"name": "Thunderbolt",    "type": "Electric"},
            {"name": "Snarl",          "type": "Dark"},
        ],
        "niche_threat": {"move": "Ice Beam", "type": "Ice",
                         "note": "Hits Dragon/Ground types that expect to switch in safely"},
    },
    {
        "name": "Excadrill", "dex_id": 530,
        "types": ["Ground","Steel"], "pokeapi_slug": "excadrill",
        "game8_id": 594060, "tier_singles": "A+", "tier_doubles": "A+",
        "roles": ["sweeper","weather_setter"],
        "moves": [
            {"name": "Earthquake",     "type": "Ground"},
            {"name": "Iron Head",      "type": "Steel"},
            {"name": "Rock Slide",     "type": "Rock"},
            {"name": "Swords Dance",   "type": "Normal"},
            {"name": "Rapid Spin",     "type": "Normal"},
            {"name": "Shadow Claw",    "type": "Ghost"},
            {"name": "X-Scissor",      "type": "Bug"},
            {"name": "Stealth Rock",   "type": "Rock"},
            {"name": "Drill Run",      "type": "Ground"},
            {"name": "Body Press",     "type": "Fighting"},
        ],
        "niche_threat": {"move": "Rock Tomb", "type": "Rock",
                         "note": "Speed control vs Flying types"},
    },
    {
        "name": "Basculegion", "dex_id": 902,
        "types": ["Water","Ghost"], "pokeapi_slug": "basculegion",
        "game8_id": 594126, "tier_singles": "A+", "tier_doubles": "A+",
        "roles": ["sweeper"],
        "moves": [
            {"name": "Wave Crash",     "type": "Water"},
            {"name": "Last Respects",  "type": "Ghost"},
            {"name": "Shadow Ball",    "type": "Ghost"},
            {"name": "Aqua Jet",       "type": "Water"},
            {"name": "Ice Beam",       "type": "Ice"},
            {"name": "Flip Turn",      "type": "Water"},
            {"name": "Liquidation",    "type": "Water"},
            {"name": "Agility",        "type": "Psychic"},
            {"name": "Crabhammer",     "type": "Water"},
            {"name": "Curse",          "type": "Ghost"},
        ],
        "niche_threat": {"move": "Thunder", "type": "Electric",
                         "note": "Mirror coverage vs opposing Water types"},
    },
    {
        "name": "Hawlucha", "dex_id": 701,
        "types": ["Fighting","Flying"], "pokeapi_slug": "hawlucha",
        "game8_id": 593736, "tier_singles": "A+", "tier_doubles": "A+",
        "roles": ["sweeper"],
        "moves": [
            {"name": "Close Combat",   "type": "Fighting"},
            {"name": "Acrobatics",     "type": "Flying"},
            {"name": "High Jump Kick", "type": "Fighting"},
            {"name": "Sky Attack",     "type": "Flying"},
            {"name": "Swords Dance",   "type": "Normal"},
            {"name": "Thunder Punch",  "type": "Electric"},
            {"name": "Bounce",         "type": "Flying"},
            {"name": "Stone Edge",     "type": "Rock"},
            {"name": "Substitute",     "type": "Normal"},
            {"name": "Roost",          "type": "Flying"},
        ],
        "niche_threat": {"move": "Poison Jab", "type": "Poison",
                         "note": "Fairy coverage that's rarely expected"},
    },
    {
        "name": "Dragapult", "dex_id": 887,
        "types": ["Dragon","Ghost"], "pokeapi_slug": "dragapult",
        "game8_id": 594062, "tier_singles": "A+", "tier_doubles": "A+",
        "roles": ["sweeper","pivot"],
        "moves": [
            {"name": "Shadow Ball",    "type": "Ghost"},
            {"name": "Dragon Darts",   "type": "Dragon"},
            {"name": "Dragon Pulse",   "type": "Dragon"},
            {"name": "U-turn",         "type": "Bug"},
            {"name": "Will-O-Wisp",    "type": "Fire"},
            {"name": "Thunderbolt",    "type": "Electric"},
            {"name": "Fire Blast",     "type": "Fire"},
            {"name": "Draco Meteor",   "type": "Dragon"},
            {"name": "Thunder Wave",   "type": "Electric"},
            {"name": "Phantom Force",  "type": "Ghost"},
        ],
        "niche_threat": {"move": "Surf", "type": "Water",
                         "note": "Hits Fire/Ground switch-ins that expect Dragon moves"},
    },
    {
        "name": "Charizard", "dex_id": 6,
        "types": ["Fire","Flying"], "pokeapi_slug": "charizard",
        "game8_id": 593744, "tier_singles": "A+", "tier_doubles": "A+",
        "roles": ["sweeper","weather_setter"],
        "moves": [
            {"name": "Flamethrower",   "type": "Fire"},
            {"name": "Air Slash",      "type": "Flying"},
            {"name": "Dragon Pulse",   "type": "Dragon"},
            {"name": "Focus Blast",    "type": "Fighting"},
            {"name": "Solar Beam",     "type": "Grass"},
            {"name": "Roost",          "type": "Flying"},
            {"name": "Will-O-Wisp",    "type": "Fire"},
            {"name": "Overheat",       "type": "Fire"},
            {"name": "Hurricane",      "type": "Flying"},
            {"name": "Fly",            "type": "Flying"},
        ],
        "niche_threat": {"move": "Ancient Power", "type": "Rock",
                         "note": "Occasionally used vs opposing Fire/Flying mirrors"},
    },
    {
        "name": "Gengar", "dex_id": 94,
        "types": ["Ghost","Poison"], "pokeapi_slug": "gengar",
        "game8_id": 593811, "tier_singles": "A+", "tier_doubles": "A+",
        "roles": ["sweeper"],
        "moves": [
            {"name": "Shadow Ball",    "type": "Ghost"},
            {"name": "Sludge Bomb",    "type": "Poison"},
            {"name": "Focus Blast",    "type": "Fighting"},
            {"name": "Thunderbolt",    "type": "Electric"},
            {"name": "Nasty Plot",     "type": "Dark"},
            {"name": "Dazzling Gleam", "type": "Fairy"},
            {"name": "Dark Pulse",     "type": "Dark"},
            {"name": "Will-O-Wisp",    "type": "Fire"},
            {"name": "Hex",            "type": "Ghost"},
            {"name": "Destiny Bond",   "type": "Ghost"},
        ],
        "niche_threat": {"move": "Energy Ball", "type": "Grass",
                         "note": "Water/Ground coverage, unexpected from Gengar"},
    },
    # ─ A Tier ────────────────────────────────────────────────────────────────
    {
        "name": "Pelipper", "dex_id": 279,
        "types": ["Water","Flying"], "pokeapi_slug": "pelipper",
        "game8_id": 593930, "tier_singles": "A", "tier_doubles": "A",
        "roles": ["weather_setter","pivot","tailwind"],
        "moves": [
            {"name": "Scald",          "type": "Water"},
            {"name": "Hurricane",      "type": "Flying"},
            {"name": "U-turn",         "type": "Bug"},
            {"name": "Tailwind",       "type": "Flying"},
            {"name": "Roost",          "type": "Flying"},
            {"name": "Rain Dance",     "type": "Water"},
            {"name": "Ice Beam",       "type": "Ice"},
            {"name": "Knock Off",      "type": "Dark"},
            {"name": "Wide Guard",     "type": "Fighting"},
            {"name": "Hydro Pump",     "type": "Water"},
        ],
        "niche_threat": {"move": "Grass Knot", "type": "Grass",
                         "note": "Punishes opposing Water types that expect a free switch"},
    },
    {
        "name": "Hatterene", "dex_id": 858,
        "types": ["Psychic","Fairy"], "pokeapi_slug": "hatterene",
        "game8_id": 593899, "tier_singles": "A", "tier_doubles": "A",
        "roles": ["trick_room","sweeper"],
        "moves": [
            {"name": "Psychic",        "type": "Psychic"},
            {"name": "Moonblast",      "type": "Fairy"},
            {"name": "Mystical Fire",  "type": "Fire"},
            {"name": "Calm Mind",      "type": "Psychic"},
            {"name": "Trick Room",     "type": "Psychic"},
            {"name": "Thunder Wave",   "type": "Electric"},
            {"name": "Dazzling Gleam", "type": "Fairy"},
            {"name": "Healing Wish",   "type": "Psychic"},
            {"name": "Nuzzle",         "type": "Electric"},
            {"name": "Psyshock",       "type": "Psychic"},
        ],
        "niche_threat": {"move": "Shadow Ball", "type": "Ghost",
                         "note": "Hits opposing Psychic types in the mirror"},
    },
    {
        "name": "Primarina", "dex_id": 730,
        "types": ["Water","Fairy"], "pokeapi_slug": "primarina",
        "game8_id": 594011, "tier_singles": "A", "tier_doubles": "A",
        "roles": ["sweeper"],
        "moves": [
            {"name": "Moonblast",      "type": "Fairy"},
            {"name": "Sparkling Aria", "type": "Water"},
            {"name": "Surf",           "type": "Water"},
            {"name": "Ice Beam",       "type": "Ice"},
            {"name": "Calm Mind",      "type": "Psychic"},
            {"name": "Dazzling Gleam", "type": "Fairy"},
            {"name": "Psychic",        "type": "Psychic"},
            {"name": "Encore",         "type": "Normal"},
            {"name": "Hyper Voice",    "type": "Normal"},
            {"name": "Perish Song",    "type": "Normal"},
        ],
        "niche_threat": {"move": "Energy Ball", "type": "Grass",
                         "note": "Punishes Water/Ground types in the mirror"},
    },
    {
        "name": "Palafin", "dex_id": 964,
        "types": ["Water"], "pokeapi_slug": "palafin",
        "game8_id": 594132, "tier_singles": "A", "tier_doubles": "A",
        "roles": ["sweeper"],
        "moves": [
            {"name": "Jet Punch",      "type": "Water"},
            {"name": "Wave Crash",     "type": "Water"},
            {"name": "Close Combat",   "type": "Fighting"},
            {"name": "Ice Punch",      "type": "Ice"},
            {"name": "Liquidation",    "type": "Water"},
            {"name": "Bulk Up",        "type": "Fighting"},
            {"name": "Drain Punch",    "type": "Fighting"},
            {"name": "Aqua Jet",       "type": "Water"},
            {"name": "Flip Turn",      "type": "Water"},
            {"name": "Double-Edge",    "type": "Normal"},
        ],
        "niche_threat": {"move": "Thunder Punch", "type": "Electric",
                         "note": "Mirror match coverage vs opposing Water types"},
    },
    {
        "name": "Weavile", "dex_id": 461,
        "types": ["Dark","Ice"], "pokeapi_slug": "weavile",
        "game8_id": 594142, "tier_singles": "A", "tier_doubles": "A",
        "roles": ["sweeper","fake_out"],
        "moves": [
            {"name": "Icicle Crash",   "type": "Ice"},
            {"name": "Knock Off",      "type": "Dark"},
            {"name": "Low Kick",       "type": "Fighting"},
            {"name": "Triple Axel",    "type": "Ice"},
            {"name": "Ice Shard",      "type": "Ice"},
            {"name": "Night Slash",    "type": "Dark"},
            {"name": "Poison Jab",     "type": "Poison"},
            {"name": "Throat Chop",    "type": "Dark"},
            {"name": "Swords Dance",   "type": "Normal"},
            {"name": "Fake Out",       "type": "Normal"},
        ],
        "niche_threat": {"move": "Rock Slide", "type": "Rock",
                         "note": "Fire/Flying coverage that catches people off guard"},
    },
    {
        "name": "Hippowdon", "dex_id": 450,
        "types": ["Ground"], "pokeapi_slug": "hippowdon",
        "game8_id": 594071, "tier_singles": "A", "tier_doubles": "A",
        "roles": ["weather_setter","pivot"],
        "moves": [
            {"name": "Earthquake",     "type": "Ground"},
            {"name": "Stealth Rock",   "type": "Rock"},
            {"name": "Slack Off",      "type": "Normal"},
            {"name": "Whirlwind",      "type": "Flying"},
            {"name": "Stone Edge",     "type": "Rock"},
            {"name": "Ice Fang",       "type": "Ice"},
            {"name": "Toxic",          "type": "Poison"},
            {"name": "Heavy Slam",     "type": "Steel"},
            {"name": "Yawn",           "type": "Normal"},
            {"name": "Body Press",     "type": "Fighting"},
        ],
        "niche_threat": {"move": "Rock Blast", "type": "Rock",
                         "note": "Breaks substitutes and hits Flying/Ice types"},
    },
    {
        "name": "Glimmora", "dex_id": 970,
        "types": ["Rock","Poison"], "pokeapi_slug": "glimmora",
        "game8_id": 594130, "tier_singles": "A", "tier_doubles": "A",
        "roles": ["hazard_setter","sweeper"],
        "moves": [
            {"name": "Power Gem",      "type": "Rock"},
            {"name": "Sludge Wave",    "type": "Poison"},
            {"name": "Mortal Spin",    "type": "Poison"},
            {"name": "Stealth Rock",   "type": "Rock"},
            {"name": "Toxic Spikes",   "type": "Poison"},
            {"name": "Energy Ball",    "type": "Grass"},
            {"name": "Earth Power",    "type": "Ground"},
            {"name": "Spikes",         "type": "Ground"},
            {"name": "Shadow Ball",    "type": "Ghost"},
            {"name": "Rock Blast",     "type": "Rock"},
        ],
        "niche_threat": {"move": "Flash Cannon", "type": "Steel",
                         "note": "Fairy/Ice coverage that resists Poison"},
    },
    {
        "name": "Froslass", "dex_id": 478,
        "types": ["Ice","Ghost"], "pokeapi_slug": "froslass",
        "game8_id": 593896, "tier_singles": "A", "tier_doubles": "A",
        "roles": ["hazard_setter","pivot"],
        "moves": [
            {"name": "Blizzard",       "type": "Ice"},
            {"name": "Shadow Ball",    "type": "Ghost"},
            {"name": "Spikes",         "type": "Ground"},
            {"name": "Destiny Bond",   "type": "Ghost"},
            {"name": "Will-O-Wisp",    "type": "Fire"},
            {"name": "Thunder Wave",   "type": "Electric"},
            {"name": "Ice Beam",       "type": "Ice"},
            {"name": "Hex",            "type": "Ghost"},
            {"name": "Icy Wind",       "type": "Ice"},
            {"name": "Calm Mind",      "type": "Psychic"},
        ],
        "niche_threat": {"move": "Dark Pulse", "type": "Dark",
                         "note": "Opposing Ghost/Psychic mirror coverage"},
    },
    {
        "name": "Venusaur", "dex_id": 3,
        "types": ["Grass","Poison"], "pokeapi_slug": "venusaur",
        "game8_id": 594153, "tier_singles": "A", "tier_doubles": "A",
        "roles": ["weather_setter","sweeper"],
        "moves": [
            {"name": "Sludge Bomb",    "type": "Poison"},
            {"name": "Giga Drain",     "type": "Grass"},
            {"name": "Earthquake",     "type": "Ground"},
            {"name": "Sleep Powder",   "type": "Grass"},
            {"name": "Leech Seed",     "type": "Grass"},
            {"name": "Synthesis",      "type": "Grass"},
            {"name": "Body Press",     "type": "Fighting"},
            {"name": "Knock Off",      "type": "Dark"},
            {"name": "Toxic",          "type": "Poison"},
            {"name": "Growth",         "type": "Normal"},
        ],
        "niche_threat": {"move": "Rock Slide", "type": "Rock",
                         "note": "Punishes opposing Fire types that switch in"},
    },
    {
        "name": "Starmie", "dex_id": 121,
        "types": ["Water","Psychic"], "pokeapi_slug": "starmie",
        "game8_id": 593819, "tier_singles": "A", "tier_doubles": "A",
        "roles": ["sweeper","pivot"],
        "moves": [
            {"name": "Surf",           "type": "Water"},
            {"name": "Ice Beam",       "type": "Ice"},
            {"name": "Psychic",        "type": "Psychic"},
            {"name": "Thunderbolt",    "type": "Electric"},
            {"name": "Scald",          "type": "Water"},
            {"name": "Rapid Spin",     "type": "Normal"},
            {"name": "Recover",        "type": "Normal"},
            {"name": "Power Gem",      "type": "Rock"},
            {"name": "Dazzling Gleam", "type": "Fairy"},
            {"name": "Psyshock",       "type": "Psychic"},
        ],
        "niche_threat": {"move": "Shadow Ball", "type": "Ghost",
                         "note": "Opposing Psychic mirror match coverage"},
    },
    {
        "name": "Meganium", "dex_id": 154,
        "types": ["Grass"], "pokeapi_slug": "meganium",
        "game8_id": 593932, "tier_singles": "A", "tier_doubles": "A",
        "roles": ["pivot","redirection"],
        "moves": [
            {"name": "Giga Drain",     "type": "Grass"},
            {"name": "Leech Seed",     "type": "Grass"},
            {"name": "Aromatherapy",   "type": "Grass"},
            {"name": "Earthquake",     "type": "Ground"},
            {"name": "Synthesis",      "type": "Grass"},
            {"name": "Toxic",          "type": "Poison"},
            {"name": "Ancient Power",  "type": "Rock"},
            {"name": "Body Press",     "type": "Fighting"},
            {"name": "Reflect",        "type": "Psychic"},
            {"name": "Light Screen",   "type": "Psychic"},
        ],
        "niche_threat": {"move": "Dragon Tail", "type": "Dragon",
                         "note": "Forces out setup sweepers, ignores Substitute"},
    },
    # ─ No tier data yet ──────────────────────────────────────────────────────
    {
        "name": "Lucario", "dex_id": 448,
        "types": ["Fighting","Steel"], "pokeapi_slug": "lucario",
        "game8_id": None, "tier_singles": None, "tier_doubles": None,
        "roles": ["sweeper"],
        "moves": [
            {"name": "Close Combat",   "type": "Fighting"},
            {"name": "Flash Cannon",   "type": "Steel"},
            {"name": "Aura Sphere",    "type": "Fighting"},
            {"name": "Iron Tail",      "type": "Steel"},
            {"name": "Bullet Punch",   "type": "Steel"},
            {"name": "Swords Dance",   "type": "Normal"},
            {"name": "Calm Mind",      "type": "Psychic"},
            {"name": "Dark Pulse",     "type": "Dark"},
            {"name": "Vacuum Wave",    "type": "Fighting"},
            {"name": "Nasty Plot",     "type": "Dark"},
        ],
        "niche_threat": {"move": "Ice Punch", "type": "Ice",
                         "note": "Ground/Dragon coverage, unexpected from Lucario"},
    },
    {
        "name": "Pikachu", "dex_id": 25,
        "types": ["Electric"], "pokeapi_slug": "pikachu",
        "game8_id": None, "tier_singles": None, "tier_doubles": None,
        "roles": ["sweeper"],
        "moves": [
            {"name": "Thunderbolt",    "type": "Electric"},
            {"name": "Volt Tackle",    "type": "Electric"},
            {"name": "Iron Tail",      "type": "Steel"},
            {"name": "Quick Attack",   "type": "Normal"},
            {"name": "Nuzzle",         "type": "Electric"},
            {"name": "Thunder",        "type": "Electric"},
            {"name": "Surf",           "type": "Water"},
            {"name": "Fake Out",       "type": "Normal"},
            {"name": "Encore",         "type": "Normal"},
            {"name": "Volt Switch",    "type": "Electric"},
        ],
        "niche_threat": {"move": "Brick Break", "type": "Fighting",
                         "note": "Rock/Normal coverage, very rarely run"},
    },
    {
        "name": "Gardevoir", "dex_id": 282,
        "types": ["Psychic","Fairy"], "pokeapi_slug": "gardevoir",
        "game8_id": None, "tier_singles": None, "tier_doubles": None,
        "roles": ["sweeper","trick_room"],
        "moves": [
            {"name": "Moonblast",      "type": "Fairy"},
            {"name": "Psychic",        "type": "Psychic"},
            {"name": "Shadow Ball",    "type": "Ghost"},
            {"name": "Calm Mind",      "type": "Psychic"},
            {"name": "Dazzling Gleam", "type": "Fairy"},
            {"name": "Thunderbolt",    "type": "Electric"},
            {"name": "Focus Blast",    "type": "Fighting"},
            {"name": "Trick",          "type": "Psychic"},
            {"name": "Will-O-Wisp",    "type": "Fire"},
            {"name": "Healing Wish",   "type": "Psychic"},
        ],
        "niche_threat": {"move": "Energy Ball", "type": "Grass",
                         "note": "Water/Ground coverage opponents won't expect"},
    },
    {
        "name": "Scizor", "dex_id": 212,
        "types": ["Bug","Steel"], "pokeapi_slug": "scizor",
        "game8_id": None, "tier_singles": None, "tier_doubles": None,
        "roles": ["sweeper","pivot"],
        "moves": [
            {"name": "Bullet Punch",   "type": "Steel"},
            {"name": "U-turn",         "type": "Bug"},
            {"name": "Swords Dance",   "type": "Normal"},
            {"name": "Superpower",     "type": "Fighting"},
            {"name": "Bug Bite",       "type": "Bug"},
            {"name": "Iron Head",      "type": "Steel"},
            {"name": "Knock Off",      "type": "Dark"},
            {"name": "Roost",          "type": "Flying"},
            {"name": "Quick Attack",   "type": "Normal"},
            {"name": "Body Press",     "type": "Fighting"},
        ],
        "niche_threat": {"move": "Aerial Ace", "type": "Flying",
                         "note": "Hits Fighting types that try to counter Scizor"},
    },
    {
        "name": "Hydreigon", "dex_id": 635,
        "types": ["Dark","Dragon"], "pokeapi_slug": "hydreigon",
        "game8_id": None, "tier_singles": None, "tier_doubles": None,
        "roles": ["sweeper","pivot"],
        "moves": [
            {"name": "Dragon Pulse",   "type": "Dragon"},
            {"name": "Dark Pulse",     "type": "Dark"},
            {"name": "Fire Blast",     "type": "Fire"},
            {"name": "Roost",          "type": "Flying"},
            {"name": "Flash Cannon",   "type": "Steel"},
            {"name": "Taunt",          "type": "Dark"},
            {"name": "Draco Meteor",   "type": "Dragon"},
            {"name": "Earth Power",    "type": "Ground"},
            {"name": "Nasty Plot",     "type": "Dark"},
            {"name": "U-turn",         "type": "Bug"},
        ],
        "niche_threat": {"move": "Focus Blast", "type": "Fighting",
                         "note": "Dark/Ice/Steel coverage in one move"},
    },
    {
        "name": "Milotic", "dex_id": 350,
        "types": ["Water"], "pokeapi_slug": "milotic",
        "game8_id": None, "tier_singles": None, "tier_doubles": None,
        "roles": ["pivot"],
        "moves": [
            {"name": "Scald",          "type": "Water"},
            {"name": "Ice Beam",       "type": "Ice"},
            {"name": "Recover",        "type": "Normal"},
            {"name": "Dragon Pulse",   "type": "Dragon"},
            {"name": "Icy Wind",       "type": "Ice"},
            {"name": "Mirror Coat",    "type": "Psychic"},
            {"name": "Hypnosis",       "type": "Psychic"},
            {"name": "Coil",           "type": "Poison"},
            {"name": "Aqua Ring",      "type": "Water"},
            {"name": "Muddy Water",    "type": "Water"},
        ],
        "niche_threat": {"move": "Dazzling Gleam", "type": "Fairy",
                         "note": "Dragon coverage, very rarely expected from Milotic"},
    },
    {
        "name": "Ursaluna", "dex_id": 901,
        "types": ["Ground","Normal"], "pokeapi_slug": "ursaluna",
        "game8_id": None, "tier_singles": None, "tier_doubles": None,
        "roles": ["sweeper"],
        "moves": [
            {"name": "Headlong Rush",  "type": "Ground"},
            {"name": "Earthquake",     "type": "Ground"},
            {"name": "Body Press",     "type": "Fighting"},
            {"name": "Facade",         "type": "Normal"},
            {"name": "Rock Slide",     "type": "Rock"},
            {"name": "Ice Punch",      "type": "Ice"},
            {"name": "Thunder Punch",  "type": "Electric"},
            {"name": "Swords Dance",   "type": "Normal"},
            {"name": "Drain Punch",    "type": "Fighting"},
            {"name": "Protect",        "type": "Normal"},
        ],
        "niche_threat": {"move": "Play Rough", "type": "Fairy",
                         "note": "Dragon types expect a free switch vs Ursaluna"},
    },
    {
        "name": "Hydrapple", "dex_id": 1019,
        "types": ["Grass","Dragon"], "pokeapi_slug": "hydrapple",
        "game8_id": None, "tier_singles": None, "tier_doubles": None,
        "roles": ["sweeper","pivot"],
        "moves": [
            {"name": "Dragon Pulse",   "type": "Dragon"},
            {"name": "Giga Drain",     "type": "Grass"},
            {"name": "Recover",        "type": "Normal"},
            {"name": "Leech Seed",     "type": "Grass"},
            {"name": "Earth Power",    "type": "Ground"},
            {"name": "Draco Meteor",   "type": "Dragon"},
            {"name": "Body Press",     "type": "Fighting"},
            {"name": "Hex",            "type": "Ghost"},
            {"name": "Hyper Voice",    "type": "Normal"},
            {"name": "Calm Mind",      "type": "Psychic"},
        ],
        "niche_threat": {"move": "Flash Cannon", "type": "Steel",
                         "note": "Ice/Fairy coverage that wrecks Dragon counters"},
    },
    {
        "name": "Talonflame", "dex_id": 663,
        "types": ["Fire","Flying"], "pokeapi_slug": "talonflame",
        "game8_id": None, "tier_singles": None, "tier_doubles": None,
        "roles": ["sweeper","tailwind"],
        "moves": [
            {"name": "Brave Bird",     "type": "Flying"},
            {"name": "Flare Blitz",    "type": "Fire"},
            {"name": "Tailwind",       "type": "Flying"},
            {"name": "Roost",          "type": "Flying"},
            {"name": "Quick Guard",    "type": "Fighting"},
            {"name": "Will-O-Wisp",    "type": "Fire"},
            {"name": "Steel Wing",     "type": "Steel"},
            {"name": "U-turn",         "type": "Bug"},
            {"name": "Acrobatics",     "type": "Flying"},
            {"name": "Aerial Ace",     "type": "Flying"},
        ],
        "niche_threat": {"move": "Low Sweep", "type": "Fighting",
                         "note": "Slows Rock types that try to wall Talonflame"},
    },
    {
        "name": "Serperior", "dex_id": 497,
        "types": ["Grass"], "pokeapi_slug": "serperior",
        "game8_id": None, "tier_singles": None, "tier_doubles": None,
        "roles": ["sweeper"],
        "moves": [
            {"name": "Leaf Storm",     "type": "Grass"},
            {"name": "Dragon Pulse",   "type": "Dragon"},
            {"name": "Glare",          "type": "Normal"},
            {"name": "Leech Seed",     "type": "Grass"},
            {"name": "Substitute",     "type": "Normal"},
            {"name": "Coil",           "type": "Poison"},
            {"name": "Knock Off",      "type": "Dark"},
            {"name": "Taunt",          "type": "Dark"},
            {"name": "Hidden Power Fire","type": "Fire"},
            {"name": "Synthesis",      "type": "Grass"},
        ],
        "niche_threat": {"move": "Aerial Ace", "type": "Flying",
                         "note": "Bug/Fighting coverage that ignores accuracy drops"},
    },
    {
        "name": "Feraligatr", "dex_id": 160,
        "types": ["Water"], "pokeapi_slug": "feraligatr",
        "game8_id": None, "tier_singles": None, "tier_doubles": None,
        "roles": ["sweeper"],
        "moves": [
            {"name": "Waterfall",      "type": "Water"},
            {"name": "Ice Punch",      "type": "Ice"},
            {"name": "Low Kick",       "type": "Fighting"},
            {"name": "Dragon Dance",   "type": "Dragon"},
            {"name": "Crunch",         "type": "Dark"},
            {"name": "Aqua Jet",       "type": "Water"},
            {"name": "Superpower",     "type": "Fighting"},
            {"name": "Body Slam",      "type": "Normal"},
            {"name": "Rock Slide",     "type": "Rock"},
            {"name": "Liquidation",    "type": "Water"},
        ],
        "niche_threat": {"move": "Earthquake", "type": "Ground",
                         "note": "Poison/Electric/Steel coverage not usually expected"},
    },
    {
        "name": "Kommo-o", "dex_id": 784,
        "types": ["Dragon","Fighting"], "pokeapi_slug": "kommo-o",
        "game8_id": None, "tier_singles": None, "tier_doubles": None,
        "roles": ["sweeper"],
        "moves": [
            {"name": "Close Combat",   "type": "Fighting"},
            {"name": "Dragon Claw",    "type": "Dragon"},
            {"name": "Poison Jab",     "type": "Poison"},
            {"name": "Iron Head",      "type": "Steel"},
            {"name": "Clanging Scales","type": "Dragon"},
            {"name": "Drain Punch",    "type": "Fighting"},
            {"name": "Swords Dance",   "type": "Normal"},
            {"name": "Thunder Punch",  "type": "Electric"},
            {"name": "Ice Punch",      "type": "Ice"},
            {"name": "Stealth Rock",   "type": "Rock"},
        ],
        "niche_threat": {"move": "Flash Cannon", "type": "Steel",
                         "note": "Ice/Fairy coverage, catches Dragon counters off guard"},
    },
    {
        "name": "Metagross", "dex_id": 376,
        "types": ["Steel","Psychic"], "pokeapi_slug": "metagross",
        "game8_id": None, "tier_singles": None, "tier_doubles": None,
        "roles": ["sweeper"],
        "moves": [
            {"name": "Meteor Mash",    "type": "Steel"},
            {"name": "Zen Headbutt",   "type": "Psychic"},
            {"name": "Earthquake",     "type": "Ground"},
            {"name": "Ice Punch",      "type": "Ice"},
            {"name": "Thunder Punch",  "type": "Electric"},
            {"name": "Bullet Punch",   "type": "Steel"},
            {"name": "Hammer Arm",     "type": "Fighting"},
            {"name": "Rock Slide",     "type": "Rock"},
            {"name": "Stealth Rock",   "type": "Rock"},
            {"name": "Body Press",     "type": "Fighting"},
        ],
        "niche_threat": {"move": "Grass Knot", "type": "Grass",
                         "note": "Water/Ground counter, very niche but punishing"},
    },
    {
        "name": "Empoleon", "dex_id": 395,
        "types": ["Water","Steel"], "pokeapi_slug": "empoleon",
        "game8_id": None, "tier_singles": None, "tier_doubles": None,
        "roles": ["pivot","hazard_setter"],
        "moves": [
            {"name": "Surf",           "type": "Water"},
            {"name": "Flash Cannon",   "type": "Steel"},
            {"name": "Ice Beam",       "type": "Ice"},
            {"name": "Stealth Rock",   "type": "Rock"},
            {"name": "Defog",          "type": "Flying"},
            {"name": "Toxic",          "type": "Poison"},
            {"name": "Agility",        "type": "Psychic"},
            {"name": "Scald",          "type": "Water"},
            {"name": "Aqua Jet",       "type": "Water"},
            {"name": "Body Press",     "type": "Fighting"},
        ],
        "niche_threat": {"move": "Grass Knot", "type": "Grass",
                         "note": "Water/Ground mirror match coverage"},
    },
    {
        "name": "Leafeon", "dex_id": 470,
        "types": ["Grass"], "pokeapi_slug": "leafeon",
        "game8_id": None, "tier_singles": None, "tier_doubles": None,
        "roles": ["sweeper"],
        "moves": [
            {"name": "Leaf Blade",     "type": "Grass"},
            {"name": "X-Scissor",      "type": "Bug"},
            {"name": "Swords Dance",   "type": "Normal"},
            {"name": "Quick Attack",   "type": "Normal"},
            {"name": "Knock Off",      "type": "Dark"},
            {"name": "Body Press",     "type": "Fighting"},
            {"name": "Synthesis",      "type": "Grass"},
            {"name": "Leech Seed",     "type": "Grass"},
            {"name": "Solar Blade",    "type": "Grass"},
            {"name": "Iron Tail",      "type": "Steel"},
        ],
        "niche_threat": {"move": "Shadow Ball", "type": "Ghost",
                         "note": "Psychic coverage not expected from Leafeon"},
    },
    {
        "name": "Sylveon", "dex_id": 700,
        "types": ["Fairy"], "pokeapi_slug": "sylveon",
        "game8_id": None, "tier_singles": None, "tier_doubles": None,
        "roles": ["sweeper","pivot"],
        "moves": [
            {"name": "Moonblast",      "type": "Fairy"},
            {"name": "Hyper Voice",    "type": "Normal"},
            {"name": "Shadow Ball",    "type": "Ghost"},
            {"name": "Calm Mind",      "type": "Psychic"},
            {"name": "Dazzling Gleam", "type": "Fairy"},
            {"name": "Psyshock",       "type": "Psychic"},
            {"name": "Mystical Fire",  "type": "Fire"},
            {"name": "Protect",        "type": "Normal"},
            {"name": "Wish",           "type": "Normal"},
            {"name": "Trick",          "type": "Psychic"},
        ],
        "niche_threat": {"move": "Energy Ball", "type": "Grass",
                         "note": "Water/Ground coverage not expected from Sylveon"},
    },
    {
        "name": "Dondozo", "dex_id": 982,
        "types": ["Water"], "pokeapi_slug": "dondozo",
        "game8_id": None, "tier_singles": None, "tier_doubles": None,
        "roles": ["pivot","trick_room"],
        "moves": [
            {"name": "Wave Crash",     "type": "Water"},
            {"name": "Earthquake",     "type": "Ground"},
            {"name": "Order Up",       "type": "Normal"},
            {"name": "Body Press",     "type": "Fighting"},
            {"name": "Yawn",           "type": "Normal"},
            {"name": "Heavy Slam",     "type": "Steel"},
            {"name": "Waterfall",      "type": "Water"},
            {"name": "Rest",           "type": "Psychic"},
            {"name": "Amnesia",        "type": "Psychic"},
            {"name": "Rock Slide",     "type": "Rock"},
        ],
        "niche_threat": {"move": "Ice Fang", "type": "Ice",
                         "note": "Dragon/Grass coverage that walls Water moves"},
    },
    {
        "name": "Oranguru", "dex_id": 765,
        "types": ["Normal","Psychic"], "pokeapi_slug": "oranguru",
        "game8_id": None, "tier_singles": None, "tier_doubles": None,
        "roles": ["trick_room","pivot"],
        "moves": [
            {"name": "Psychic",        "type": "Psychic"},
            {"name": "Trick Room",     "type": "Psychic"},
            {"name": "Instruct",       "type": "Psychic"},
            {"name": "Calm Mind",      "type": "Psychic"},
            {"name": "Shadow Ball",    "type": "Ghost"},
            {"name": "Focus Blast",    "type": "Fighting"},
            {"name": "Thunder Wave",   "type": "Electric"},
            {"name": "Protect",        "type": "Normal"},
            {"name": "Foul Play",      "type": "Dark"},
            {"name": "Recover",        "type": "Normal"},
        ],
        "niche_threat": {"move": "Energy Ball", "type": "Grass",
                         "note": "Water/Ground coverage to punish switch-ins"},
    },
    {
        "name": "Aegislash", "dex_id": 681,
        "types": ["Steel","Ghost"], "pokeapi_slug": "aegislash-shield",
        "game8_id": None, "tier_singles": None, "tier_doubles": None,
        "roles": ["sweeper","trick_room"],
        "moves": [
            {"name": "Shadow Ball",    "type": "Ghost"},
            {"name": "Flash Cannon",   "type": "Steel"},
            {"name": "King's Shield",  "type": "Steel"},
            {"name": "Swords Dance",   "type": "Normal"},
            {"name": "Iron Head",      "type": "Steel"},
            {"name": "Sacred Sword",   "type": "Fighting"},
            {"name": "Shadow Sneak",   "type": "Ghost"},
            {"name": "Wide Guard",     "type": "Fighting"},
            {"name": "Head Smash",     "type": "Rock"},
            {"name": "Ghost Dive",     "type": "Ghost"},
        ],
        "niche_threat": {"move": "Close Combat", "type": "Fighting",
                         "note": "Dark/Steel coverage in Sword form, very unexpected"},
    },
    {
        "name": "Hisuian Samurott", "dex_id": 503,
        "types": ["Water","Dark"], "pokeapi_slug": "samurott-hisui",
        "game8_id": None, "tier_singles": None, "tier_doubles": None,
        "roles": ["sweeper","hazard_setter"],
        "moves": [
            {"name": "Ceaseless Edge",  "type": "Dark"},
            {"name": "Liquidation",     "type": "Water"},
            {"name": "Close Combat",    "type": "Fighting"},
            {"name": "Night Slash",     "type": "Dark"},
            {"name": "Ice Punch",       "type": "Ice"},
            {"name": "Swords Dance",    "type": "Normal"},
            {"name": "Aqua Jet",        "type": "Water"},
            {"name": "Spikes",          "type": "Ground"},
            {"name": "Knock Off",       "type": "Dark"},
            {"name": "Sucker Punch",    "type": "Dark"},
        ],
        "niche_threat": {"move": "Poison Jab", "type": "Poison",
                         "note": "Fairy coverage that's rarely expected from Samurott"},
    },
]

# ── Build JSON ────────────────────────────────────────────────────────────────

def build(output_path="pokemon_db.json"):
    db = {}
    for p in ROSTER:
        key = p["name"].lower()
        matchups = compute_matchups(p["types"])
        db[key] = {
            "name":          p["name"],
            "dex_id":        p["dex_id"],
            "types":         p["types"],
            "pokeapi_slug":  p["pokeapi_slug"],
            "game8_id":      p["game8_id"],
            "game8_url":     f"https://game8.co/games/Pokemon-Champions/archives/{p['game8_id']}" if p["game8_id"] else None,
            "tier_singles":  p.get("tier_singles"),
            "tier_doubles":  p.get("tier_doubles"),
            "roles":         p.get("roles", []),
            "moves":         p.get("moves", []),
            "niche_threat":  p.get("niche_threat"),
            **matchups,
        }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    print(f"Built {len(db)} pokemon -> {output_path}")
    return db


# ── Analysis helpers ──────────────────────────────────────────────────────────

def _roster_db():
    return {p["name"].lower(): p for p in ROSTER}


def how_to_beat(target_name):
    """
    Given a target pokemon, prints:
      - What types threaten it (4x / 2x)
      - Which roster pokemon have moves that cover those weaknesses
      - What moves the target itself typically runs (so you know what it threatens back)
    """
    db = _roster_db()
    target = db.get(target_name.lower())
    if not target:
        print(f"Unknown: {target_name}")
        return

    mu = compute_matchups(target["types"])
    threat_types = set(mu["weak4x"] + mu["weak2x"])

    print(f"\n{'='*55}")
    print(f"  How to beat {target['name']}  ({'/'.join(target['types'])})")
    print(f"{'='*55}")

    if mu["weak4x"]:
        print(f"  4x WEAK :  {', '.join(mu['weak4x'])}  << exploit this")
    if mu["weak2x"]:
        print(f"  2x weak :  {', '.join(mu['weak2x'])}")
    if mu["immune"]:
        print(f"  Immune  :  {', '.join(mu['immune'])}  << don't use these")
    if mu["resist"]:
        print(f"  Resists :  {', '.join(mu['resist'])}")

    print(f"\n  {target['name']} typically threatens with:")
    for move in target["moves"]:
        print(f"    {move['name']:20s} ({move['type']})")
    if target.get("niche_threat"):
        nt = target["niche_threat"]
        print(f"    [NICHE] {nt['move']} ({nt['type']}) - {nt['note']}")

    print(f"\n  Roster counters (pokemon with SE moves vs {target['name']}):")
    found = False
    for p in ROSTER:
        if p["name"] == target["name"]:
            continue
        hits = []
        for move in p.get("moves", []):
            if move["type"] in mu["weak4x"]:
                hits.append(f"{move['name']} ({move['type']}) x4!")
            elif move["type"] in mu["weak2x"]:
                hits.append(f"{move['name']} ({move['type']}) x2")
        nt = p.get("niche_threat")
        if nt and nt["type"] in threat_types:
            mult = "x4!" if nt["type"] in mu["weak4x"] else "x2"
            hits.append(f"[niche] {nt['move']} ({nt['type']}) {mult}")
        if hits:
            found = True
            print(f"    {p['name']:22s}: {', '.join(hits)}")
    if not found:
        print("    None in current roster!")


def matchup(attacker_name, defender_name):
    """
    Bidirectional matchup: what can attacker do to defender and vice versa.
    """
    db = _roster_db()
    att = db.get(attacker_name.lower())
    defe = db.get(defender_name.lower())
    if not att or not defe:
        print("Unknown pokemon name(s)")
        return

    att_mu  = compute_matchups(att["types"])
    def_mu  = compute_matchups(defe["types"])

    def _label(move_type, matchups):
        if move_type in matchups["weak4x"]:   return "x4! "
        if move_type in matchups["weak2x"]:   return "x2  "
        if move_type in matchups["immune"]:   return "IMM "
        if move_type in matchups["resist"]:   return "1/2 "
        return "    "

    print(f"\n  {att['name']} vs {defe['name']}")
    print(f"  {'-'*45}")
    print(f"\n  {att['name']} attacking {defe['name']}:")
    for move in att.get("moves", []):
        label = _label(move["type"], def_mu)
        if label.strip():
            print(f"    {label} {move['name']:20s} ({move['type']})")
    nt = att.get("niche_threat")
    if nt:
        label = _label(nt["type"], def_mu)
        print(f"    {label} [niche] {nt['move']:14s} ({nt['type']})")

    print(f"\n  {defe['name']} attacking {att['name']}:")
    for move in defe.get("moves", []):
        label = _label(move["type"], att_mu)
        if label.strip():
            print(f"    {label} {move['name']:20s} ({move['type']})")
    nt = defe.get("niche_threat")
    if nt:
        label = _label(nt["type"], att_mu)
        print(f"    {label} [niche] {nt['move']:14s} ({nt['type']})")


if __name__ == "__main__":
    build()
    how_to_beat("Incineroar")
    print()
    matchup("Garchomp", "Incineroar")
