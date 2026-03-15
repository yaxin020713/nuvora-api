# Nuvora API (Flask)

A simple Flask app for collecting and viewing health data.

## Current API

- `GET /` dashboard UI
- `GET /status` health check
- `GET /auth/me` read current session state
- `POST /auth/register` create an account and log in
- `POST /auth/login` log in
- `POST /auth/logout` log out
- `GET /health-data` list health records for the current logged-in user
- `POST /health-data` create a health record for the current logged-in user
- `POST /parse-text` parse a natural-language health message and optionally save it for the current logged-in user
- `POST /whisper` upload an `audio` file for Whisper + GPT parsing and optionally save it for the current logged-in user

## Local Development

1. Create `.env` from `.env.example`
2. Set `OPENAI_API_KEY` if you want to use `/whisper`
3. Set `SECRET_KEY` for stable login sessions
4. Optionally set `DATABASE_URL`; otherwise the app uses local SQLite
5. Run `flask db upgrade`
6. Run `python app.py`
7. Open `http://127.0.0.1:5000`

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
6. Set `SECRET_KEY`
