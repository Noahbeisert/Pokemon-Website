"""
Scrapes all Pokemon data from pokebase.app/pokemon-champions.
Extracts data from Next.js RSC (React Server Components) payload embedded in HTML.
"""
import requests
import json
import time
import re
from bs4 import BeautifulSoup

BASE_URL = "https://pokebase.app/pokemon-champions/pokemon"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; PokeScraper/1.0)"}
DELAY = 0.4  # polite delay between requests


# ---------------------------------------------------------------------------
# RSC payload extraction
# ---------------------------------------------------------------------------

def get_rsc_payload(html: str) -> str:
    """Decode all self.__next_f.push([1, "..."]) chunks into one string."""
    chunks = re.findall(r'self\.__next_f\.push\(\[1,(.*?)\]\s*\)', html, re.DOTALL)
    parts = []
    for chunk in chunks:
        try:
            parts.append(json.loads(chunk))
        except Exception:
            pass
    return "".join(parts)


# ---------------------------------------------------------------------------
# Individual field extractors (all operate on the RSC payload string)
# ---------------------------------------------------------------------------

def extract_base_stats(payload: str) -> dict:
    m = re.search(
        r'"baseStats"\s*:\s*\{"hp"\s*:\s*(\d+),"attack"\s*:\s*(\d+),'
        r'"defense"\s*:\s*(\d+),"specialAttack"\s*:\s*(\d+),'
        r'"specialDefense"\s*:\s*(\d+),"speed"\s*:\s*(\d+)\}',
        payload,
    )
    if not m:
        return {}
    keys = ["hp", "attack", "defense", "specialAttack", "specialDefense", "speed"]
    return {k: int(v) for k, v in zip(keys, m.groups())}


def extract_movelist(payload: str) -> list:
    """Find the largest JSON array of move objects in the payload."""
    # Moves look like: [{"name":"Acid Spray","slug":"acid-spray","type":{...},"damageClass":"special",...}]
    # Find all positions where a move array might start
    best = []
    for m in re.finditer(r'\[\{"name":"[^"]+","slug":"[^"]+","type":\{', payload):
        start = m.start()
        # walk forward to find matching closing bracket
        depth = 0
        i = start
        for i in range(start, min(start + 200_000, len(payload))):
            if payload[i] == "[":
                depth += 1
            elif payload[i] == "]":
                depth -= 1
                if depth == 0:
                    break
        candidate = payload[start : i + 1]
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, list) and len(parsed) > len(best):
                best = parsed
        except Exception:
            pass
    # Simplify: keep only relevant fields
    moves = []
    for mv in best:
        if not isinstance(mv, dict):
            continue
        moves.append({
            "name": mv.get("name"),
            "slug": mv.get("slug"),
            "type": mv.get("type", {}).get("name") if isinstance(mv.get("type"), dict) else mv.get("typeName"),
            "damageClass": mv.get("damageClass"),
            "power": mv.get("power"),
            "accuracy": mv.get("accuracy"),
            "pp": mv.get("pp"),
            "description": mv.get("description"),
        })
    return moves


def extract_abilities(soup: BeautifulSoup) -> list:
    """Parse abilities from HTML — they render as <li> with name + description."""
    abilities = []
    seen = set()
    # Find the "Abilities" section header
    for h in soup.find_all(["h2", "h3"]):
        if h.get_text(strip=True).lower() == "abilities":
            ul = h.find_next("ul")
            if ul:
                for li in ul.find_all("li", recursive=False):
                    name_el = li.find(["div", "span", "strong"], class_=re.compile(r"font-semibold|font-bold|font-medium"))
                    desc_el = li.find("p")
                    name = name_el.get_text(strip=True) if name_el else ""
                    desc = desc_el.get_text(strip=True) if desc_el else ""
                    if name and name not in seen:
                        seen.add(name)
                        abilities.append({"name": name, "description": desc})
            break
    return abilities


def extract_tournament_usage(payload: str) -> dict:
    """
    Extract usage stats for abilities, items, and moves.
    Each section has aria-label="Abilities"/"Items"/"Moves".
    Entries: "children":"<Name>" followed by [<percent>,"%"].
    """
    BAD_WORDS = ("dark:", "text-", "flex", "grid", "border", "zinc", "rounded",
                 "items-", "justify-", "overflow", "space-", "divide", "py-", "px-",
                 "gap-", "font-", "shadow", "tracking", "truncate", "tabular")

    def parse_usage_section(chunk: str) -> list:
        results = []
        for pm in re.finditer(r'\[([\d.]+),"%"\]', chunk):
            pct = float(pm.group(1))
            snippet = chunk[max(0, pm.start() - 400) : pm.start()]
            names = re.findall(r'"children"\s*:\s*"([^"]{2,60})"', snippet)
            name = next(
                (n for n in reversed(names) if not any(w in n for w in BAD_WORDS)),
                None,
            )
            if name:
                results.append({"name": name, "percent": pct})
        return results

    sections: dict = {"abilities": [], "items": [], "moves": []}
    all_matches = list(re.finditer(r'"aria-label"\s*:\s*"(Abilities|Items|Moves)"', payload))
    for i, m in enumerate(all_matches):
        label = m.group(1).lower()
        end = all_matches[i + 1].start() if i + 1 < len(all_matches) else m.start() + 6000
        chunk = payload[m.start() : end]
        sections[label] = parse_usage_section(chunk)

    return sections


def extract_type_effectiveness(payload: str) -> dict:
    """
    Each type badge has aria-label="<Type> <mult>×" (× = U+00D7).
    These only appear in the type effectiveness section. Scan full payload.
    """
    MULT_SIGN = "\u00d7"
    pattern = rf'"aria-label"\s*:\s*"([A-Za-z]+)\s+([\d/]+){re.escape(MULT_SIGN)}"'
    matches = re.findall(pattern, payload)
    return {ptype: mult for ptype, mult in matches}


def extract_types(payload: str) -> list:
    """
    Get the Pokemon's own types from the profile card type badge section.
    Types appear as tooltip components: ["$","$L3d","Fighting",{...}]
    near the div with className containing "top-3 left-3".
    """
    POKEMON_TYPES = {
        "Normal", "Fire", "Water", "Electric", "Grass", "Ice",
        "Fighting", "Poison", "Ground", "Flying", "Psychic", "Bug",
        "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy",
    }
    # The profile card type badges are in a div with "top-3 left-3" className
    m = re.search(r'top-3 left-3', payload)
    if m:
        chunk = payload[m.start() : m.start() + 1200]
        # Extract alt attributes from type icon images — most reliable signal
        alts = re.findall(r'"alt"\s*:\s*"([^"]+)"', chunk)
        found = [a for a in alts if a in POKEMON_TYPES]
        if found:
            return list(dict.fromkeys(found))  # deduplicate, preserve order
    return []


def extract_image_url(soup: BeautifulSoup) -> str | None:
    """Main pokemon profile image — hosted under pokemon-champions/ with large size."""
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if "pokemon-champions/" in src and ("480" in src or "360" in src or "240" in src):
            return src
    # fallback: any pokemon-champions image that's not tiny
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if "pokemon-champions/" in src and "width=48" not in src and "width=72" not in src:
            return src
    return None


def extract_pokedex_number(payload: str) -> int | None:
    m = re.search(r'"pokedexNumber"\s*:\s*(\d+)', payload)
    return int(m.group(1)) if m else None


# ---------------------------------------------------------------------------
# Slug discovery
# ---------------------------------------------------------------------------

def get_all_slugs() -> list:
    """Fetch list pages until a page returns no new slugs."""
    slugs = []
    seen = set()
    page = 1
    while True:
        html = requests.get(f"{BASE_URL}?page={page}", headers=HEADERS, timeout=15).text
        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all("a", href=re.compile(r"^/pokemon-champions/pokemon/[^?#/]+$"))
        new = 0
        for a in links:
            slug = a["href"].split("/")[-1]
            if slug and slug not in seen:
                seen.add(slug)
                slugs.append(slug)
                new += 1
        print(f"  page {page}: +{new} slugs (total {len(slugs)})")
        if new == 0:
            break
        page += 1
        time.sleep(DELAY)
    return slugs


# ---------------------------------------------------------------------------
# Single Pokemon scrape
# ---------------------------------------------------------------------------

def scrape_pokemon(slug: str) -> dict:
    url = f"{BASE_URL}/{slug}"
    html = requests.get(url, headers=HEADERS, timeout=15).text
    soup = BeautifulSoup(html, "html.parser")
    payload = get_rsc_payload(html)

    h1 = soup.find("h1")
    name = h1.get_text(strip=True) if h1 else slug.replace("-", " ").title()

    return {
        "slug": slug,
        "name": name,
        "pokedex_number": extract_pokedex_number(payload),
        "types": extract_types(payload),
        "image_url": extract_image_url(soup),
        "base_stats": extract_base_stats(payload),
        "abilities": extract_abilities(soup),
        "type_effectiveness": extract_type_effectiveness(payload),
        "tournament_usage": extract_tournament_usage(payload),
        "movelist": extract_movelist(payload),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Collecting slugs...")
    slugs = get_all_slugs()
    print(f"Found {len(slugs)} Pokemon\n")

    all_data = {}
    errors = []

    for i, slug in enumerate(slugs, 1):
        print(f"[{i}/{len(slugs)}] {slug}", end=" ... ", flush=True)
        try:
            data = scrape_pokemon(slug)
            all_data[slug] = data
            stat_count = len(data["base_stats"])
            move_count = len(data["movelist"])
            print(f"OK (stats={stat_count}, moves={move_count})")
        except Exception as e:
            print(f"ERROR: {e}")
            errors.append({"slug": slug, "error": str(e)})
        time.sleep(DELAY)

    out_path = "pokemon_champions.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(all_data)} Pokemon to {out_path}")

    if errors:
        with open("scrape_errors.json", "w", encoding="utf-8") as f:
            json.dump(errors, f, indent=2)
        print(f"{len(errors)} errors saved to scrape_errors.json")


if __name__ == "__main__":
    main()
