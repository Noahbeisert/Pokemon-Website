CREATE TABLE abilities (
        slug        TEXT PRIMARY KEY,
        name        TEXT,
        description TEXT
    );

CREATE TABLE item_usage (
        item_slug    TEXT REFERENCES items(slug),
        pokemon_slug TEXT,
        usage_pct    REAL,
        PRIMARY KEY (item_slug, pokemon_slug)
    );

CREATE TABLE items (
        slug              TEXT PRIMARY KEY,
        name              TEXT,
        category          TEXT,
        description       TEXT,
        is_megastone      INTEGER DEFAULT 0,
        mega_pokemon_slug TEXT,
        overall_usage_pct REAL
    , unlock TEXT);

CREATE TABLE move_usage (
        move_slug     TEXT REFERENCES moves(slug),
        pokemon_slug  TEXT REFERENCES pokemon(slug),
        usage_pct     REAL,
        PRIMARY KEY (move_slug, pokemon_slug)
    );

CREATE TABLE moves (
        slug         TEXT PRIMARY KEY,
        name         TEXT,
        type         TEXT,
        damage_class TEXT,
        power        INTEGER,
        accuracy     INTEGER,
        pp           INTEGER,
        description  TEXT,
        overall_usage_pct REAL  -- filled after scraping move pages
    , priority INTEGER, target TEXT, effect TEXT, effect_chance INTEGER);

CREATE TABLE natures (
        slug         TEXT PRIMARY KEY,
        name         TEXT,
        increased    TEXT,   -- stat name or NULL for neutral
        decreased    TEXT    -- stat name or NULL for neutral
    );

CREATE TABLE pokemon (
        slug        TEXT PRIMARY KEY,
        name        TEXT,
        types       TEXT,   -- JSON array
        hp          INTEGER, attack      INTEGER, defense     INTEGER,
        sp_attack   INTEGER, sp_defense  INTEGER, speed       INTEGER,
        image_url   TEXT
    );

CREATE TABLE pokemon_move (
        pokemon_slug TEXT REFERENCES pokemon(slug),
        move_slug    TEXT REFERENCES moves(slug),
        PRIMARY KEY (pokemon_slug, move_slug)
    );

CREATE TABLE team_move (
        team_id      TEXT REFERENCES teams(id),
        position     INTEGER,
        move_slug    TEXT,
        PRIMARY KEY (team_id, position, move_slug)
    );

CREATE TABLE team_pokemon (
        team_id      TEXT REFERENCES teams(id),
        position     INTEGER,
        pokemon_slug TEXT,
        ability      TEXT,
        item         TEXT,
        nature       TEXT,
        PRIMARY KEY (team_id, position)
    );

CREATE TABLE teams (
        id              TEXT PRIMARY KEY,
        tournament_id   TEXT REFERENCES tournaments(id),
        player          TEXT,
        placing         INTEGER,
        wins            INTEGER,
        losses          INTEGER,
        ties            INTEGER
    );

CREATE TABLE tournament_usage (
        pokemon_slug  TEXT REFERENCES pokemon(slug),
        category      TEXT CHECK(category IN ('ability','item','move')),
        name          TEXT,
        usage_pct     REAL,
        PRIMARY KEY (pokemon_slug, category, name)
    );

CREATE TABLE tournaments (
        id          TEXT PRIMARY KEY,
        name        TEXT,
        date        TEXT,
        num_players INTEGER,
        limitless_id TEXT
    );

CREATE TABLE type_chart (
        pokemon_slug    TEXT REFERENCES pokemon(slug),
        attacking_type  TEXT,
        multiplier      TEXT,
        PRIMARY KEY (pokemon_slug, attacking_type)
    );

