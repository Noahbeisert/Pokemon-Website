"""
Generates website/data/PredictData.json from BattleData.json + pokebase_champions.db.

BattleData.json (9 mons) has EV spreads, natures, items, abilities, moves with usage %.
DB has item/ability/move distributions for the full top-20+ from tournament data.

Output schema per pokemon slug:
  speeds   — list of {spe, label, pct} sorted by pct desc (empty if no spread data)
  topNature, topItem, topAbility — most common of each
  topMoves — top 4 move slugs
  items    — list of [slug, pct] top 5
  natures  — list of [slug, pct] top 3
"""

import sqlite3, json, math
from collections import defaultdict

DB = "pokebase_champions.db"
BATTLE_DATA = "../website/data/BattleData.json"
OUT = "../website/data/PredictData.json"

SPE_MULT = {
    "timid": 1.1, "jolly": 1.1, "hasty": 1.1, "naive": 1.1,
    "brave": 0.9, "quiet": 0.9, "relaxed": 0.9, "sassy": 0.9,
}

def norm(s):
    return s.lower().strip().replace(" ", "-").replace("'", "") if s else ""

def calc_spe(base, ev, nature):
    nm = SPE_MULT.get(nature, 1.0)
    return math.floor((math.floor((2 * base + 31) * 50 / 100) + 5) * nm) + ev

def pct(s):
    return float(str(s).strip("%"))

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

with open(BATTLE_DATA) as f:
    battle_data = json.load(f)

result = {}

# ── BattleData entries (full EV + nature data) ─────────────────────────────────
for entry in battle_data:
    slug = norm(entry["pokemon"])

    cur.execute("SELECT speed FROM pokemon WHERE slug=?", (slug,))
    row = cur.fetchone()
    if not row:
        cur.execute("SELECT speed FROM pokemon WHERE name=?", (entry["pokemon"],))
        row = cur.fetchone()
    if not row:
        print(f"  SKIP {slug} — not in DB")
        continue
    base_spe = row["speed"]

    natures = [(norm(n["name"]), pct(n["usage"])) for n in entry["nature"]]
    top_nature = natures[0][0] if natures else "none"

    # Compute speed for each EV spread using the top nature.
    # If the 2nd most common nature falls in a different speed bracket, add those too.
    speed_map = defaultdict(float)
    speed_labels = {}

    for spread in entry["ev_spreads"][:10]:
        ev = spread["spe"]
        u = pct(spread["usage"])
        spe = calc_spe(base_spe, ev, top_nature)
        speed_map[spe] += u
        if spe not in speed_labels:
            speed_labels[spe] = f"{top_nature.capitalize()}, {ev} Spe EVs"

    # Add a second nature tier if it gives a meaningfully different speed
    for nat, nat_pct in natures[1:4]:
        if SPE_MULT.get(nat, 1.0) == SPE_MULT.get(top_nature, 1.0):
            continue
        for spread in entry["ev_spreads"][:3]:
            ev = spread["spe"]
            u = pct(spread["usage"]) * nat_pct / 100
            spe = calc_spe(base_spe, ev, nat)
            speed_map[spe] += u
            if spe not in speed_labels:
                speed_labels[spe] = f"{nat.capitalize()}, {ev} Spe EVs"

    speeds = sorted(
        [{"spe": k, "label": speed_labels[k], "pct": round(v, 1)} for k, v in speed_map.items()],
        key=lambda x: -x["pct"],
    )[:6]

    items_raw = [(norm(i["name"]), pct(i["usage"])) for i in entry["items"]]
    abils_raw = [(norm(a["name"]), pct(a["usage"])) for a in entry["ability"]]
    moves_raw = [norm(m["name"]) for m in entry["moves"]]

    result[slug] = {
        "speeds":     speeds,
        "topNature":  top_nature,
        "topItem":    items_raw[0][0] if items_raw else "",
        "topAbility": abils_raw[0][0] if abils_raw else "",
        "topMoves":   moves_raw[:4],
        "items":      items_raw[:5],
        "natures":    [(n, round(p, 1)) for n, p in natures[:3]],
    }
    print(f"  {slug}: base_spe={base_spe}  top speeds={[s['spe'] for s in speeds[:3]]}")

# ── DB-only entries (items/abilities/moves, no spread data) ────────────────────
cur.execute("""
    SELECT tp.pokemon_slug, COUNT(DISTINCT tp.team_id) AS teams
    FROM team_pokemon tp
    GROUP BY tp.pokemon_slug
    ORDER BY teams DESC
    LIMIT 40
""")
top_db = [(r["pokemon_slug"], r["teams"]) for r in cur.fetchall()]

battle_slugs = set(result.keys())

for slug, teams in top_db:
    if slug in battle_slugs or teams < 400:
        continue

    cur.execute("SELECT speed FROM pokemon WHERE slug=?", (slug,))
    row = cur.fetchone()
    if not row:
        continue

    cur.execute("""
        SELECT item, COUNT(*) AS cnt FROM team_pokemon
        WHERE pokemon_slug=? AND item IS NOT NULL
        GROUP BY item ORDER BY cnt DESC LIMIT 5
    """, (slug,))
    items_db = [(norm(r["item"]), r["cnt"]) for r in cur.fetchall()]
    total = sum(c for _, c in items_db)
    items_pct = [(i, round(c / total * 100, 1)) for i, c in items_db] if total else []

    cur.execute("""
        SELECT ability, COUNT(*) AS cnt FROM team_pokemon
        WHERE pokemon_slug=? AND ability IS NOT NULL
        GROUP BY ability ORDER BY cnt DESC LIMIT 3
    """, (slug,))
    abils_db = [(norm(r["ability"]), r["cnt"]) for r in cur.fetchall()]
    total_a = sum(c for _, c in abils_db)
    abils_pct = [(a, round(c / total_a * 100, 1)) for a, c in abils_db] if total_a else []

    cur.execute("""
        SELECT tm.move_slug, COUNT(*) AS cnt
        FROM team_move tm
        JOIN team_pokemon tp ON tm.team_id=tp.team_id AND tm.position=tp.position
        WHERE tp.pokemon_slug=?
        GROUP BY tm.move_slug ORDER BY cnt DESC LIMIT 6
    """, (slug,))
    moves_db = [r["move_slug"] for r in cur.fetchall()]

    result[slug] = {
        "speeds":     [],
        "topNature":  None,
        "topItem":    items_pct[0][0] if items_pct else "",
        "topAbility": abils_pct[0][0] if abils_pct else "",
        "topMoves":   moves_db[:4],
        "items":      items_pct,
        "natures":    [],
    }
    print(f"  {slug}: DB-only ({teams} teams)")

conn.close()

with open(OUT, "w") as f:
    json.dump(result, f, indent=2)

print(f"\nWrote {len(result)} entries to {OUT}")
