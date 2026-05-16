"""
Extended replay analysis: win rates, move effectiveness, team preview misplays, in-game misplays.
"""
import json
import re
from collections import defaultdict, Counter
from itertools import combinations

with open("showdown_replays.json", encoding="utf-8") as f:
    replays = json.load(f)

TOTAL = len(replays)
print(f"Analyzing {TOTAL} replays\n")

SETUP_MOVES = {
    "Quiver Dance", "Dragon Dance", "Swords Dance", "Nasty Plot", "Calm Mind",
    "Bulk Up", "Coil", "Shell Smash", "Geomancy", "Agility", "Coaching",
    "Spicy Extract", "Competitive", "Speed Boost",
}

# ── Per-game tracking ─────────────────────────────────────────────────────────
pokemon_wins   = Counter()   # on winning team (preview)
pokemon_losses = Counter()   # on losing team (preview)
pokemon_appearances = Counter()

lead_wins   = Counter()
lead_losses = Counter()

brought_wins   = Counter()   # actually brought (of 6)
brought_losses = Counter()

benched_winners = Counter()  # left on bench by winner
benched_losers  = Counter()  # left on bench by loser
mega_capable    = set()      # pokemon that Mega Evolved at least once across all replays
mega_benched_winners = Counter()  # Mega-capable pokemon benched by winner
mega_benched_losers  = Counter()  # Mega-capable pokemon benched by loser

move_by_winner = Counter()
move_by_loser  = Counter()

winning_pairs = Counter()    # pairs of pokemon on winning teams (brought)

miss_by_move       = Counter()  # move → how many times it missed
protect_waste      = Counter()  # side (winner/loser) → attacks wasted into protect
double_protect_total = 0
sucker_punch_fails = 0
confusion_self_hits= 0
flinch_winner      = 0
flinch_loser       = 0
setup_winner       = Counter()  # setup moves completed by winners
setup_loser        = Counter()  # setup moves completed by losers
sweepers           = Counter()  # pokemon that got 3+ KOs
game_lengths       = []
early_forfeits     = 0
timer_pressure_winner = 0
timer_pressure_loser  = 0
miss_winner        = 0
miss_loser         = 0


def parse(log):
    lines = log.split("\n")

    # Teams from preview
    teams = {"p1": [], "p2": []}
    for l in lines:
        m = re.match(r"\|poke\|(p[12])\|([^,|]+)", l)
        if m:
            teams[m.group(1)].append(m.group(2).strip())

    # Player names
    players = {}
    for l in lines:
        m = re.match(r"\|player\|(p[12])\|([^|]+)", l)
        if m:
            players[m.group(1)] = m.group(2).strip()

    # Winner
    winner = None
    for l in lines:
        m = re.match(r"\|win\|(.+)", l)
        if m:
            winner = m.group(1).strip()

    # Mega Evolutions that actually happened this game (base form name)
    megas_used = {"p1": set(), "p2": set()}
    for l in lines:
        m = re.match(r"\|-mega\|(p[12])[ab]: [^|]+\|([^|]+)\|", l)
        if m:
            megas_used[m.group(1)].add(m.group(2).strip())

    # Pokemon brought (unique first-time switches after |start)
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
            side, mon = m.group(1), m.group(2).strip()
            if mon not in brought[side]:
                brought[side].append(mon)

    leads = {"p1": brought["p1"][:2], "p2": brought["p2"][:2]}

    # Moves by side — track last move per active slot for miss attribution
    moves_by_side = {"p1": [], "p2": []}
    last_move_by_slot = {}   # "p1a" → move name
    misses = []              # (attacker_side, move)

    for l in lines:
        m = re.match(r"\|move\|(p[12])([ab]): [^|]+\|([^|]+)\|", l)
        if m:
            side, slot, move = m.group(1), m.group(2), m.group(3).strip()
            moves_by_side[side].append(move)
            last_move_by_slot[side + slot] = move

        m2 = re.match(r"\|-miss\|(p[12])([ab]):", l)
        if m2:
            side, slot = m2.group(1), m2.group(2)
            move = last_move_by_slot.get(side + slot, "Unknown")
            misses.append((side, move))

    # Attacks wasted into protect — |-activate|pXY|move: Protect means attacker (other side) wasted a move
    protect_wasted = {"p1": 0, "p2": 0}
    for l in lines:
        m = re.match(r"\|-activate\|(p[12])[ab]: [^|]+\|move: Protect", l)
        if m:
            defender = m.group(1)
            attacker = "p2" if defender == "p1" else "p1"
            protect_wasted[attacker] += 1

    # Double protect — turns where both sides protect
    turn_protectors = defaultdict(set)
    cur_turn = 0
    for l in lines:
        m = re.match(r"\|turn\|(\d+)", l)
        if m:
            cur_turn = int(m.group(1))
        m2 = re.match(r"\|-singleturn\|(p[12])[ab]:", l)
        if m2 and "Protect" in l:
            turn_protectors[cur_turn].add(m2.group(1))
    double_protects = sum(1 for v in turn_protectors.values() if len(v) == 2)

    # Sucker Punch fails
    sucker_fails = sum(1 for l in lines if re.match(r"\|-fail\|[^|]+\|Sucker Punch", l))

    # Confusion self-hits
    conf_hits = sum(1 for l in lines if "|-damage|" in l and "[from] confusion" in l)

    # Flinches per side
    flinches = {"p1": 0, "p2": 0}
    for l in lines:
        m = re.match(r"\|cant\|(p[12])[ab]: [^|]+\|flinch", l)
        if m:
            flinches[m.group(1)] += 1

    # Setup moves completed (not failed, not into protect)
    setup_used = {"p1": [], "p2": []}
    for l in lines:
        m = re.match(r"\|move\|(p[12])[ab]: [^|]+\|([^|]+)\|", l)
        if m and m.group(2).strip() in SETUP_MOVES:
            setup_used[m.group(1)].append(m.group(2).strip())

    # Timer pressure
    timer = {"p1": 0, "p2": 0}
    for l in lines:
        m = re.match(r"\|inactive\|(.+) has (\d+) seconds left", l)
        if m:
            name, secs = m.group(1), int(m.group(2))
            if secs <= 30:
                for side, pname in players.items():
                    if pname == name:
                        timer[side] += 1

    # Sweepers: pokemon that dealt the killing blow to 3+ opponents
    last_attacker = {}   # slot → mon name
    faint_by = defaultdict(int)
    for l in lines:
        m = re.match(r"\|move\|(p[12])([ab]): ([^|]+)\|", l)
        if m:
            slot = m.group(1) + m.group(2)
            last_attacker[slot] = (m.group(1), m.group(3).strip())
        m2 = re.match(r"\|faint\|(p[12])([ab]):", l)
        if m2:
            dead_slot = m2.group(1) + m2.group(2)
            # The killing blow came from a pokemon on the other side
            for slot, (side, mon) in last_attacker.items():
                if side != m2.group(1):
                    faint_by[(side, mon)] += 1
                    break

    swept = [(side, mon) for (side, mon), n in faint_by.items() if n >= 3]

    # Game length
    last_turn = 0
    for l in lines:
        m = re.match(r"\|turn\|(\d+)", l)
        if m:
            last_turn = int(m.group(1))

    forfeit = any("forfeited" in l for l in lines)

    return {
        "teams": teams, "players": players, "winner": winner,
        "brought": brought, "leads": leads,
        "megas_used": megas_used,
        "moves_by_side": moves_by_side, "misses": misses,
        "protect_wasted": protect_wasted, "double_protects": double_protects,
        "sucker_fails": sucker_fails, "conf_hits": conf_hits,
        "flinches": flinches, "setup_used": setup_used,
        "timer": timer, "swept": swept,
        "last_turn": last_turn, "forfeit": forfeit,
        "early_forfeit": forfeit and last_turn < 5,
    }


for replay in replays:
    d = parse(replay["log"])
    if not d["winner"] or not d["players"]:
        continue

    winner_side = next((s for s, n in d["players"].items() if n == d["winner"]), None)
    if not winner_side:
        continue
    loser_side = "p2" if winner_side == "p1" else "p1"

    # ── Pokemon stats ──────────────────────────────────────────────────────────
    for mon in d["teams"][winner_side]:
        pokemon_wins[mon] += 1
        pokemon_appearances[mon] += 1
    for mon in d["teams"][loser_side]:
        pokemon_losses[mon] += 1
        pokemon_appearances[mon] += 1

    for mon in d["brought"][winner_side]:
        brought_wins[mon] += 1
    for mon in d["brought"][loser_side]:
        brought_losses[mon] += 1

    for mon in d["leads"][winner_side]:
        lead_wins[mon] += 1
    for mon in d["leads"][loser_side]:
        lead_losses[mon] += 1

    # Track which pokemon are Mega-capable (evolved at least once in any game)
    for side in ("p1", "p2"):
        mega_capable.update(d["megas_used"][side])

    bench_w = set(d["teams"][winner_side]) - set(d["brought"][winner_side])
    bench_l = set(d["teams"][loser_side]) - set(d["brought"][loser_side])
    for mon in bench_w:
        benched_winners[mon] += 1
        if mon in d["megas_used"][winner_side] or any(
            mon in d["megas_used"][s] for s in ("p1", "p2")
        ):
            mega_benched_winners[mon] += 1
    for mon in bench_l:
        benched_losers[mon] += 1
        if mon in d["megas_used"][loser_side] or any(
            mon in d["megas_used"][s] for s in ("p1", "p2")
        ):
            mega_benched_losers[mon] += 1

    # ── Winning pairs ──────────────────────────────────────────────────────────
    for pair in combinations(sorted(d["brought"][winner_side]), 2):
        winning_pairs[pair] += 1

    # ── Moves ─────────────────────────────────────────────────────────────────
    for mv in d["moves_by_side"][winner_side]:
        move_by_winner[mv] += 1
    for mv in d["moves_by_side"][loser_side]:
        move_by_loser[mv] += 1

    # ── Misplays ──────────────────────────────────────────────────────────────
    for side, move in d["misses"]:
        miss_by_move[move] += 1
        if side == winner_side:
            miss_winner += 1
        else:
            miss_loser += 1

    protect_waste["winner"] += d["protect_wasted"][winner_side]
    protect_waste["loser"]  += d["protect_wasted"][loser_side]
    double_protect_total    += d["double_protects"]
    sucker_punch_fails      += d["sucker_fails"]
    confusion_self_hits     += d["conf_hits"]
    flinch_winner           += d["flinches"][winner_side]
    flinch_loser            += d["flinches"][loser_side]

    for mv in d["setup_used"][winner_side]:
        setup_winner[mv] += 1
    for mv in d["setup_used"][loser_side]:
        setup_loser[mv] += 1

    if d["timer"][winner_side] > 0:
        timer_pressure_winner += 1
    if d["timer"][loser_side] > 0:
        timer_pressure_loser += 1

    for side, mon in d["swept"]:
        sweepers[mon] += 1

    if d["early_forfeit"]:
        early_forfeits += 1
    if d["last_turn"] > 0:
        game_lengths.append(d["last_turn"])


# ── Helper ────────────────────────────────────────────────────────────────────
def win_rate(wins, losses, min_games=10):
    results = {}
    for mon in set(wins) | set(losses):
        w, l = wins[mon], losses[mon]
        if w + l >= min_games:
            results[mon] = (w / (w + l), w + l)
    return results

def sep(title):
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}")


# ══ POKEMON WIN RATES ════════════════════════════════════════════════════════
sep("POKEMON WIN RATES  (min 10 appearances in team preview)")
rates = win_rate(pokemon_wins, pokemon_losses)
for mon, (wr, total) in sorted(rates.items(), key=lambda x: -x[1][0])[:25]:
    bar = "█" * int(wr * 20)
    print(f"  {mon:<26} {wr*100:5.1f}%  n={total:<4}  {bar}")

# ══ BRING RATE vs WIN RATE ═══════════════════════════════════════════════════
sep("BRING RATE  — how often is each pokemon actually brought (of 6)?")
print(f"  {'Pokemon':<26} {'Bring%':>7}  {'WinRate':>7}  {'n':>5}")
print(f"  {'-'*55}")
bring_rates = {}
for mon in set(brought_wins) | set(brought_losses):
    bw = brought_wins[mon]
    bl = brought_losses[mon]
    total_preview = pokemon_appearances[mon]
    if total_preview >= 10:
        bring_pct = (bw + bl) / total_preview
        win_pct   = bw / (bw + bl) if (bw + bl) > 0 else 0
        bring_rates[mon] = (bring_pct, win_pct, total_preview)

for mon, (bp, wp, n) in sorted(bring_rates.items(), key=lambda x: -x[1][0])[:20]:
    print(f"  {mon:<26} {bp*100:6.1f}%  {wp*100:6.1f}%  {n:>5}")

# ══ TEAM PREVIEW MISPLAYS ════════════════════════════════════════════════════
sep("TEAM PREVIEW — what do LOSERS leave on the bench vs WINNERS?")
print("  Pokemon benched often by losers but rarely by winners = likely misplay")
print("  [M] = Mega-capable: benching may be intentional (running 2 Megas, chose the other)")
print(f"\n  {'':3} {'Pokemon':<23} {'Benched losers':>15}  {'Benched winners':>15}  {'Diff':>6}  Note")
print(f"  {'-'*82}")
all_bench = set(benched_losers) | set(benched_winners)
bench_diff = []
for mon in all_bench:
    bl = benched_losers[mon]
    bw = benched_winners[mon]
    total = pokemon_appearances[mon]
    if total < 8:
        continue
    bl_rate = bl / total
    bw_rate = bw / total
    bench_diff.append((mon, bl, bw, bl_rate - bw_rate))

for mon, bl, bw, diff in sorted(bench_diff, key=lambda x: -x[3])[:20]:
    is_mega = mon in mega_capable
    tag = "[M]" if is_mega else "   "
    if is_mega and diff > 0.15:
        note = "Mega matchup choice — not necessarily a misplay"
    elif diff > 0.15:
        note = "likely misplay"
    else:
        note = ""
    print(f"  {tag} {mon:<23}  {bl:>10}x        {bw:>10}x      {diff:+.2f}  {note}")

# ══ LEAD WIN RATES ═══════════════════════════════════════════════════════════
sep("LEAD WIN RATES  (min 5 times led)")
rates = win_rate(lead_wins, lead_losses, min_games=5)
for mon, (wr, total) in sorted(rates.items(), key=lambda x: -x[1][0])[:20]:
    print(f"  {mon:<26} {wr*100:5.1f}%  led {total}x")

# ══ MOVE WIN RATES ═══════════════════════════════════════════════════════════
sep("MOVE WIN RATES  — moves used more by winners than losers (min 15 uses)")
all_moves = set(move_by_winner) | set(move_by_loser)
move_rates = []
for mv in all_moves:
    w = move_by_winner[mv]
    l = move_by_loser[mv]
    if w + l >= 15:
        move_rates.append((mv, w / (w + l), w + l))

print(f"\n  Best moves (winners use them more):")
for mv, wr, total in sorted(move_rates, key=lambda x: -x[1])[:15]:
    print(f"  {mv:<28} {wr*100:5.1f}% win-side  ({total} uses)")

print(f"\n  Worst moves (losers use them more):")
for mv, wr, total in sorted(move_rates, key=lambda x: x[1])[:10]:
    print(f"  {mv:<28} {(1-wr)*100:5.1f}% loss-side ({total} uses)")

# ══ WINNING PAIRS ════════════════════════════════════════════════════════════
sep("TOP WINNING POKEMON PAIRS  (brought together on winning team)")
for pair, count in winning_pairs.most_common(15):
    print(f"  {pair[0]} + {pair[1]:<30}  {count}x")

# ══ SETUP MOVES ══════════════════════════════════════════════════════════════
sep("SETUP MOVES  — completed by winners vs losers")
all_setup = set(setup_winner) | set(setup_loser)
print(f"  {'Move':<22} {'By winner':>10}  {'By loser':>9}  {'Win%':>6}")
for mv in sorted(all_setup, key=lambda m: -(setup_winner[m] + setup_loser[m])):
    w, l = setup_winner[mv], setup_loser[mv]
    if w + l < 5:
        continue
    print(f"  {mv:<22}  {w:>9}x  {l:>8}x  {w/(w+l)*100:>5.0f}%")

# ══ SWEEPERS ═════════════════════════════════════════════════════════════════
sep("SWEEPERS  — pokemon that knocked out 3+ opponents in one game")
for mon, count in sweepers.most_common(15):
    print(f"  {mon:<28}  {count}x")

# ══ IN-GAME MISPLAYS ═════════════════════════════════════════════════════════
sep("IN-GAME MISPLAYS")

avg_turns = sum(game_lengths) / len(game_lengths) if game_lengths else 0
short_games = sum(1 for t in game_lengths if t <= 4)

print(f"\n  Game length")
print(f"    Average turns:              {avg_turns:.1f}")
print(f"    Games decided by turn 4:   {short_games} ({short_games/TOTAL*100:.1f}%)")

print(f"\n  Team preview")
print(f"    Early forfeits (<t5):      {early_forfeits} ({early_forfeits/TOTAL*100:.1f}%) — opponent read team wrong")

print(f"\n  Protect misuse")
print(f"    Attacks into protect:")
print(f"      By eventual winner:       {protect_waste['winner']} ({protect_waste['winner']/TOTAL:.2f}/game)")
print(f"      By eventual loser:        {protect_waste['loser']} ({protect_waste['loser']/TOTAL:.2f}/game)")
print(f"    Both players protecting same turn: {double_protect_total} ({double_protect_total/TOTAL:.2f}/game)")

print(f"\n  Accuracy failures")
print(f"    Total misses:              {miss_winner + miss_loser} ({(miss_winner+miss_loser)/TOTAL:.2f}/game)")
print(f"      By eventual winner:       {miss_winner}")
print(f"      By eventual loser:        {miss_loser}")
print(f"\n    Misses per move:")
for mv, count in miss_by_move.most_common(12):
    print(f"      {mv:<28}  {count}x")

print(f"\n  Move-specific misplays")
print(f"    Sucker Punch fails:         {sucker_punch_fails} ({sucker_punch_fails/TOTAL:.2f}/game)")
print(f"    Confusion self-hits:        {confusion_self_hits} ({confusion_self_hits/TOTAL:.2f}/game)")

print(f"\n  Flinch impact")
print(f"    Winners lost to flinch:     {flinch_winner}x")
print(f"    Losers lost to flinch:      {flinch_loser}x")

print(f"\n  Timer pressure (under 30s at some point)")
print(f"    Winners time-pressured:     {timer_pressure_winner} games")
print(f"    Losers time-pressured:      {timer_pressure_loser} games")
