import sqlite3

conn = sqlite3.connect("pokebase_champions.db")

print("=== TOP 20 MOVES ===")
rows = conn.execute("""
    SELECT move_slug, COUNT(*) as cnt
    FROM team_move
    GROUP BY move_slug ORDER BY cnt DESC LIMIT 20
""").fetchall()
for r in rows:
    print(f"  {r[0]:<30} {r[1]:>6}")

print()
print("=== TOP 15 ITEMS ===")
rows = conn.execute("""
    SELECT item, COUNT(*) as cnt
    FROM team_pokemon
    WHERE item IS NOT NULL AND item != ''
    GROUP BY item ORDER BY cnt DESC LIMIT 15
""").fetchall()
for r in rows:
    print(f"  {r[0]:<30} {r[1]:>6}")

print()
print("=== MOST COMMON DUOS (top 4 finishes) ===")
rows = conn.execute("""
    SELECT a.pokemon_slug, b.pokemon_slug, COUNT(*) as cnt
    FROM team_pokemon a
    JOIN team_pokemon b ON a.team_id = b.team_id AND a.pokemon_slug < b.pokemon_slug
    JOIN teams t ON a.team_id = t.id
    WHERE t.placing <= 4
    GROUP BY a.pokemon_slug, b.pokemon_slug
    ORDER BY cnt DESC LIMIT 15
""").fetchall()
for r in rows:
    print(f"  {r[0]:<25} + {r[1]:<25} {r[2]:>5}")

print()
print("=== SNEASLER TOP PARTNERS (top 4) ===")
rows = conn.execute("""
    SELECT b.pokemon_slug, COUNT(*) as cnt
    FROM team_pokemon a
    JOIN team_pokemon b ON a.team_id = b.team_id AND a.pokemon_slug != b.pokemon_slug
    JOIN teams t ON a.team_id = t.id
    WHERE a.pokemon_slug = 'sneasler' AND t.placing <= 4
    GROUP BY b.pokemon_slug ORDER BY cnt DESC LIMIT 10
""").fetchall()
for r in rows:
    print(f"  {r[0]:<30} {r[1]:>5}")

print()
print("=== KINGAMBIT TOP PARTNERS (top 4) ===")
rows = conn.execute("""
    SELECT b.pokemon_slug, COUNT(*) as cnt
    FROM team_pokemon a
    JOIN team_pokemon b ON a.team_id = b.team_id AND a.pokemon_slug != b.pokemon_slug
    JOIN teams t ON a.team_id = t.id
    WHERE a.pokemon_slug = 'kingambit' AND t.placing <= 4
    GROUP BY b.pokemon_slug ORDER BY cnt DESC LIMIT 10
""").fetchall()
for r in rows:
    print(f"  {r[0]:<30} {r[1]:>5}")

conn.close()
