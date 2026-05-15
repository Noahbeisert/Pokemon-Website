"""
Scrapes all items from pokebase.app/pokemon-champions/items.
For each item: name, slug, category, description, is_megastone, mega_pokemon_slug
              + per-Pokemon tournament usage % from individual item pages.
Writes results into the existing pokebase_champions.db SQLite database.
"""
import requests
import json
import re
import time
import sqlite3

BASE = "https://pokebase.app/pokemon-champions"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; PokeScraper/1.0)"}
DELAY = 0.35
DB_PATH = "pokebase_champions.db"

# Regex: slug ends in "-ite" or "-ite-x" / "-ite-y"  (megastones)
_MEGASTONE_RE = re.compile(r'^.+ite(-[xy])?$')


# -- helpers ------------------------------------------------------------------

def fetch(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.text


def rsc(html: str) -> str:
    parts = []
    for chunk in re.findall(r'self\.__next_f\.push\(\[1,(.*?)\]\s*\)', html, re.DOTALL):
        try:
            parts.append(json.loads(chunk))
        except Exception:
            pass
    return "".join(parts)


def clean(s):
    if not isinstance(s, str):
        return s
    try:
        return s.encode("latin-1").decode("utf-8")
    except Exception:
        return s


def is_megastone(slug: str, category) -> bool:
    if category and "mega" in str(category).lower():
        return True
    return bool(_MEGASTONE_RE.match(slug or ""))


# -- ID → slug map ------------------------------------------------------------

def build_id_slug_map(payload: str) -> dict:
    id_slug = {}
    # nationalNumber and slug are always adjacent sibling fields in the pokemon object.
    # The pokemon's own "id" is the last 24-char hex id before the next nationalNumber.
    for m in re.finditer(
        r'"nationalNumber"\s*:\s*\d+\s*,\s*"slug"\s*:\s*"([a-z0-9\-]+)"',
        payload,
    ):
        slug = m.group(1)
        following = payload[m.end(): m.end() + 5000]
        next_nat = re.search(r'"nationalNumber"', following)
        scope = following[: next_nat.start()] if next_nat else following
        ids = re.findall(r'"id"\s*:\s*"([a-f0-9]{24})"', scope)
        if ids:
            id_slug[ids[-1]] = slug
    return id_slug


# -- item list scrape ---------------------------------------------------------

def scrape_item_list() -> tuple[list, dict]:
    print("Fetching item list …")
    payload = rsc(fetch(f"{BASE}/items"))

    print(f"  Building ID->slug map from pokemon list page ...")
    pokemon_payload = rsc(fetch(f"{BASE}/pokemon"))
    id_slug = build_id_slug_map(pokemon_payload)
    print(f"  ID->slug map: {len(id_slug)} entries")

    total_match = re.search(r'"totalDocs"\s*:\s*(\d+)', payload)
    if not total_match:
        print("  WARNING: could not find totalDocs — payload may be empty")
        return [], id_slug
    print(f"  totalDocs = {total_match.group(1)}")

    idx = total_match.start()
    docs_start = payload.rfind('"docs":[', 0, idx)
    if docs_start == -1:
        print("  WARNING: could not find docs array")
        return [], id_slug
    array_start = docs_start + len('"docs":')

    depth, end = 0, array_start
    for end in range(array_start, min(array_start + 2_000_000, len(payload))):
        if payload[end] == '[':
            depth += 1
        elif payload[end] == ']':
            depth -= 1
            if depth == 0:
                break
    try:
        docs = json.loads(payload[array_start: end + 1])
    except Exception:
        docs = []

    items = []
    for d in docs:
        slug = d.get("slug")
        category = d.get("category") or d.get("itemCategory") or d.get("itemType")
        if isinstance(category, dict):
            category = category.get("name")

        description = clean(
            d.get("description") or d.get("effect") or
            d.get("shortDescription") or d.get("flavorText") or ""
        )

        items.append({
            "slug":         slug,
            "name":         clean(d.get("name", "")),
            "category":     category,
            "description":  description,
            "is_megastone": is_megastone(slug, category),
            "unlock":       d.get("unlock"),
        })

    print(f"  Parsed {len(items)} items ({sum(1 for i in items if i['is_megastone'])} megastones detected)")
    return items, id_slug


# -- individual item page scrape ----------------------------------------------

def scrape_item_page(slug: str, id_slug: dict) -> tuple[dict, str | None]:
    """
    Returns ({pokemon_slug: usage_pct}, mega_pokemon_slug|None).
    mega_pokemon_slug is only set when the page embeds a linked Pokemon object.
    Mutates id_slug in-place with any new ID→slug pairs found on this page.
    """
    payload = rsc(fetch(f"{BASE}/items/{slug}"))

    # Enrich the global map from this page's embedded pokemon data
    id_slug.update(build_id_slug_map(payload))

    # --- usage ---
    usage = {}
    for idx in [m.start() for m in re.finditer(r'"usagePercentByPokemonId"', payload)]:
        obj_start = payload.find("{", idx)
        if obj_start == -1:
            continue
        depth, end = 0, obj_start
        for end in range(obj_start, min(obj_start + 500_000, len(payload))):
            if payload[end] == "{":
                depth += 1
            elif payload[end] == "}":
                depth -= 1
                if depth == 0:
                    break
        try:
            obj = json.loads(payload[obj_start: end + 1])
        except Exception:
            continue
        for pid, pct in obj.items():
            poke_slug = id_slug.get(pid)
            if poke_slug and isinstance(pct, (int, float)):
                usage[poke_slug] = pct

    # --- mega pokemon: look for a single pokemon object linked to this item ---
    # Pattern: "pokemon":{"slug":"charizard",...} or "pokemonSlug":"charizard"
    mega_slug = None
    m = re.search(r'"pokemonSlug"\s*:\s*"([a-z0-9\-]+)"', payload)
    if m:
        mega_slug = m.group(1)
    else:
        # Look for a pokemon object that has nationalNumber (not inside the big usage list)
        # Heuristic: first nationalNumber occurrence on the page is the item's linked Pokemon
        m2 = re.search(r'"nationalNumber"\s*:\s*(\d+).*?"slug"\s*:\s*"([a-z0-9\-]+)"', payload)
        if m2:
            mega_slug = m2.group(2)

    return usage, mega_slug


# -- database setup -----------------------------------------------------------

def init_item_tables(conn: sqlite3.Connection):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS items (
        slug              TEXT PRIMARY KEY,
        name              TEXT,
        category          TEXT,
        description       TEXT,
        is_megastone      INTEGER DEFAULT 0,
        mega_pokemon_slug TEXT,
        overall_usage_pct REAL,
        unlock            TEXT
    );

    CREATE TABLE IF NOT EXISTS item_usage (
        item_slug    TEXT REFERENCES items(slug),
        pokemon_slug TEXT,
        usage_pct    REAL,
        PRIMARY KEY (item_slug, pokemon_slug)
    );
    """)
    # Add new columns if the table was created by an older version of this script
    for col, typedef in [
        ("is_megastone",      "INTEGER DEFAULT 0"),
        ("mega_pokemon_slug", "TEXT"),
        ("description",       "TEXT"),
        ("unlock",            "TEXT"),
    ]:
        try:
            conn.execute(f"ALTER TABLE items ADD COLUMN {col} {typedef}")
        except sqlite3.OperationalError:
            pass  # column already exists
    conn.commit()


# -- main ---------------------------------------------------------------------

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    init_item_tables(conn)

    print("\n-- Scraping items --")
    items, id_slug = scrape_item_list()

    if not items:
        print("No items found — aborting.")
        conn.close()
        return

    for it in items:
        conn.execute("""
            INSERT OR IGNORE INTO items (slug, name, category, description, is_megastone, unlock)
            VALUES (?,?,?,?,?,?)
        """, (it["slug"], it["name"], it["category"], it["description"], int(it["is_megastone"]), it.get("unlock")))
    conn.commit()
    print(f"Inserted {len(items)} item stubs into DB")

    print(f"\n-- Scraping {len(items)} item pages for per-Pokemon usage --")
    errors = []
    for i, it in enumerate(items, 1):
        slug = it["slug"]
        print(f"[{i:3d}/{len(items)}] {slug}", end=" ... ", flush=True)
        try:
            usage, mega_slug = scrape_item_page(slug, id_slug)

            for poke_slug, pct in usage.items():
                conn.execute("""
                    INSERT OR REPLACE INTO item_usage (item_slug, pokemon_slug, usage_pct)
                    VALUES (?,?,?)
                """, (slug, poke_slug, pct))

            overall = round(sum(usage.values()) / len(usage), 2) if usage else 0.0
            conn.execute("""
                UPDATE items SET overall_usage_pct=?, mega_pokemon_slug=COALESCE(?,mega_pokemon_slug)
                WHERE slug=?
            """, (overall, mega_slug, slug))
            conn.commit()

            extra = f" mega={mega_slug}" if mega_slug and it["is_megastone"] else ""
            print(f"OK ({len(usage)} users{extra})")
        except Exception as e:
            print(f"ERROR: {e}")
            errors.append({"slug": slug, "error": str(e)})
        time.sleep(DELAY)

    if errors:
        with open("item_scrape_errors.json", "w") as f:
            json.dump(errors, f, indent=2)
        print(f"\n{len(errors)} errors saved to item_scrape_errors.json")

    # -- summary queries --
    print("\n-- Database summary --")
    for table in ["items", "item_usage"]:
        n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:<22} {n:>6} rows")

    print("\n-- Top 20 most-used items (avg usage % across Pokemon that run them) --")
    rows = conn.execute("""
        SELECT i.name, i.category, i.is_megastone,
               COUNT(DISTINCT iu.pokemon_slug) AS num_users,
               ROUND(AVG(iu.usage_pct), 1)     AS avg_pct,
               ROUND(MAX(iu.usage_pct), 1)     AS peak_pct
        FROM items i
        JOIN item_usage iu ON i.slug = iu.item_slug
        WHERE iu.usage_pct > 0
        GROUP BY i.slug
        ORDER BY avg_pct DESC
        LIMIT 20
    """).fetchall()
    print(f"  {'Item':<28} {'Category':<16} {'Mega':>4}  {'Users':>5}  {'Avg%':>6}  {'Peak%':>6}")
    print(f"  {'-'*28} {'-'*16} {'-'*4}  {'-'*5}  {'-'*6}  {'-'*6}")
    for r in rows:
        cat  = r[1] or "—"
        mega = "yes" if r[2] else ""
        print(f"  {r[0]:<28} {cat:<16} {mega:>4}  {r[3]:>5}  {r[4]:>6}  {r[5]:>6}")

    print("\n-- All megastones + their Pokemon --")
    rows = conn.execute("""
        SELECT i.name, i.mega_pokemon_slug,
               ROUND(MAX(iu.usage_pct), 1) AS top_usage_pct
        FROM items i
        LEFT JOIN item_usage iu ON i.slug = iu.item_slug
        WHERE i.is_megastone = 1
        GROUP BY i.slug
        ORDER BY top_usage_pct DESC NULLS LAST
    """).fetchall()
    print(f"  {'Stone':<28} {'Pokemon':<22} {'Top usage%':>10}")
    print(f"  {'-'*28} {'-'*22} {'-'*10}")
    for r in rows:
        poke = r[1] or "unknown"
        pct  = r[2] if r[2] is not None else "—"
        print(f"  {r[0]:<28} {poke:<22} {str(pct):>10}")

    print("\n-- Berry list (name + what it does) --")
    rows = conn.execute("""
        SELECT name, description
        FROM items
        WHERE LOWER(category) LIKE '%berry%'
           OR LOWER(name) LIKE '%berry%'
        ORDER BY name
    """).fetchall()
    for r in rows:
        desc = (r[1] or "no description")[:80]
        print(f"  {r[0]:<25} {desc}")

    conn.close()
    print(f"\nDatabase saved to {DB_PATH}")


if __name__ == "__main__":
    main()
