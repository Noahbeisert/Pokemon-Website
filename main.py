import json
import re
import sqlite3

import requests
from bs4 import BeautifulSoup

SEREBII_URL = "https://www.serebii.net/pokemonchampions/pokemon.shtml"
GAME8_DOUBLES_URL = "https://game8.co/games/Pokemon-Champions/archives/593883"
DB_FILE = "pokemon_champions.db"
JSON_FILE = "pokemon.json"

HEADERS = {"User-Agent": "Mozilla/5.0"}

# ── Type chart ────────────────────────────────────────────────────────────────
ALL_TYPES = [
    "Normal", "Fire", "Water", "Electric", "Grass", "Ice", "Fighting", "Poison",
    "Ground", "Flying", "Psychic", "Bug", "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy",
]

_DEF = {
    "Normal":   {"weak": ["Fighting"],                          "immune": ["Ghost"],             "resist": []},
    "Fire":     {"weak": ["Water", "Ground", "Rock"],           "immune": [],                    "resist": ["Fire", "Grass", "Ice", "Bug", "Steel", "Fairy"]},
    "Water":    {"weak": ["Electric", "Grass"],                 "immune": [],                    "resist": ["Fire", "Water", "Ice", "Steel"]},
    "Electric": {"weak": ["Ground"],                            "immune": [],                    "resist": ["Electric", "Flying", "Steel"]},
    "Grass":    {"weak": ["Fire", "Ice", "Poison", "Flying", "Bug"], "immune": [],               "resist": ["Water", "Electric", "Grass", "Ground"]},
    "Ice":      {"weak": ["Fire", "Fighting", "Rock", "Steel"], "immune": [],                    "resist": ["Ice"]},
    "Fighting": {"weak": ["Flying", "Psychic", "Fairy"],        "immune": [],                    "resist": ["Bug", "Rock", "Dark"]},
    "Poison":   {"weak": ["Ground", "Psychic"],                 "immune": [],                    "resist": ["Grass", "Fighting", "Poison", "Bug", "Fairy"]},
    "Ground":   {"weak": ["Water", "Grass", "Ice"],             "immune": ["Electric"],          "resist": ["Poison", "Rock"]},
    "Flying":   {"weak": ["Electric", "Ice", "Rock"],           "immune": ["Ground"],            "resist": ["Grass", "Fighting", "Bug"]},
    "Psychic":  {"weak": ["Bug", "Ghost", "Dark"],              "immune": [],                    "resist": ["Fighting", "Psychic"]},
    "Bug":      {"weak": ["Fire", "Flying", "Rock"],            "immune": [],                    "resist": ["Grass", "Fighting", "Ground"]},
    "Rock":     {"weak": ["Water", "Grass", "Fighting", "Ground", "Steel"], "immune": [],        "resist": ["Normal", "Fire", "Poison", "Flying"]},
    "Ghost":    {"weak": ["Ghost", "Dark"],                     "immune": ["Normal", "Fighting"], "resist": ["Poison", "Bug"]},
    "Dragon":   {"weak": ["Ice", "Dragon", "Fairy"],            "immune": [],                    "resist": ["Fire", "Water", "Electric", "Grass"]},
    "Dark":     {"weak": ["Fighting", "Bug", "Fairy"],          "immune": ["Psychic"],           "resist": ["Ghost", "Dark"]},
    "Steel":    {"weak": ["Fire", "Fighting", "Ground"],        "immune": ["Poison"],            "resist": ["Normal", "Grass", "Ice", "Flying", "Psychic", "Bug", "Rock", "Dragon", "Steel", "Fairy"]},
    "Fairy":    {"weak": ["Poison", "Steel"],                   "immune": ["Dragon"],            "resist": ["Fighting", "Bug", "Dark"]},
}


def compute_matchups(types):
    m = {t: 1.0 for t in ALL_TYPES}
    for ptype in types:
        if ptype not in _DEF:
            continue
        for t in _DEF[ptype]["weak"]:   m[t] *= 2
        for t in _DEF[ptype]["resist"]: m[t] *= 0.5
        for t in _DEF[ptype]["immune"]: m[t]  = 0
    return {
        "weak4x": [t for t in ALL_TYPES if m[t] == 4],
        "weak2x": [t for t in ALL_TYPES if m[t] == 2],
        "resist":  [t for t in ALL_TYPES if 0 < m[t] < 1],
        "immune":  [t for t in ALL_TYPES if m[t] == 0],
    }


# ── Scrapers ──────────────────────────────────────────────────────────────────

# game8 uses forme-qualified names; Serebii uses the base name
_GAME8_NAME_ALIASES = {
    "Eternal Flower Floette": "Floette",
    "Wash Rotom":             "Rotom",
    "Basculegion (Male)":     "Basculegion",
    "Aegislash (Shield Forme)": "Aegislash",
    "Meowstic (Male)":        "Meowstic",
}


def fetch_serebii():
    resp = requests.get(SEREBII_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # First class="tab" table is navigation; second is the roster (517 rows)
    table = soup.find_all("table", class_="tab")[1]
    pokemon = []
    for row in table.find_all("tr"):
        cells = row.find_all("td", class_="fooinfo")
        if len(cells) < 4:
            continue
        dex_number = int(cells[0].get_text(strip=True).lstrip("#"))
        name = cells[2].find("a").get_text(strip=True)
        img_tag = cells[1].find("img")
        image_url = "https://www.serebii.net" + img_tag["src"] if img_tag else None
        type_links = cells[3].find_all("a")
        type1 = type_links[0]["href"].split("/")[-1].replace(".shtml", "") if type_links else None
        type2 = type_links[1]["href"].split("/")[-1].replace(".shtml", "") if len(type_links) > 1 else None
        pokemon.append((dex_number, name, type1, type2, image_url))
    return pokemon


def fetch_doubles_tiers():
    resp = requests.get(GAME8_DOUBLES_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    tiers = {}
    tier_table = None
    for table in soup.find_all("table"):
        th = table.find("th")
        if th and th.find("img") and "Tier" in (th.find("img").get("alt") or ""):
            tier_table = table
            break

    if not tier_table:
        print("WARNING: Could not find tier table on game8")
        return tiers

    for row in tier_table.find_all("tr"):
        th = row.find("th")
        if not th:
            continue
        img = th.find("img")
        if not img:
            continue
        m = re.match(r"^(S|A\+|A|B|C)\s+Tier", img.get("alt", ""))
        if not m:
            continue
        tier = m.group(1)
        for template in row.find_all("template", class_="js-tooltip-content"):
            name = template.get_text(strip=True)
            if name:
                tiers[_GAME8_NAME_ALIASES.get(name, name)] = tier

    return tiers


# ── Persistence ───────────────────────────────────────────────────────────────

def save_to_db(pokemon, tiers):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS pokemon")
    cur.execute("""
        CREATE TABLE pokemon (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            dex_no       INTEGER NOT NULL,
            name         TEXT    NOT NULL,
            type1        TEXT,
            type2        TEXT,
            tier_doubles TEXT,
            weak4x       TEXT,
            weak2x       TEXT,
            resist       TEXT,
            immune       TEXT,
            image_url    TEXT
        )
    """)

    rows = []
    for dex, name, t1, t2, img in pokemon:
        types = [t.capitalize() for t in [t1, t2] if t]
        mu = compute_matchups(types)
        rows.append((
            dex, name, t1, t2,
            tiers.get(name),
            ",".join(mu["weak4x"]),
            ",".join(mu["weak2x"]),
            ",".join(mu["resist"]),
            ",".join(mu["immune"]),
            img,
        ))

    cur.executemany(
        "INSERT INTO pokemon (dex_no, name, type1, type2, tier_doubles, weak4x, weak2x, resist, immune, image_url)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    con.commit()
    con.close()


def update_json(tiers):
    with open(JSON_FILE, encoding="utf-8") as f:
        data = json.load(f)

    for entry in data.values():
        entry.pop("tier_singles", None)
        entry["tier_doubles"] = tiers.get(entry["name"])
        # recompute matchups from types to ensure consistency
        mu = compute_matchups(entry.get("types", []))
        entry.update(mu)

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Fetching Pokemon Champions roster from Serebii...")
    pokemon = fetch_serebii()
    print(f"  {len(pokemon)} entries")

    print("Fetching doubles tier list from game8...")
    tiers = fetch_doubles_tiers()
    print(f"  {len(tiers)} Pokemon ranked")
    for tier in ["S", "A+", "A", "B", "C"]:
        names = [n for n, t in tiers.items() if t == tier]
        print(f"  {tier}: {len(names)}")

    print("Saving to DB...")
    save_to_db(pokemon, tiers)
    print(f"  Saved to {DB_FILE}")

    print("Updating JSON...")
    update_json(tiers)
    print(f"  Updated {JSON_FILE}")
