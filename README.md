# Pokemon Champions VGC Toolkit

A VGC Doubles analysis toolkit: tournament data pipeline, meta analysis, and in-browser tools for competitive play. Doubles format only (bring 4 of 6, pick 2 each turn).

See **[CHAMPIONS.md](CHAMPIONS.md)** for format info, meta insights, and game mechanics.
See **[PLAN.md](pokemon/PLAN.md)** for website implementation plans and future work.

---

## Project Structure

```
pokemon/
├── website/                      ← Pure frontend — HTML + CSS + JS, no backend
│   ├── index.html
│   ├── type-chart.html
│   ├── type-chart-advanced.html
│   ├── damage-calc.html
│   ├── pokeplan.html
│   ├── css/                      ← Per-page stylesheets
│   ├── js/                       ← Per-page JavaScript
│   └── data/
│       └── BattleData.json
└── scraper/                      ← Python data pipeline
    ├── scrape_limitless.py       ← Tournament data from Limitless TCG API
    ├── scrape_pokemon.py         ← Pokemon base stats + types from PokeAPI
    ├── scrape_moves.py           ← Move data + flags from PokeAPI
    ├── scrape_items.py           ← Item data from PokeAPI
    ├── scrape_tournaments.py     ← Tournament data from pokebase.app (RSC payload)
    ├── scrape_replays.py         ← Showdown replay logs for both regulations
    ├── analyze_replays.py        ← Win rates, misplay detection, pair analysis
    ├── schema.sql                ← SQLite schema reference
    ├── pokebase_champions.db     ← Local DB (not committed — run scrapers)
    ├── showdown_replays.json     ← Replay log data (not committed — run scraper)
    └── tournament_teams.json     ← pokebase.app team data
```

---

## Data Sources

### Limitless TCG API
Base: `https://play.limitlesstcg.com/api` — public, no key required.

| Endpoint | Returns |
|---|---|
| `GET /tournaments?game=VGC&format=M-A` | Paginated tournament list |
| `GET /tournaments/{id}/details` | Organizer, platform, decklists flag |
| `GET /tournaments/{id}/standings` | All players: placing, record, full 6-mon team |

Rate limit: ~100 req/min. Scraper uses 2s delays + exponential backoff on 429s.

### Pokemon Showdown Replay API
No auth required.

```
# Paginated replay list — 51/page, hard cap at page 100 (5100 replays max per format)
GET https://replay.pokemonshowdown.com/search.json?format=FORMAT&page=N

# Full replay JSON (includes full battle log)
GET https://replay.pokemonshowdown.com/REPLAYID.json
```

Format IDs: `gen9championsvgc2026regma` (season 1), `gen9championsvgc2026regmb` (season 2)

### PokeAPI
`https://pokeapi.co` — public, free, no auth. Used for pokemon stats, move data, and move flags (sound, contact, spread, punch, protect, bullet).

### pokebase.app
`https://pokebase.app/pokemon-champions` — scraped via Next.js RSC payload (no JS execution needed).

---

## Running the Scrapers

All scripts run from `pokemon/scraper/`. Use the PycharmProjects Pokemon venv — it has `requests` installed:
```
C:\Users\Admin\PycharmProjects\Pokemon\.venv\Scripts\python.exe SCRIPT.py
```

```bash
# Tournament data
python scrape_limitless.py --format M-A

# Base data
python scrape_pokemon.py
python scrape_moves.py
python scrape_items.py

# Showdown replays (resume-safe — re-run skips already-fetched IDs)
python scrape_replays.py

# Meta analysis
python analyze_replays.py
```

---

## Database Schema

| Table | Description |
|---|---|
| `tournaments` | id, name, date, num_players, limitless_id |
| `teams` | id, tournament_id, player, placing, W/L/T |
| `team_pokemon` | team_id, position (0–5), pokemon_slug, ability, item, tera_type |
| `team_move` | team_id, position, move_slug |
| `pokemon` | slug, name, types (JSON), base stats, image_url |
| `moves` | slug, name, type, power, accuracy, PP, flags (JSON) |
| `items` | slug, name, category, description |

See `schema.sql` for full definition.

---

## Frontend Design System

All pages share:
```css
--bg:      #0d0f14   /* page background */
--surface: #161a23   /* cards */
--accent:  #7c6af7   /* highlights */
font-family: 'Rajdhani' (headings), 'Inter' (body)
```

`pokeplan.html` uses dual-color: `--player: #4cc9f0` (cyan) vs `--enemy: #f72585` (magenta).
`damage-calc.html` uses `--accent: #7c83fd` with a minified system-ui stylesheet.
