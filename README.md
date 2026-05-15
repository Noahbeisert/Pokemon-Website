# Pokemon Champions VGC Toolkit

A VGC Doubles analysis toolkit: tournament data pipeline, meta analysis, and a set of in-browser tools for competitive play. Format scope is **Pokemon Champions Doubles only** (bring 4 of 6, pick 2 each turn).

---

## Project Structure

```
pokemon/
├── website/                      ← Pure frontend — HTML + CSS + JS, no backend
│   ├── index.html                ← Navigation hub
│   ├── type-chart.html           ← Type matchup lookup by type or Pokémon name
│   ├── type-chart-advanced.html  ← Same + learnset-aware move lookup via GraphQL
│   ├── damage-calc.html          ← Damage rolls, KO %, stat spreads
│   ├── pokeplan.html             ← Full team planner with enemy scout + save/load
│   ├── css/                      ← Per-page stylesheets (extracted from inline)
│   │   ├── type-chart.css
│   │   ├── type-chart-advanced.css
│   │   ├── damage-calc.css
│   │   └── pokeplan.css
│   ├── js/                       ← Per-page JavaScript (extracted from inline)
│   │   ├── type-chart.js
│   │   ├── type-chart-advanced.js
│   │   ├── damage-calc.js
│   │   └── pokeplan.js
│   └── data/
│       └── BattleData.json
└── scraper/                      ← Python data pipeline → SQLite
    ├── scrape_limitless.py       ← Tournament data from Limitless TCG API
    ├── scrape_pokemon.py         ← Pokémon base stats + types from PokeAPI
    ├── scrape_moves.py           ← Move data from PokeAPI
    ├── scrape_items.py           ← Item data from PokeAPI
    ├── scrape_tournaments.py     ← Tournament data from pokebase.app (RSC payload)
    ├── analyze.py                ← Meta analysis queries against the DB
    ├── schema.sql                ← SQLite schema reference
    └── pokebase_champions.db     ← Local database (not committed — run scrapers)
```

---

## Data Sources

### Limitless TCG API — tournament data

Base URL: `https://play.limitlesstcg.com/api`

Public API, no key required. Endpoints used:

| Endpoint | Returns |
|---|---|
| `GET /tournaments?game=VGC&format=M-A` | Paginated list of tournaments |
| `GET /tournaments/{id}/details` | Organizer, platform, `decklists` flag |
| `GET /tournaments/{id}/standings` | All players: placing, record, full 6-mon team |

Each standing entry includes the full team sheet: Pokémon slug, item, ability, 4 moves, and tera type. No EVs/IVs (not submitted in-game).

Rate limit: ~100 req/min unauthenticated. The scraper uses 2s delays + exponential backoff on 429s.

### PokeAPI — Pokémon / move / item data

`https://pokeapi.co` — public, free, no auth.

### pokebase.app — curated tournament highlights

`https://pokebase.app/pokemon-champions` — scraped via Next.js RSC payload parsing (no JS execution needed).

---

## Running the Scrapers

All scripts run from `pokemon/scraper/`. The DB is created automatically if it doesn't exist.

```bash
cd pokemon/scraper

# Fetch all public Pokemon Champions (M-A) tournament data
python scrape_limitless.py --format M-A

# Fetch only current regulation, skip already-scraped tournaments (default)
python scrape_limitless.py --format M-A

# Re-import everything (useful after schema changes)
python scrape_limitless.py --format M-A --refetch

# Count without writing to DB
python scrape_limitless.py --format M-A --dry-run

# Pokémon / move / item base data
python scrape_pokemon.py
python scrape_moves.py
python scrape_items.py
```

The scraper is resumable — re-running skips tournaments already in the DB.

---

## Meta Insights — Regulation M-A (as of May 2026)

Data from **203 tournaments**, **14,963 teams**, **Apr–May 2026**.

### Top Pokémon by usage
| Pokémon | Usage % | Notes |
|---|---|---|
| Sneasler | 48.7% | #1 overall; Dire Claw / Close Combat / Fake Out core |
| Garchomp | 39.8% | Earthquake + Dragon Claw spread |
| Incineroar | 35.7% | Parting Shot + Fake Out support |
| Kingambit | 32.8% | **Leads 1st-place teams** despite being 4th in usage |
| Basculegion | 31.6% | Last Respects win condition |
| Aerodactyl | 25.6% | Rock Slide spread, often lead |

Kingambit notably **overperforms its usage rate** — it appears on 1st-place teams more than anything else despite not being the most used Pokémon overall.

### The dominant core

**Sneasler + Kingambit + Basculegion + Garchomp** is the format's central quartet. Win condition: trade aggressively, stack Last Respects stacks on Basculegion, clean up with Kingambit's priority (Sucker Punch / Kowtow Cleave).

Most common top-4 duos:
1. Kingambit + Sneasler (232)
2. Basculegion + Kingambit (209)
3. Basculegion + Sneasler (208)
4. Garchomp + Kingambit (193)

### Mega Evolutions are legal

| Mega | Appearances |
|---|---|
| Charizard-Y (Charizardite Y) | 2,650 |
| Floette-Eternal (Floettite) | 2,589 |
| Tyranitar (Tyranitarite) | 1,552 |
| Froslass (Froslassite) | 1,517 |
| Meganium (Meganiumite) | 1,177 |

Floette-Eternal appears on 30 first-place teams — punching well above its overall usage.

### Speed control split

- Tailwind: 10,176 uses
- Trick Room: 6,415 uses

Tailwind outnumbers TR ~3:2. The format skews faster but TR is prevalent enough to warrant specific counterplay.

### Rain is a real archetype

Pelipper + Archaludon is the 12th most common top-4 duo (106 appearances) — a fully fleshed-out alternative to the hyper-offense core.

### Top items
| Item | Count |
|---|---|
| Focus Sash | 12,024 |
| Sitrus Berry | 11,653 |
| Choice Scarf | 7,863 |
| White Herb | 7,833 |

White Herb at #4 almost certainly lives on Sneasler: use Close Combat, White Herb restores the defense drop, maintain bulk.

---

## Database Schema

Key tables (see `schema.sql` for full definition):

| Table | Description |
|---|---|
| `tournaments` | id, name, date, num_players, limitless_id |
| `teams` | id, tournament_id, player, player_name, country, placing, W/L/T, drop_round |
| `team_pokemon` | team_id, position (0–5), pokemon_slug, ability, item, tera_type |
| `team_move` | team_id, position (Pokémon slot), move_slug |
| `pokemon` | slug, name, types (JSON), base stats, image_url |
| `moves` | slug, name, type, power, accuracy, PP, description |
| `items` | slug, name, category, description |

---

## Frontend Design System

All pages share this design language (defined per-page in `css/`):

```css
--bg:      #0d0f14   /* page background */
--surface: #161a23   /* cards */
--accent:  #7c6af7   /* highlights */
font-family: 'Rajdhani' (headings), 'Inter' (body)
```

`pokeplan.html` uses a dual-color scheme: `--player: #4cc9f0` (cyan) vs `--enemy: #f72585` (magenta).

`damage-calc.html` uses `--accent: #7c83fd` with a minified system-ui stylesheet.

See `PLAN.md` for the full design spec, lead/bring prediction algorithms, and page-level implementation notes.
