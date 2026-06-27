"""
Pokemon Champions damage calculator.

Game parameters (from pokebase.app damage-calc JS bundle analysis):
  - Level 50, IVs always 31, Gen 9 stat formula
  - EVs: 0-32 per stat in-game, stored raw; multiply by 8 for smogon formula (max 252)
  - Total EV budget: 66 points (528 smogon equivalent), scaled to 510 if over
  - No Choice Band/Specs/Life Orb; type-boosting items give 1.2x
  - Resist berries give 0.5x vs super-effective moves of their type

Usage:
    from damage_calc import calc, StatBlock

    attacker = StatBlock("incineroar", attack=95, sp_atk=75, nature="Adamant", atk_ev=32)
    defender = StatBlock("ferrothorn", defense=131, sp_def=116)
    result = calc(attacker, "flare-blitz", defender, db_path="pokemon_app.db")
    print(result)
"""
import math
import sqlite3
from dataclasses import dataclass, field
from typing import Optional


LEVEL = 50

NATURE_MULTS = {
    "Hardy":   {},
    "Lonely":  {"attack": 1.1, "defense": 0.9},
    "Brave":   {"attack": 1.1, "speed": 0.9},
    "Adamant": {"attack": 1.1, "sp_atk": 0.9},
    "Naughty": {"attack": 1.1, "sp_def": 0.9},
    "Bold":    {"defense": 1.1, "attack": 0.9},
    "Docile":  {},
    "Relaxed": {"defense": 1.1, "speed": 0.9},
    "Impish":  {"defense": 1.1, "sp_atk": 0.9},
    "Lax":     {"defense": 1.1, "sp_def": 0.9},
    "Timid":   {"speed": 1.1, "attack": 0.9},
    "Hasty":   {"speed": 1.1, "defense": 0.9},
    "Serious": {},
    "Jolly":   {"speed": 1.1, "sp_atk": 0.9},
    "Naive":   {"speed": 1.1, "sp_def": 0.9},
    "Modest":  {"sp_atk": 1.1, "attack": 0.9},
    "Mild":    {"sp_atk": 1.1, "defense": 0.9},
    "Quiet":   {"sp_atk": 1.1, "speed": 0.9},
    "Bashful": {},
    "Rash":    {"sp_atk": 1.1, "sp_def": 0.9},
    "Calm":    {"sp_def": 1.1, "attack": 0.9},
    "Gentle":  {"sp_def": 1.1, "defense": 0.9},
    "Sassy":   {"sp_def": 1.1, "speed": 0.9},
    "Careful": {"sp_def": 1.1, "sp_atk": 0.9},
    "Quirky":  {},
}

# Stat stage multipliers (numerators / 2 for attack/defense stages)
# Stages -6 to +6
_STAGE_MULT = {
    -6: 2/8, -5: 2/7, -4: 2/6, -3: 2/5, -2: 2/4, -1: 2/3,
     0: 1.0,
     1: 3/2,  2: 4/2,  3: 5/2,  4: 6/2,  5: 7/2,  6: 8/2,
}

# Type-boosting items: item_slug → type they boost
TYPE_BOOST_ITEMS = {
    "charcoal":       "Fire",
    "mystic-water":   "Water",
    "miracle-seed":   "Grass",
    "magnet":         "Electric",
    "never-melt-ice": "Ice",
    "black-belt":     "Fighting",
    "poison-barb":    "Poison",
    "soft-sand":      "Ground",
    "sharp-beak":     "Flying",
    "twisted-spoon":  "Psychic",
    "silver-powder":  "Bug",
    "hard-stone":     "Rock",
    "spell-tag":      "Ghost",
    "dragon-fang":    "Dragon",
    "black-glasses":  "Dark",
    "metal-coat":     "Steel",
    "silk-scarf":     "Normal",
    "fairy-feather":  "Fairy",
}

# Resist berries: item_slug → type they halve (when hit super-effectively)
RESIST_BERRIES = {
    "cheri-berry":   None,   # status berries — not resist berries, ignore
    "occa-berry":    "Fire",
    "passho-berry":  "Water",
    "wacan-berry":   "Electric",
    "rindo-berry":   "Grass",
    "yache-berry":   "Ice",
    "chople-berry":  "Fighting",
    "kebia-berry":   "Poison",
    "shuca-berry":   "Ground",
    "coba-berry":    "Flying",
    "payapa-berry":  "Psychic",
    "tanga-berry":   "Bug",
    "charti-berry":  "Rock",
    "kasib-berry":   "Ghost",
    "haban-berry":   "Dragon",
    "colbur-berry":  "Dark",
    "babiri-berry":  "Steel",
    "roseli-berry":  "Fairy",
    "chilan-berry":  "Normal",
}


def _smogon_ev(champions_ev: int) -> int:
    return min(252, champions_ev * 8)


def calc_stat(base: int, ev: int = 0, nature: str = "Hardy", stat: str = "attack") -> int:
    """
    Compute a final stat value (non-HP) at level 50, 31 IVs.
    ev is in Pokemon Champions units (0-32); converted to smogon internally.
    """
    smogon_ev = _smogon_ev(ev)
    raw = math.floor((2 * base + 31 + smogon_ev * 2) * 0.5) + 5
    mult = NATURE_MULTS.get(nature, {}).get(stat, 1.0)
    return math.floor(raw * mult)


def calc_hp(base: int, ev: int = 0) -> int:
    smogon_ev = _smogon_ev(ev)
    return math.floor((2 * base + 31 + smogon_ev * 2) * 0.5) + 60


@dataclass
class StatBlock:
    """
    Represents a Pokemon in battle with its current stats and modifiers.
    Pass base stat values + ev allocations + nature; final stats are computed.
    Or pass final_* overrides to skip the formula.
    """
    slug: str = ""
    nature: str = "Hardy"
    item: Optional[str] = None        # item slug

    # Base stats (from DB if not provided)
    base_hp:     int = 0
    base_atk:    int = 0
    base_def:    int = 0
    base_spa:    int = 0
    base_spd:    int = 0
    base_spe:    int = 0

    # EV allocation (Champions units, 0-32 each)
    hp_ev:  int = 0
    atk_ev: int = 0
    def_ev: int = 0
    spa_ev: int = 0
    spd_ev: int = 0
    spe_ev: int = 0

    # Stat stages (-6 to +6)
    atk_stage: int = 0
    def_stage: int = 0
    spa_stage: int = 0
    spd_stage: int = 0
    spe_stage: int = 0

    # Optional stat overrides (skip formula)
    final_hp:  Optional[int] = None
    final_atk: Optional[int] = None
    final_def: Optional[int] = None
    final_spa: Optional[int] = None
    final_spd: Optional[int] = None
    final_spe: Optional[int] = None

    def hp(self)  -> int: return self.final_hp  or calc_hp(self.base_hp, self.hp_ev)
    def atk(self) -> int: return self.final_atk or calc_stat(self.base_atk, self.atk_ev, self.nature, "attack")
    def def_(self)-> int: return self.final_def or calc_stat(self.base_def, self.def_ev, self.nature, "defense")
    def spa(self) -> int: return self.final_spa or calc_stat(self.base_spa, self.spa_ev, self.nature, "sp_atk")
    def spd(self) -> int: return self.final_spd or calc_stat(self.base_spd, self.spd_ev, self.nature, "sp_def")
    def spe(self) -> int: return self.final_spe or calc_stat(self.base_spe, self.spe_ev, self.nature, "speed")

    def effective_atk(self) -> int:
        return math.floor(self.atk() * _STAGE_MULT[self.atk_stage])

    def effective_def(self) -> int:
        return math.floor(self.def_() * _STAGE_MULT[self.def_stage])

    def effective_spa(self) -> int:
        return math.floor(self.spa() * _STAGE_MULT[self.spa_stage])

    def effective_spd(self) -> int:
        return math.floor(self.spd() * _STAGE_MULT[self.spd_stage])


@dataclass
class CalcResult:
    damage_min: int
    damage_max: int
    damage_rolls: list[int]
    ko_chance: float          # fraction of rolls that KO (defender.hp() is used)
    defender_hp: int
    type_effectiveness: float
    is_stab: bool
    attacker_item_mult: float
    defender_item_mult: float
    move_name: str
    move_type: str
    damage_class: str

    def __str__(self):
        rolls_str = "-".join(str(r) for r in self.damage_rolls)
        pct_min = round(100 * self.damage_min / self.defender_hp, 1)
        pct_max = round(100 * self.damage_max / self.defender_hp, 1)
        ko_str = f" ({self.ko_chance*100:.0f}% KO)" if self.ko_chance > 0 else ""
        return (
            f"{self.move_name} [{self.move_type}] {self.damage_class}\n"
            f"  Rolls: {rolls_str}\n"
            f"  Damage: {self.damage_min}-{self.damage_max} ({pct_min}-{pct_max}% of {self.defender_hp} HP){ko_str}\n"
            f"  STAB={self.is_stab}  TypeMult={self.type_effectiveness}x"
            f"  AtkItem={self.attacker_item_mult}x  DefItem={self.defender_item_mult}x"
        )


def _load_from_db(slug: str, db_path: str) -> dict:
    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT hp, attack, defense, sp_atk, sp_def, speed, type1, type2 FROM pokemon WHERE slug=?",
        (slug,),
    ).fetchone()
    conn.close()
    if not row:
        raise ValueError(f"Pokemon not found in DB: {slug!r}")
    return {
        "base_hp": row[0], "base_atk": row[1], "base_def": row[2],
        "base_spa": row[3], "base_spd": row[4], "base_spe": row[5],
        "type1": row[6], "type2": row[7],
    }


def load_statblock(slug: str, db_path: str, nature: str = "Hardy", item: str = None,
                   hp_ev=0, atk_ev=0, def_ev=0, spa_ev=0, spd_ev=0, spe_ev=0) -> StatBlock:
    d = _load_from_db(slug, db_path)
    return StatBlock(
        slug=slug, nature=nature, item=item,
        base_hp=d["base_hp"], base_atk=d["base_atk"], base_def=d["base_def"],
        base_spa=d["base_spa"], base_spd=d["base_spd"], base_spe=d["base_spe"],
        hp_ev=hp_ev, atk_ev=atk_ev, def_ev=def_ev,
        spa_ev=spa_ev, spd_ev=spd_ev, spe_ev=spe_ev,
    )


def _get_move(move_slug: str, db_path: str) -> dict:
    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT name, type, damage_class, power FROM move WHERE slug=?", (move_slug,)
    ).fetchone()
    conn.close()
    if not row:
        raise ValueError(f"Move not found in DB: {move_slug!r}")
    return {"name": row[0], "type": row[1], "damage_class": row[2], "power": row[3]}


def _get_type_mult(move_type: str, defender_slug: str, db_path: str) -> float:
    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT multiplier FROM type_chart WHERE pokemon_slug=? AND attacking_type=?",
        (defender_slug, move_type),
    ).fetchone()
    conn.close()
    return row[0] if row else 1.0


def _get_pokemon_types(slug: str, db_path: str) -> tuple[str, Optional[str]]:
    conn = sqlite3.connect(db_path)
    row = conn.execute("SELECT type1, type2 FROM pokemon WHERE slug=?", (slug,)).fetchone()
    conn.close()
    return (row[0], row[1]) if row else (None, None)


def calc(
    attacker: StatBlock,
    move_slug: str,
    defender: StatBlock,
    db_path: str = "pokemon_app.db",
    # Field modifiers
    tailwind_attacker: bool = False,
    tailwind_defender: bool = False,
    trick_room: bool = False,
    reflect: bool = False,       # halves physical damage
    light_screen: bool = False,  # halves special damage
    aurora_veil: bool = False,   # halves both
) -> CalcResult:
    """
    Calculate damage for one move.

    attacker/defender StatBlocks should have base stats set (either manually or via load_statblock).
    Pokemon types and type effectiveness are loaded from db_path.
    """
    move = _get_move(move_slug, db_path)
    if move["power"] is None or move["power"] == 0:
        raise ValueError(f"Move {move_slug!r} has no power (status move?)")

    power = move["power"]
    move_type = move["type"]
    dmg_class = move["damage_class"]

    # --- attacker stat ---
    if dmg_class == "physical":
        atk_stat = attacker.effective_atk()
    else:
        atk_stat = attacker.effective_spa()

    # --- defender stat ---
    if dmg_class == "physical":
        def_stat = defender.effective_def()
    else:
        def_stat = defender.effective_spd()

    # --- STAB ---
    atk_types = _get_pokemon_types(attacker.slug, db_path) if attacker.slug else (None, None)
    is_stab = move_type in atk_types
    stab = 1.5 if is_stab else 1.0

    # --- type effectiveness ---
    type_mult = _get_type_mult(move_type, defender.slug, db_path) if defender.slug else 1.0

    # --- attacker item modifier ---
    atk_item_mult = 1.0
    if attacker.item and move_type:
        boost_type = TYPE_BOOST_ITEMS.get(attacker.item)
        if boost_type and boost_type == move_type:
            atk_item_mult = 1.2

    # --- defender item modifier (resist berries) ---
    def_item_mult = 1.0
    if defender.item and type_mult > 1.0:
        berry_type = RESIST_BERRIES.get(defender.item)
        if berry_type and berry_type == move_type:
            def_item_mult = 0.5

    # --- screen modifiers ---
    screen_mult = 1.0
    if aurora_veil:
        screen_mult = 0.5
    elif dmg_class == "physical" and reflect:
        screen_mult = 0.5
    elif dmg_class == "special" and light_screen:
        screen_mult = 0.5

    # --- base damage (before random roll) ---
    # floor(floor(floor(2*L/5+2) * power * A/D) / 50 + 2)
    base = math.floor(
        math.floor(
            math.floor(2 * LEVEL / 5 + 2) * power * atk_stat / def_stat
        ) / 50 + 2
    )

    # --- roll 16 damage values (85%–100% in 1% steps) ---
    rolls = []
    for r in range(85, 101):
        dmg = math.floor(base * r / 100)
        dmg = math.floor(dmg * stab)
        dmg = math.floor(dmg * type_mult)
        dmg = math.floor(dmg * atk_item_mult)
        dmg = math.floor(dmg * def_item_mult)
        dmg = math.floor(dmg * screen_mult)
        rolls.append(max(1, dmg))

    defender_hp = defender.hp()
    ko_rolls = sum(1 for r in rolls if r >= defender_hp)

    return CalcResult(
        damage_min=rolls[0],
        damage_max=rolls[-1],
        damage_rolls=rolls,
        ko_chance=ko_rolls / len(rolls),
        defender_hp=defender_hp,
        type_effectiveness=type_mult,
        is_stab=is_stab,
        attacker_item_mult=atk_item_mult,
        defender_item_mult=def_item_mult,
        move_name=move["name"],
        move_type=move_type,
        damage_class=dmg_class,
    )


def calc_from_db(
    attacker_slug: str,
    move_slug: str,
    defender_slug: str,
    db_path: str = "pokemon_app.db",
    attacker_nature: str = "Hardy",
    attacker_item: Optional[str] = None,
    defender_item: Optional[str] = None,
    atk_ev: int = 0,
    def_ev: int = 0,
    spa_ev: int = 0,
    spd_ev: int = 0,
    attacker_atk_stage: int = 0,
    attacker_spa_stage: int = 0,
    defender_def_stage: int = 0,
    defender_spd_stage: int = 0,
    **kwargs,
) -> CalcResult:
    """Convenience wrapper: load both pokemon from DB, compute damage."""
    attacker = load_statblock(attacker_slug, db_path, nature=attacker_nature, item=attacker_item,
                              atk_ev=atk_ev, spa_ev=spa_ev)
    attacker.atk_stage = attacker_atk_stage
    attacker.spa_stage = attacker_spa_stage

    defender = load_statblock(defender_slug, db_path, item=defender_item,
                              def_ev=def_ev, spd_ev=spd_ev)
    defender.def_stage = defender_def_stage
    defender.spd_stage = defender_spd_stage

    return calc(attacker, move_slug, defender, db_path=db_path, **kwargs)


if __name__ == "__main__":
    import sys
    db = "pokemon_app.db"

    print("=== Damage Calculator Test ===\n")

    # Test 1: Verify stat formula against known values
    # Incineroar base Atk=115, Adamant nature, 0 EV → should be 167
    stat = calc_stat(115, ev=0, nature="Adamant", stat="attack")
    print(f"Incineroar Atk (Adamant, 0 EV): {stat}  (expected 167)")

    # With 32 EVs (max): min(252, 32*8)=252 EVs
    stat_ev = calc_stat(115, ev=32, nature="Adamant", stat="attack")
    print(f"Incineroar Atk (Adamant, 32 EV): {stat_ev}  (expected 216)")

    # HP: Incineroar base 95, 0 EV → 160
    hp = calc_hp(95, ev=0)
    print(f"Incineroar HP (0 EV): {hp}  (expected 160)")

    print()

    # Test 2: Damage calc from DB
    try:
        result = calc_from_db(
            "incineroar", "flare-blitz", "ferrothorn",
            db_path=db,
            attacker_nature="Adamant",
            atk_ev=32,
        )
        print(f"Adamant +32 Incineroar Flare Blitz vs 0 Def Ferrothorn:")
        print(result)
    except Exception as e:
        print(f"DB test skipped ({e}) — run build_db.py first")

    print()

    # Test 3: Fake Out vs Incineroar
    try:
        result = calc_from_db(
            "incineroar", "fake-out", "incineroar",
            db_path=db,
        )
        print(f"Neutral Incineroar Fake Out vs Incineroar:")
        print(result)
    except Exception as e:
        print(f"DB test skipped ({e})")
