CREATE TABLE health_data (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    water_ml INTEGER,
    heart_rate INTEGER,
    sleep_hour FLOAT
);
