CREATE TABLE health_data (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    heart_rate INTEGER,
    water_intake INTEGER,
    sleep_hours FLOAT
);
