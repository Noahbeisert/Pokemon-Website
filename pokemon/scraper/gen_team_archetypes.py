"""
Generates website/data/TeamArchetypes.json from pokebase_champions.db.

Groups the 43k tournament teams into unique 6-mon compositions so the team
preview can match an entered team against real archetypes and read off the
actual sets (item / ability / moves / roles) those teams ran, instead of
species-wide averages.

Output (string tables keep the file small — everything references ids):
  mons   — id → pokemon slug (mega forms normalized to base)
  moves  — id → move slug
  items  — id → item name
  abils  — id → ability name
  roles  — id → role tag
  stones — stone item name (lowercase) → base pokemon slug
  comps  — [{m: [6 mon ids, sorted], n: team count,
             s: {monId: [ {mv:[moveIds], it:itemId, ab:abilId, r:[roleIds], n:count}, ... ]}}]
           `s` only present for comps with n >= MIN_DETAIL; sets sorted by
           count desc, top MAX_SETS_PER_MON kept.
"""

import sqlite3, json
from collections import Counter, defaultdict

from gen_common import derive_roles, item_to_stone_slug, build_megastone_map

DB = "pokebase_champions.db"
OUT = "../website/data/TeamArchetypes.json"
MIN_DETAIL = 2          # comps seen fewer times than this carry no set details
MAX_SETS_PER_MON = 3
SET_MIN_SHARE = 0.10    # drop sets under 10% of the comp's teams

MEGA_SUFFIXES = ("-mega-x", "-mega-y", "-mega")


def base_form(slug):
    for suffix in MEGA_SUFFIXES:
        if slug.endswith(suffix):
            return slug[: -len(suffix)]
    return slug


conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

team_moves_by_slot = defaultdict(list)
for r in conn.execute("SELECT team_id, position, move_slug FROM team_move"):
    team_moves_by_slot[(r["team_id"], r["position"])].append(r["move_slug"])

# team_id -> [(slug, item, ability, moves_sig)]
teams = defaultdict(list)
for r in conn.execute("SELECT team_id, position, pokemon_slug, item, ability FROM team_pokemon"):
    moves = tuple(sorted(team_moves_by_slot.get((r["team_id"], r["position"]), ())))
    teams[r["team_id"]].append((base_form(r["pokemon_slug"]), r["item"], r["ability"], moves))

# comp (sorted slug tuple) -> per-mon Counter of (moves, item, ability)
comp_count = Counter()
comp_sets = defaultdict(lambda: defaultdict(Counter))
for members in teams.values():
    comp = tuple(sorted(m[0] for m in members))
    if len(comp) != 6:
        continue
    comp_count[comp] += 1
    for slug, item, ability, moves in members:
        comp_sets[comp][slug][(moves, item or "", ability or "")] += 1

# ── String tables ─────────────────────────────────────────────────────────────
def interner():
    table = {}
    def intern(s):
        if s not in table:
            table[s] = len(table)
        return table[s]
    return table, intern

mon_tab,  mon_id  = interner()
move_tab, move_id = interner()
item_tab, item_id = interner()
abil_tab, abil_id = interner()
role_tab, role_id = interner()

comps_out = []
for comp, n in sorted(comp_count.items(), key=lambda kv: -kv[1]):
    entry = {"m": sorted(mon_id(s) for s in comp), "n": n}
    if n >= MIN_DETAIL:
        details = {}
        for slug, sets in comp_sets[comp].items():
            out_sets = []
            for (moves, item, ability), cnt in sets.most_common(MAX_SETS_PER_MON):
                if cnt / n < SET_MIN_SHARE or not moves:
                    continue
                roles = derive_roles(moves, ability, item)
                out_sets.append({
                    "mv": [move_id(m) for m in moves],
                    "it": item_id(item),
                    "ab": abil_id(ability),
                    "r":  sorted(role_id(x) for x in roles),
                    "n":  cnt,
                })
            if out_sets:
                details[str(mon_id(slug))] = out_sets
        if details:
            entry["s"] = details
    comps_out.append(entry)

stones = {slug: base for slug, base in build_megastone_map(conn).items()}
conn.close()


def table_list(tab):
    return [s for s, _ in sorted(tab.items(), key=lambda kv: kv[1])]

result = {
    "mons":   table_list(mon_tab),
    "moves":  table_list(move_tab),
    "items":  table_list(item_tab),
    "abils":  table_list(abil_tab),
    "roles":  table_list(role_tab),
    "stones": stones,
    "comps":  comps_out,
}

with open(OUT, "w") as f:
    json.dump(result, f, separators=(",", ":"))

detailed = sum(1 for c in comps_out if "s" in c)
import os
print(f"Wrote {len(comps_out)} comps ({detailed} with set details), "
      f"{os.path.getsize(OUT) / 1e6:.1f} MB")
