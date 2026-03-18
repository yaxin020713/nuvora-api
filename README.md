# Nuvora API (Flask)

A simple Flask app for collecting and viewing health data.

## Current API

- `GET /` dashboard UI
- `GET /status` health check
- `GET /beta/access` read whether registration currently requires invite codes
- `POST /beta/invite-codes/validate` validate an invite code without consuming it
- `GET /auth/me` read current session state
- `POST /auth/register` create an account, log in, and return a Bearer token
- `POST /auth/login` log in and return a Bearer token
- `POST /auth/apple` verify a Sign in with Apple identity token and return a Bearer token
- `POST /auth/logout` log out the current session or invalidate the current Bearer token
- `DELETE /auth/account` delete the current account after password confirmation
- `GET /health-data` list health records for the current logged-in user
- `POST /health-data` create a health record for the current logged-in user
- `POST /parse-text` parse a natural-language health message and optionally save it for the current logged-in user
- `POST /whisper` upload an `audio` file for Whisper + GPT parsing and optionally save it for the current logged-in user
- `GET /admin/invite-codes` list invite codes with `X-Admin-Key`
- `POST /admin/invite-codes` create invite codes with `X-Admin-Key`
- `PATCH /admin/invite-codes/<code>` enable/disable or resize invite codes with `X-Admin-Key`

## iOS-Friendly Auth

- Native apps can call `POST /auth/register` or `POST /auth/login` and store the returned `token`
- Native apps can also call `POST /auth/apple` with an Apple identity token from `ASAuthorizationAppleIDCredential`
- Send `Authorization: Bearer <token>` on future API requests
- The web dashboard still works with session cookies, so both web and iOS can share the same backend

## Local Development

1. Create `.env` from `.env.example`
2. Set `OPENAI_API_KEY` if you want to use `/whisper`
3. Set `SECRET_KEY` for stable login sessions
4. Optionally set `DATABASE_URL`; otherwise the app uses local SQLite
5. Optionally set `BETA_INVITE_ONLY=true` if you want closed-beta registration
6. Optionally set `ADMIN_API_KEY` so you can create invite codes over HTTP
7. Optionally set `APPLE_SIGN_IN_AUDIENCE`; by default it expects `com.yaxinzhu.nuvora`
8. Run `flask db upgrade`
9. Run `python app.py`
10. Open `http://127.0.0.1:5000`

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
7. If you want invite-only beta, set `BETA_INVITE_ONLY=true`
8. If you want to manage invite codes remotely, set `ADMIN_API_KEY`
9. If you enable Sign in with Apple, make sure `APPLE_SIGN_IN_AUDIENCE` matches your iOS bundle id

## Sign in with Apple

- Backend verifies Apple identity tokens against Apple's public JWKS
- Default expected audience is `com.yaxinzhu.nuvora`
- First successful Apple sign-in creates a user with `auth_provider=apple`
- Existing local username/password accounts continue to work unchanged

### Sign in with Apple request example

```bash
curl -X POST http://127.0.0.1:5000/auth/apple \
  -H "Content-Type: application/json" \
  -d '{
    "identity_token": "APPLE_IDENTITY_TOKEN",
    "username_hint": "yaxin",
    "email": "relay-or-real-email@example.com",
    "invite_code": "NUVORA-ABC123"
  }'
```

## Closed Beta / Invite Codes

- Leave `BETA_INVITE_ONLY=false` if you want open registration
- Set `BETA_INVITE_ONLY=true` if you want only invite-code holders to register
- The web dashboard registration form will automatically ask for an invite code when invite-only mode is enabled

### Create an invite code via CLI

```bash
flask create-invite-code
```

### Create an invite code via API

```bash
curl -X POST http://127.0.0.1:5000/admin/invite-codes \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: YOUR_ADMIN_API_KEY" \
  -d '{"label":"founding-testers","max_uses":25}'
```

### Validate an invite code before registration

```bash
curl -X POST http://127.0.0.1:5000/beta/invite-codes/validate \
  -H "Content-Type: application/json" \
  -d '{"invite_code":"NUVORA-ABC123"}'
```
