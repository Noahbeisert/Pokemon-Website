"""
Generates website/data/BringRates.json from showdown_replays.json.

Output per pokemon slug:
  appearances  — times seen at team preview
  brought      — times actually used in battle
  led          — times started as one of the two leads
  bring_rate   — brought / appearances
  lead_rate    — led / brought  (when brought, how often does it lead?)
  lead_win_rate— (led + won) / led  (win rate when leading)

Only includes pokemon with >= MIN_APP appearances to filter noise.
"""

import json, re
from collections import defaultdict

REPLAYS = "showdown_replays.json"
OUT     = "../website/data/BringRates.json"
MIN_APP = 5   # min preview appearances to include

def norm(name):
    slug = name.lower().strip().replace(" ", "-").replace("'", "").replace(".", "")
    # Strip cosmetic-only form suffixes that aren't in the profiles
    for suffix in ("-masterpiece", "-fancy", "-sun", "-rainbow-swirl", "-mint-cream"):
        if slug.endswith(suffix):
            slug = slug[: -len(suffix)]
            break
    return slug

def parse_replay(log):
    lines = log.split("\n")

    teams = {"p1": [], "p2": []}
    for l in lines:
        m = re.match(r"\|poke\|(p[12])\|([^,|]+)", l)
        if m:
            teams[m.group(1)].append(norm(m.group(2)))

    players = {}
    for l in lines:
        m = re.match(r"\|player\|(p[12])\|([^|]+)", l)
        if m:
            players[m.group(1)] = m.group(2).strip()

    winner = None
    for l in lines:
        m = re.match(r"\|win\|(.+)", l)
        if m:
            winner = m.group(1).strip()

    brought = {"p1": [], "p2": []}
    started = False
    for l in lines:
        if l == "|start":
            started = True
            continue
        if not started:
            continue
        m = re.match(r"\|switch\|(p[12])[ab]: [^|]+\|([^,|]+)", l)
        if m:
            side, mon = m.group(1), norm(m.group(2))
            if mon not in brought[side]:
                brought[side].append(mon)

    leads = {"p1": brought["p1"][:2], "p2": brought["p2"][:2]}

    winner_side = None
    if winner:
        for side, name in players.items():
            if name == winner:
                winner_side = side

    return teams, brought, leads, winner_side


with open(REPLAYS, encoding="utf-8") as f:
    replays = json.load(f)

appearances = defaultdict(int)
brought_cnt = defaultdict(int)
led_cnt     = defaultdict(int)
led_won_cnt = defaultdict(int)

for r in replays:
    teams, brought, leads, winner_side = parse_replay(r["log"])
    if not winner_side:
        continue

    for side in ("p1", "p2"):
        won = (side == winner_side)
        for mon in teams[side]:
            appearances[mon] += 1
        for mon in brought[side]:
            brought_cnt[mon] += 1
        for mon in leads[side]:
            led_cnt[mon] += 1
            if won:
                led_won_cnt[mon] += 1

result = {}
for mon in appearances:
    app = appearances[mon]
    if app < MIN_APP:
        continue
    br  = brought_cnt.get(mon, 0)
    ld  = led_cnt.get(mon, 0)
    lw  = led_won_cnt.get(mon, 0)
    result[mon] = {
        "appearances":   app,
        "brought":       br,
        "led":           ld,
        "bring_rate":    round(br / app, 3) if app else 0,
        "lead_rate":     round(ld / br,  3) if br else 0,
        "lead_win_rate": round(lw / ld,  3) if ld else 0,
    }

with open(OUT, "w") as f:
    json.dump(result, f, indent=2)

print(f"Wrote {len(result)} entries (from {len(replays)} replays)")

# Show top 15 by bring rate for sanity check
top = sorted(result.items(), key=lambda x: -x[1]["bring_rate"])[:15]
for slug, d in top:
    print(f"  {slug:<28} bring={d['bring_rate']:.0%}  lead={d['lead_rate']:.0%}  n={d['appearances']}")
