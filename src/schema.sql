CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY,
    origin_guild BIGINT,
    last_updated BIGINT NOT NULL,
    private BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS currencies (
    shorthand TEXT PRIMARY KEY,
    circulation BIGINT,
    cur_value FLOAT NOT NULL
);

CREATE TABLE IF NOT EXISTS upgrades (
    id SERIAL,
    item_name TEXT PRIMARY KEY NOT NULL,
    price FLOAT NOT NULL,
    generation FLOAT NOT NULL
);

CREATE TABLE IF NOT EXISTS bank (
    id BIGINT PRIMARY KEY, -- The id of the discord user, allows for cross guild use
    balance BIGINT NOT NULL
    -- Might add the ability for multiple currencies to be stored per account at some point
);

CREATE TABLE IF NOT EXISTS user_upgrades (
    id BIGINT,
    name TEXT NOT NULL,
    count BIGINT DEFAULT 1
);

CREATE TABLE IF NOT EXISTS errors (
    id SERIAL PRIMARY KEY,
    error_timestamp BIGINT NOT NULL,
    traceback TEXT NOT NULL
);

INSERT INTO upgrades (item_name, price, generation) VALUES ('Lemonade', 1.0, 0.1) ON CONFLICT DO NOTHING;
-- INSERT INTO currencies (shorthand,circulation,cur_value) VALUES ('USD', NULL, 1) ON CONFLICT DO NOTHING;
-- INSERT INTO upgrades (item_name, currency, price) VALUES ("Lemonade", "USD", 1.0);