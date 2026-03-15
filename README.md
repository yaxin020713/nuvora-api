# Nuvora API (Flask)

A simple Flask app for collecting and viewing health data.

## Current API

- `GET /` dashboard UI
- `GET /status` health check
- `GET /health-data` list health records, optional `?user_id=...`
- `POST /health-data` create a health record with JSON:
  `{"user_id":"u1","heart_rate":72,"water_intake":1800,"sleep_hours":7.5}`
- `POST /parse-text` parse a natural-language health message and optionally save it
- `POST /whisper` upload an `audio` file for Whisper + GPT parsing
- `POST /whisper` also supports form fields `save=true` and `user_id=...` to store the parsed result

## Local Development

1. Create `.env` from `.env.example`
2. Set `OPENAI_API_KEY` if you want to use `/whisper`
3. Optionally set `DATABASE_URL`; otherwise the app uses local SQLite
4. Run `flask db upgrade`
5. Run `python app.py`
6. Open `http://127.0.0.1:5000`

## Deployment Notes

- Render can deploy this app directly with [`render.yaml`](/Users/xiaolaohu/nuvora/render.yaml)
- Startup now runs `flask db upgrade` before `gunicorn`, so schema changes are versioned instead of relying on `db.create_all()`
- A [`Dockerfile`](/Users/xiaolaohu/nuvora/Dockerfile) is included so the app can be moved to Google Cloud Run, Fly.io, Railway, AWS, or another container platform later with minimal app changes

## How to Deploy on Render

1. Create a PostgreSQL database on Render (name: `nuvora-db`)
2. Push this repo to GitHub
3. Connect to Render -> New Web Service -> Select this repo
4. Add environment variable `DATABASE_URL` or use `fromDatabase`
5. Set `OPENAI_API_KEY`
