# Assignment Submission Portal — monolith for Vercel

One Flask app (`portal/`) + static assets (`public/static/`). The old Nginx, Gunicorn and Redis containers are gone.

| Before (3 containers) | Now |
|---|---|
| Nginx serving `/static` + proxy | Vercel CDN serves `public/static`; Vercel routes the rest to Flask |
| Gunicorn + Flask in Docker | `app.py` exports `app` (Vercel Python/WSGI function) |
| Redis container | Optional external Redis (Upstash). No Redis = no caching |
| `entrypoint.sh` migrate+seed on boot | `scripts/init_db.py` or guarded `POST /internal/init-db` |
| `backend/app`, `frontend/templates` | `portal/`, `portal/templates` |

## Deploy
1. Create a Postgres DB (Supabase). Use the **transaction pooler** string (port 6543).
2. Push this folder to GitHub → import in Vercel (framework auto-detects Flask), or `vercel --prod`.
3. Env vars (Settings → Environment Variables): `SECRET_KEY`, `DATABASE_URL`, `ADMIN_PASSWORD`, `INIT_TOKEN`; optional `REDIS_URL`.
4. Initialise the DB once:
   ```bash
   curl -X POST -H "X-Init-Token: $INIT_TOKEN" "https://<your-app>.vercel.app/internal/init-db?seed=admin"
   ```
   (or locally: `vercel env pull .env.local && python scripts/init_db.py --seed admin`). Then remove `INIT_TOKEN`.
   `?seed=demo` loads demo students/assignments (known passwords — don't use on a public site).
5. Tip: set the function region near your database (Project → Settings → Functions).

## Local
```bash
pip install -r requirements-dev.txt
cp .env.example .env   # set DATABASE_URL
python scripts/init_db.py --seed demo
flask --app app run --debug
pytest
```

## Behaviour changes you should know about
- **Password reset link is no longer shown on the page in production** (anyone knowing an email could take over the account). Set `SHOW_RESET_LINK=true` only for demos. Add an email provider to enable real resets.
- Reset tokens are now signed/stateless (the old in-memory dict can't work across serverless instances).
- The in-memory fake Redis was removed (it would serve stale data across instances).
- Seeding no longer runs on every boot; admin email/password come from `ADMIN_EMAIL` / `ADMIN_PASSWORD`.
- `legacy/react-prototype/` is the old mock-data React/Vite UI. It was never connected to Flask, so it isn't deployed.
