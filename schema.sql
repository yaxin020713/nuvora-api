CREATE TABLE health_data (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    heart_rate INTEGER,
    water_intake INTEGER,
    sleep_hours FLOAT
);

CREATE TABLE invite_codes (
    id SERIAL PRIMARY KEY,
    code VARCHAR(64) NOT NULL UNIQUE,
    label VARCHAR(120),
    max_uses INTEGER NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE users
    ADD COLUMN invite_code_id INTEGER REFERENCES invite_codes(id),
    ADD COLUMN invite_code_value VARCHAR(64);

ALTER TABLE users
    ALTER COLUMN password_hash DROP NOT NULL;

ALTER TABLE users
    ADD COLUMN auth_provider VARCHAR(30) NOT NULL DEFAULT 'local',
    ADD COLUMN provider_subject VARCHAR(255) UNIQUE,
    ADD COLUMN email VARCHAR(255);
