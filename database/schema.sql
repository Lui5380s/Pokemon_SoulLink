CREATE TABLE IF NOT EXISTS trainers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS routes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    status TEXT DEFAULT 'open' CHECK(status IN ('open', 'closed'))
);

CREATE TABLE IF NOT EXISTS pokemon (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    route_id INTEGER,
    trainer_id INTEGER,
    status TEXT DEFAULT 'alive' CHECK(status IN ('alive', 'dead')),
    FOREIGN KEY (route_id) REFERENCES routes (id),
    FOREIGN KEY (trainer_id) REFERENCES trainers (id)
);

CREATE TABLE IF NOT EXISTS banned_pokemon (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pokemon_name TEXT NOT NULL UNIQUE,
    reason TEXT NOT NULL
);

-- Neue Tabelle für aktive Pokémon pro Spieler
CREATE TABLE IF NOT EXISTS active_pokemon (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pokemon_id INTEGER NOT NULL,
    trainer_id INTEGER NOT NULL,
    is_active INTEGER DEFAULT 1 CHECK(is_active IN (0, 1)),
    FOREIGN KEY (pokemon_id) REFERENCES pokemon (id),
    FOREIGN KEY (trainer_id) REFERENCES trainers (id)
);