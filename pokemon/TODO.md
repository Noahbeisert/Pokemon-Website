# Damage Calculator — TODO

## Done
- [x] Damage engine (16-roll spread, STAB, type effectiveness)
- [x] Held items (berries, choice items, type boosters, plates, AV, Eviolite, Air Balloon)
- [x] Attacker abilities (Huge Power, Adaptability, Tough Claws, Technician, etc.)
- [x] Defender abilities (Multiscale, Filter, Fluffy, Ice Scales, immunities, etc.)
- [x] Field: Weather, Terrain, Screens (Reflect / Light Screen / Aurora Veil)
- [x] Stat stages (±6, updates live stat display)
- [x] Three scenarios: Current / Defensive Max / Critical Hit
- [x] IVs fixed at 31, Stat Points (66 cap, +1 direct)
- [x] Autocomplete: Pokemon, moves, abilities (pokemon-specific, instant on focus), items (local list)

---

## Bugs / Polish
- [ ] OHKO moves (Fissure, Horn Drill, Sheer Cold, Guillotine) — detect via `meta.category === 'ohko'` in loadMove(), skip damage calc entirely, show "OHKO move — not calculable"
- [ ] Moves that can't crit (Future Sight, fixed-damage moves) — add `cannotCrit` flag to move data, hide crit section in buildResult()
- [ ] Wonder Guard edge case — currently returns immune for eff ≤ 1 before checking the normal-type Chilan Berry path

---

## High Priority

### Both sides as attacker / defender
Currently attacker = always My Team, defender = always Enemy Team.

**Change:** merge both teams into both dropdowns, labeled by side.
- Use `<optgroup>` tags: "My Team" group then "Enemy Team" group
- Pull from both `S.my` and `S.en` instead of one side each
- `refreshSelectors()` needs to encode side+idx in the value, e.g. `"my-2"` or `"en-4"`
- `calculate()` parses `"my-2"` → `{side:'my', idx:2}` to get the pokemon

### Doubles — spread move multiplier
In doubles, moves that hit multiple targets deal 0.75× damage (standard VGC rule).

**PokeAPI targets that trigger 0.75×:**
- `all-opponents` (Heat Wave, Discharge, Hyper Voice, etc.)
- `all-other-pokemon` (Earthquake, Surf — also hits partner)
- `all-pokemon` (rarely used)

**Change:** save `target: d.target.name` in `loadMove()`. In `calc()`, add a `spreadMult` param (0.75 if spread, else 1.0). Show "Spread (0.75×)" in result metadata when active.

### Doubles — two attackers into one defender
Use case: "Do my Charizard + Rillaboom together OHKO their Garchomp?"

**UI:** add a second optional attacker row under the first:
```
Attacker 1: [Charizard ▾]   Move: [Flamethrower ▾]
Attacker 2: [Rillaboom ▾]   Move: [Wood Hammer ▾]   [× clear]
```
A small "+ Add attacker" link toggles the second row visible.

**Calc:** run `calc()` twice independently, then compute combined result:
- `combinedMin = r1.dMin + r2.dMin`
- `combinedMax = r1.dMax + r2.dMax`
- Show a fourth section: "Combined" with the same bar + badge logic

**Note:** the two moves are independent damage instances — no interactions between them in the formula.

### Doubles — spread move hitting both defenders
Use case: "Earthquake from Landorus hits both enemy slots — does it KO both?"

**UI:** when a spread move is selected, show a second "Defender 2" selector (optional). If filled, run calc against both defenders and show two result panels side by side (or stacked).

```
Move: [Earthquake ▾]  ← spread detected automatically
Defender 1: [Garchomp ▾]
Defender 2: [Tyranitar ▾]   [× clear]
```

---

## Medium Priority

### Doubles — Helping Hand
An ally using Helping Hand boosts the next move by 1.5×.
- Add a `helpingHand` checkbox in the calc panel (shown only in doubles context)
- Apply as a multiplier in the roll pipeline

### Doubles — ally Friend Guard
Defender's ally with Friend Guard reduces incoming damage by 0.75×.
- Add "Ally ability" dropdown next to the defender section
- Apply in `calc()` when ally ability = 'friend-guard'

### Doubles — redirection
Storm Drain and Lightning Rod redirect moves in doubles. This is a targeting mechanic more than a damage one — flag it as an info note when the move type matches the ally's ability, rather than trying to calc it.

---

## Low Priority / Nice to Have
- [ ] Tailwind: ×2 Speed for the team (Speed doesn't affect damage, but useful for turn-order display if we ever add that)
- [ ] Tera type support (Champions-specific — check if the game uses Terastallization)
- [ ] Move search across all moves, not just the pokemon's learnset (for when learnset isn't loaded yet)
- [ ] Result permalink / shareable URL (encode atk/def/move/evs in query string)
