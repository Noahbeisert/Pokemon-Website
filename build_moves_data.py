#!/usr/bin/env python3
"""
Parse PS moves.ts into moves_data.json.
Contains everything needed for the battle-data tooltip: power, accuracy,
category, type, target, priority, flags, secondary effects, drain, recoil, multihit.
Replaces the PokeAPI approach for move tooltips.
"""

import json, re, sys, requests

PS_MOVES_URL = "https://raw.githubusercontent.com/smogon/pokemon-showdown/master/data/moves.ts"

RELEVANT_FLAGS = {'contact', 'bullet', 'sound', 'punch', 'slicing', 'dance', 'powder'}

STATUS_NAMES = {
    'brn': 'burn', 'frz': 'freeze', 'par': 'paralysis',
    'psn': 'poison', 'tox': 'toxic', 'slp': 'sleep',
}
VOLATILE_NAMES = {
    'flinch': 'flinch', 'confusion': 'confusion', 'attract': 'attract',
    'partiallytrapped': 'trapped',
}
STAT_NAMES = {
    'atk': 'Atk', 'def': 'Def', 'spa': 'SpA', 'spd': 'SpD',
    'spe': 'Spe', 'accuracy': 'Accuracy', 'evasion': 'Evasion',
}

def pokeapi_slug(name):
    return re.sub(r'[^a-z0-9-]', '', name.lower().replace(' ', '-'))

def extract_inner_block(text, key):
    """Extract content of key: { ... } handling nested braces."""
    m = re.search(rf'\b{key}:\s*\{{', text)
    if not m:
        return None
    depth = 0
    for i in range(m.end() - 1, len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                return text[m.end():i]
    return None

def parse_boosts(block):
    if not block:
        return {}
    return {k: int(v) for k, v in re.findall(r'(\w+):\s*(-?\d+)', block)}

def secondary_desc(sec_block):
    if not sec_block:
        return None
    chance_m = re.search(r'\bchance:\s*(\d+)', sec_block)
    chance = int(chance_m.group(1)) if chance_m else None
    pfx = f"{chance}% " if chance else ""

    parts = []
    status_m = re.search(r'\bstatus:\s*[\'"](\w+)[\'"]', sec_block)
    if status_m:
        parts.append(f"{pfx}{STATUS_NAMES.get(status_m.group(1), status_m.group(1))}")

    vol_m = re.search(r'\bvolatileStatus:\s*[\'"](\w+)[\'"]', sec_block)
    if vol_m:
        parts.append(f"{pfx}{VOLATILE_NAMES.get(vol_m.group(1), vol_m.group(1))}")

    boosts_block = extract_inner_block(sec_block, 'boosts')
    for stat, val in parse_boosts(boosts_block).items():
        parts.append(f"{pfx}{'↑' if val > 0 else '↓'}{abs(val)} {STAT_NAMES.get(stat, stat)}")

    self_block = extract_inner_block(sec_block, 'self')
    self_boosts_block = extract_inner_block(self_block, 'boosts') if self_block else None
    for stat, val in parse_boosts(self_boosts_block).items():
        parts.append(f"{pfx}{'↑' if val > 0 else '↓'}{abs(val)} {STAT_NAMES.get(stat, stat)} (self)")

    return ', '.join(parts) if parts else None

def parse_block(block):
    name_m = re.search(r'\bname:\s*"([^"]+)"', block) or re.search(r"\bname:\s*'([^']+)'", block)
    if not name_m:
        return None, None
    name = name_m.group(1)

    def get_int(key):
        m = re.search(rf'\b{key}:\s*(-?\d+)', block)
        return int(m.group(1)) if m else None

    def get_str(key):
        m = re.search(rf'\b{key}:\s*[\'"]([^\'"]+)[\'"]', block)
        return m.group(1) if m else None

    acc_m = re.search(r'\baccuracy:\s*(true|\d+)', block)
    accuracy = None if not acc_m or acc_m.group(1) == 'true' else int(acc_m.group(1))

    power = get_int('basePower') or None
    category = get_str('category')
    move_type = get_str('type')
    target = get_str('target')
    priority = get_int('priority')

    flags_block = extract_inner_block(block, 'flags')
    flags = sorted(set(re.findall(r'(\w+):\s*1', flags_block or '')) & RELEVANT_FLAGS)

    # Secondary / secondaries
    if re.search(r'\bsecondary:\s*null\b', block):
        sec = None
    else:
        sec_block = extract_inner_block(block, 'secondary')
        sec = secondary_desc(sec_block)

    # Drain / recoil (stored as [numerator, denominator])
    drain_m = re.search(r'\bdrain:\s*\[(\d+),\s*(\d+)\]', block)
    drain = round(int(drain_m.group(1)) / int(drain_m.group(2)) * 100) if drain_m else None

    recoil_m = re.search(r'\brecoil:\s*\[(\d+),\s*(\d+)\]', block)
    recoil = round(int(recoil_m.group(1)) / int(recoil_m.group(2)) * 100) if recoil_m else None

    # Multi-hit
    mh_m = re.search(r'\bmultihit:\s*(\[[\d,\s]+\]|\d+)', block)
    multihit = None
    if mh_m:
        val = mh_m.group(1).strip()
        if val.startswith('['):
            nums = list(map(int, re.findall(r'\d+', val)))
            multihit = f"{nums[0]}-{nums[1]}" if len(nums) >= 2 else str(nums[0])
        else:
            multihit = val

    crit_m = re.search(r'\bcritRatio:\s*(\d+)', block)
    high_crit = bool(crit_m and int(crit_m.group(1)) >= 2)

    # shortDesc uses double quotes and may contain apostrophes — use a quote-aware regex
    desc_m = re.search(r'\bshortDesc:\s*"([^"]+)"', block)
    desc = desc_m.group(1) if desc_m else None

    data = {
        'name': name,
        'power': power,
        'accuracy': accuracy,
        'category': category,
        'type': move_type,
        'target': target,
        'priority': priority if priority else None,
        'flags': flags if flags else None,
        'desc': desc,
        'secondary': sec,
        'drain': drain,
        'recoil': recoil,
        'multihit': multihit,
        'highCrit': True if high_crit else None,
    }
    data = {k: v for k, v in data.items() if v is not None}
    return pokeapi_slug(name), data

def main():
    print("Fetching PS moves.ts ...")
    try:
        resp = requests.get(PS_MOVES_URL, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print(f"Fetch failed: {e}", file=sys.stderr)
        sys.exit(1)

    text = resp.text
    results = {}

    lines = text.split('\n')
    in_block = False
    depth = 0
    block_lines = []

    for line in lines:
        if not in_block:
            if re.match(r'\t(?:\w+|"[^"]+")\s*:\s*\{', line):
                in_block = True
                depth = line.count('{') - line.count('}')
                block_lines = [line]
        else:
            block_lines.append(line)
            depth += line.count('{') - line.count('}')
            if depth <= 0:
                block = '\n'.join(block_lines)
                slug, data = parse_block(block)
                if slug and data:
                    results[slug] = data
                in_block = False
                block_lines = []
                depth = 0

    with open('moves_data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, separators=(',', ':'))

    print(f"Saved {len(results)} moves -> moves_data.json")

    for m in ['rock-slide', 'ice-punch', 'hyper-voice', 'shadow-ball',
              'fake-out', 'aqua-jet', 'close-combat', 'leaf-blade', 'dire-claw']:
        d = results.get(m, {})
        print(f"  {m}: power={d.get('power')} flags={d.get('flags')} desc={repr(d.get('desc', '')[:50])}")

if __name__ == '__main__':
    main()
