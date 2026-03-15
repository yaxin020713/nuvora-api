# Nuvora API (Flask)

A simple Flask backend for storing health data.

## Current API

- `GET /` health check
- `GET /health-data` list health records, optional `?user_id=...`
- `POST /health-data` create a health record with JSON:
  `{"user_id":"u1","heart_rate":72,"water_intake":1800,"sleep_hours":7.5}`
- `POST /whisper` upload an `audio` file for Whisper + GPT parsing
- `POST /whisper` also supports form fields `save=true` and `user_id=...` to store the parsed result

## Local Development

1. Create `.env` from `.env.example`
2. Set `OPENAI_API_KEY` if you want to use `/whisper`
3. Optionally set `DATABASE_URL`; otherwise the app uses local SQLite
4. Run `python app.py`

## How to Deploy on Render

1. Create a PostgreSQL database on Render (name: `nuvora-db`)
2. Push this repo to GitHub
3. Connect to Render -> New Web Service -> Select this repo
4. Add environment variable `DATABASE_URL` or use `fromDatabase`
