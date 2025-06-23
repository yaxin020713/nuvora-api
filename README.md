# Nuvora API (Flask)

A simple Flask backend for storing health data.

## How to Deploy on Render

1. Create a PostgreSQL database on Render (name: `nuvora-db`)
2. Push this repo to GitHub
3. Connect to Render -> New Web Service -> Select this repo
4. Add environment variable `DATABASE_URL` or use `fromDatabase`
