"""
Scrapes tournament team data from pokebase.app/pokemon-champions homepage.
Extracts all tournaments in the "Tournament Tops" section with full team details.
Data lives in the Next.js RSC payload — no JavaScript execution needed.
"""
import requests
import json
import re

BASE_URL = "https://pokebase.app/pokemon-champions"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; PokeScraper/1.0)"}


def get_rsc_payload(html: str) -> str:
    chunks = re.findall(r'self\.__next_f\.push\(\[1,(.*?)\]\s*\)', html, re.DOTALL)
    parts = []
    for chunk in chunks:
        try:
            parts.append(json.loads(chunk))
        except Exception:
            pass
    return "".join(parts)


def extract_json_object(text: str, start: int) -> tuple[dict | None, int]:
    """Walk from `start` (must point at '{') and return the parsed object + end index."""
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start : i + 1]), i + 1
                except Exception:
                    return None, i + 1
    return None, len(text)


def extract_json_array(text: str, start: int) -> tuple[list | None, int]:
    """Walk from `start` (must point at '[') and return the parsed array + end index."""
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "[":
            depth += 1
        elif text[i] == "]":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start : i + 1]), i + 1
                except Exception:
                    return None, i + 1
    return None, len(text)


def clean_text(s: str) -> str:
    """Fix encoding issues (e.g. Mojibake from Latin-1/UTF-8 mix)."""
    if not isinstance(s, str):
        return s
    try:
        return s.encode("latin-1").decode("utf-8")
    except Exception:
        return s


def clean_obj(obj):
    """Recursively fix encoding in all string values."""
    if isinstance(obj, dict):
        return {k: clean_obj(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_obj(v) for v in obj]
    if isinstance(obj, str):
        return clean_text(obj)
    return obj


def extract_tournaments(payload: str) -> list[dict]:
    """
    Extract all tournament objects from the RSC payload.
    Each tournament has: id, name, date, numberOfPlayers, limitlessId,
                         usageRates[], teams[]
    Each team has: placing, wins, losses, limitlessPlayer,
                   pokemon[] (name, ability, item, moves x4)
    """
    tournaments = []

    # Find each tournament by its limitlessId marker
    for m in re.finditer(r'"limitlessId"\s*:\s*"[a-f0-9]{24}"', payload):
        # Back up to the opening { of this tournament object
        obj_start = payload.rfind('{"id":', 0, m.start())
        if obj_start == -1:
            continue

        obj, _ = extract_json_object(payload, obj_start)
        if not obj:
            continue

        # The tournament object itself doesn't include teams — it's a plain metadata obj.
        # The teams array follows immediately after as: }, "usageRates": [...], "teams": [...]
        # Find "teams":[ that comes after this tournament's id
        teams_search_start = obj_start + 1
        teams_idx = payload.find('"teams":[', teams_search_start)
        if teams_idx == -1:
            continue

        # Make sure this teams array belongs to this tournament (not the next one)
        next_tournament = payload.find('"limitlessId":', m.end())
        if next_tournament != -1 and teams_idx > next_tournament:
            continue

        array_start = teams_idx + len('"teams":')
        teams, _ = extract_json_array(payload, array_start)
        if not isinstance(teams, list):
            continue

        # Also extract usageRates
        usage_idx = payload.find('"usageRates":[', obj_start)
        usage = []
        if usage_idx != -1 and (next_tournament == -1 or usage_idx < next_tournament):
            usage_array_start = usage_idx + len('"usageRates":')
            usage, _ = extract_json_array(payload, usage_array_start)

        tournament = {
            "id": obj.get("id"),
            "name": obj.get("name"),
            "date": obj.get("date"),
            "numberOfPlayers": obj.get("numberOfPlayers"),
            "limitlessId": obj.get("limitlessId"),
            "usageRates": usage or [],
            "teams": teams,
        }
        tournaments.append(tournament)

    return tournaments


def simplify_team(team: dict) -> dict:
    """Keep only the fields we care about; clean up nested noise."""
    pokemon = []
    for p in team.get("pokemon", []):
        pokemon.append({
            "name": p.get("name"),
            "slug": p.get("slug"),
            "ability": p.get("ability"),
            "item": p.get("item"),
            "nature": p.get("nature"),
            "moves": [
                {
                    "name": mv.get("name"),
                    "type": mv.get("typeName"),
                    "damageClass": mv.get("damageClass"),
                    "power": mv.get("power"),
                    "accuracy": mv.get("accuracy"),
                }
                for mv in p.get("moves", [])
            ],
        })
    return {
        "placing": team.get("placing"),
        "wins": team.get("wins"),
        "losses": team.get("losses"),
        "ties": team.get("ties"),
        "player": team.get("limitlessPlayer"),
        "teamName": team.get("name"),
        "pokemon": pokemon,
    }


def main():
    print(f"Fetching {BASE_URL} ...")
    html = requests.get(BASE_URL, headers=HEADERS, timeout=15).text
    payload = get_rsc_payload(html)
    print(f"RSC payload: {len(payload):,} chars\n")

    tournaments = extract_tournaments(payload)
    tournaments = clean_obj(tournaments)

    print(f"Found {len(tournaments)} tournaments:")
    for t in tournaments:
        print(f"  [{t['date'][:10]}] {t['name']} — {len(t['teams'])} teams, {t['numberOfPlayers']} players")

    # Save full data
    with open("tournament_teams.json", "w", encoding="utf-8") as f:
        json.dump(tournaments, f, indent=2, ensure_ascii=False)
    print("\nFull data saved to tournament_teams.json")

    # Print summary for HeroicTitan (first tournament)
    if tournaments:
        t = tournaments[0]
        print(f"\n{'='*60}")
        print(f"WINNER: {t['name']}")
        print(f"{'='*60}")
        first_team = simplify_team(t["teams"][0])
        print(f"1st place: {first_team['player']}  ({first_team['wins']}-{first_team['losses']})")
        for p in first_team["pokemon"]:
            print(f"\n  {p['name']} @ {p['item']}")
            print(f"  Ability: {p['ability']}")
            for mv in p["moves"]:
                power_str = f" (power {mv['power']})" if mv["power"] else ""
                print(f"    - {mv['name']} [{mv['type']}]{power_str}")


if __name__ == "__main__":
    main()
