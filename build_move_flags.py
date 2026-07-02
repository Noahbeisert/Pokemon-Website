#!/usr/bin/env python3
"""
Scrapes move flags from Pokemon Showdown's moves.ts and writes move_flags.json.
Flags included: contact, bullet, sound, punch, slicing, dance, powder
Run once whenever the PS data changes.
"""

import json
import re
import sys
import requests

PS_MOVES_URL = "https://raw.githubusercontent.com/smogon/pokemon-showdown/master/data/moves.ts"
RELEVANT = {'contact', 'bullet', 'sound', 'punch', 'slicing', 'dance', 'powder'}

def pokeapi_slug(name):
    return re.sub(r'[^a-z0-9-]', '', name.lower().replace(' ', '-'))

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

    # Walk line-by-line tracking brace depth to isolate each top-level move block.
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

                name_m = re.search(r'name:\s*"([^"]+)"', block)
                if not name_m:
                    in_block = False
                    block_lines = []
                    depth = 0
                    continue

                flags_m = re.search(r'flags:\s*\{([^}]*)\}', block)
                if flags_m:
                    raw_flags = set(re.findall(r'(\w+):\s*1', flags_m.group(1)))
                    relevant = raw_flags & RELEVANT
                    if relevant:
                        slug = pokeapi_slug(name_m.group(1))
                        results[slug] = sorted(relevant)

                in_block = False
                block_lines = []
                depth = 0

    with open('move_flags.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, sort_keys=True)

    print(f"Saved {len(results)} moves with relevant flags -> move_flags.json")

    # Sanity check
    checks = ['shadow-ball', 'ice-punch', 'hyper-voice', 'aqua-jet',
              'protect', 'leaf-blade', 'bullet-punch', 'close-combat']
    for m in checks:
        print(f"  {m}: {results.get(m, [])}")

if __name__ == '__main__':
    main()
