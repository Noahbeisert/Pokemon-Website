# Pokemon Champions — Format & Meta

## Mechanics — Rules Worth Knowing

Doubles-specific interactions that affect play decisions. Log new ones here as discovered.

### Move flags (from PokeAPI `moves/{id}` — `flags` array)
PokeAPI exposes these as boolean flags per move — already scrapeable via `scrape_moves.py`.
Relevant flags for this format:

| Flag | What it means | Example moves |
|---|---|---|
| `sound` | Bypasses Substitute; hits through it | Hyper Voice, Boomburst, Sparkling Aria, Disarming Voice |
| `contact` | Triggers contact abilities (Rough Skin, Iron Barbs, Static, Flame Body) | Close Combat, Fake Out, Flare Blitz |
| `protect` | Blocked by Protect/Detect/King's Shield | Most damaging moves |
| `punch` | Boosted by Iron Fist | Bullet Punch, Ice Punch, Thunder Punch |
| `bullet` | Bypasses Bulletproof ability | Shadow Ball, Sludge Bomb, Aura Sphere |
| `spread` | Hits both opponents (80% power in doubles) | Earthquake, Rock Slide, Heat Wave, Dazzling Gleam |

### Doubles interaction rules
- **Spread moves deal 75% damage to both targets** — Earthquake, Rock Slide, Heat Wave etc. all lose power when hitting two pokemon. Single-target moves do full damage.
- **Sound moves ignore Substitute** — Hyper Voice hits through Substitute. Relevant when running Sylveon/Primarina vs Substitute users.
- **Fake Out only works turn 1** of a pokemon being on the field — switching in and using Fake Out next turn works.
- **Intimidate triggers on switch-in** including mid-turn switches (Parting Shot, U-turn) — can chain multiple Intimidates.
- **Redirection (Follow Me / Rage Powder):** forces single-target moves to hit the redirector. Does NOT redirect spread moves or moves with No Guard.
- **Trick Room reverses speed order** — slower pokemon go first. Under TR, Choice Scarf becomes a liability.
- **Last Respects power:** +50 base power per fainted ally (max +300). One faint = 100 BP, two = 150, three = 200 etc.
- **Helping Hand boosts damage by 50%** and stacks with other modifiers. Commonly paired with high-power spread moves.
- **Protect variant interactions:** King's Shield lowers Attack on contact; Spiky Shield deals damage on contact; Burning Bulwark inflicts burn on contact.
- **Weather Ball:** doubles in power and changes type in weather (Fire in sun, Water in rain, Ice in hail/snow, Rock in sand). 100 BP in weather.
- **Electro Shot:** charges turn 1 (raising Sp.Atk), fires turn 2. In rain, fires immediately at full power — core of the Archaludon + Pelipper archetype.

### Ability interactions worth tracking
- **Hospitality (Sinistcha):** heals ally by 25% HP on switch-in — very powerful doubles support.
- **Moxie:** +1 Attack per KO — Gyarados and Kangaskhan snowball fast.
- **Stamina:** +1 Defense per hit taken — Archaludon becomes tankier as it takes hits.
- **Unburden:** doubles Speed when item is consumed/lost — Hawlucha with Flying Gem or Berry.
- **Speed Boost (Espathra):** +1 Speed at end of each turn — naturally accelerates without Tailwind.
- **Fairy Aura / Dark Aura (Xerneas/Yveltal mechanics):** multiplies power of Fairy/Dark moves for ALL pokemon on field, including opponent.

---

## What is Pokemon Champions

A custom Pokemon format on Pokemon Showdown. VGC doubles rules: bring 4 of 6 pokemon, pick 2 to lead each turn. Curated roster of ~52 pokemon. Mega evolutions are legal.

Two regulations currently active:
- **Season 1 — Reg M-A:** format ID `gen9championsvgc2026regma`
- **Season 2 — Reg M-B:** format ID `gen9championsvgc2026regmb`

Singles variant exists (`gen9championsbssregma`) but this project covers doubles only.

---

## Meta — Tournament Data (Reg M-A, Apr–May 2026)

Source: Limitless TCG API. **203 tournaments, 14,963 teams.**

### Top Pokemon by usage
| Pokemon | Usage % | Notes |
|---|---|---|
| Sneasler | 48.7% | #1 overall; Dire Claw / Close Combat / Fake Out |
| Garchomp | 39.8% | Earthquake + Dragon Claw spread |
| Incineroar | 35.7% | Parting Shot + Fake Out support |
| Kingambit | 32.8% | Leads 1st-place teams despite being 4th in usage |
| Basculegion | 31.6% | Last Respects win condition |
| Aerodactyl | 25.6% | Rock Slide spread, often lead |

Kingambit overperforms its usage rate — it appears on 1st-place teams more than anything else.

### Dominant core
**Sneasler + Kingambit + Basculegion + Garchomp** — trade aggressively, stack Last Respects, clean up with Kingambit priority.

Most common top-4 duos:
1. Kingambit + Sneasler (232)
2. Basculegion + Kingambit (209)
3. Basculegion + Sneasler (208)
4. Garchomp + Kingambit (193)

### Mega Evolutions
| Mega | Appearances |
|---|---|
| Charizard-Y | 2,650 |
| Floette-Eternal | 2,589 |
| Tyranitar | 1,552 |
| Froslass | 1,517 |
| Meganium | 1,177 |

Floette-Eternal appears on 30 first-place teams — well above its overall usage rate.

### Speed control split
- Tailwind: 10,176 uses
- Trick Room: 6,415 uses (~3:2 ratio)

### Top items
| Item | Count |
|---|---|
| Focus Sash | 12,024 |
| Sitrus Berry | 11,653 |
| Choice Scarf | 7,863 |
| White Herb | 7,833 |

White Herb at #4 almost certainly lives on Sneasler — use Close Combat, White Herb restores the defense drop.

---

## Meta — Replay Analysis (Reg M-A, 250 replays, May 2026)

Source: Showdown replay API. Run `analyze_replays.py` to regenerate.

### What wins

**Top pokemon by win rate (min 10 appearances):**
Oranguru 81% · Abomasnow 73% · Vivillon 71% · Palafin 71% · Meowscarada 68% · Excadrill 67% · Blastoise 63% · Tyranitar 60% · Corviknight 59%

**Top winning pairs (brought together):**
1. Archaludon + Pelipper (14x) — rain + Electro Shot, #1 archetype
2. Blastoise + Vivillon / Farigiraf / Politoed (8–9x each)
3. Excadrill + Tyranitar (9x) — sand core
4. Gengar + Incineroar (8x)

**Top megas on winning teams:** Blastoise · Charizard · Gengar · Floette · Lopunny

**Moves used significantly more by winners:**
| Move | Win-side % | Note |
|---|---|---|
| Muddy Water | 97% | Almost exclusively on winning teams |
| Water Spout | 91% | Blastoise/Basculegion full-HP nuke |
| Trick Room | 74% | Format is TR-tilted, winners set it more |
| Calm Mind / Shell Smash / Coil | 69–70% | Special/defensive setup wins |
| Body Press, Sludge Bomb, Bullet Punch | ~75% | |

**Moves used more by losers:**
- Draining Kiss 96% loss-side — gimmick that does not pay off
- Follow Me 96% loss-side — being punished, likely misused
- Rain Dance 76%, Dragon Claw 73%, Dire Claw 71%, Hydro Pump 67%

**Setup note:** Swords Dance (41% win rate) and Dragon Dance (40%) — physical setup gets countered before it fires. Calm Mind and Shell Smash win because they build defensive momentum too.

**Best leads (win rate, min 5 games led):**
Excadrill 88% · Lucario 83% · Meowscarada / Scizor / Oranguru 80% · Vivillon 75% · Blastoise 70%

**Sweepers (3+ KOs in one game):** Blastoise · Archaludon · Garchomp · Pelipper · Kangaskhan · Basculegion

### Team preview misplays

Pokemon benched far more by losers than winners — players bring them but misread when to play:

| Pokemon | Benched by losers | Benched by winners | Signal |
|---|---|---|---|
| Sneasler | 25x | 9x | Misread matchup |
| Aerodactyl | 22x | 9x | Brought speculatively |
| Garganacl | 7x | 0x | Never bench this |
| Aegislash | 8x | 5x | |
| Hatterene | 4x | 0x | Never bench this |
| Dragapult | 7x | 4x | |

11% of games end via early forfeit before turn 5. Bad team preview is the single most common loss condition.

### In-game misplays

- **Accuracy:** Losers miss 50% more than winners (78 vs 51 misses). Rock Slide causes 28 misses alone — the biggest accuracy gamble in the format.
- **Flinch:** Losers get flinched twice as much (99 vs 50). Rock Slide flinches swing games.
- **Timer:** 114 losing games vs 93 winning games had someone under 30 seconds. Decision speed is a real skill gap.
- **Protect:** ~1.1 attacks wasted into Protect per game, equally on both sides — unavoidable, not a differentiator.
- **Game length:** Average 7.1 turns. 16% of games end by turn 4 — blowouts are common.
