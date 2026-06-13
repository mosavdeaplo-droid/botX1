# All Mode Fix

This version fixes Railway `RAILWAY_MODE=all` startup issues caused by placeholder environment variables.

## Fixed

- `app.py` no longer crashes when Railway Suggested Variables contain placeholder role IDs like `your_arc_raiders_role_id_here`.
- `.env.example` no longer contains placeholder text for optional numeric Discord IDs. Leave them blank or use real Discord IDs.
- `railway_start.py` keeps the dashboard alive in `RAILWAY_MODE=all` even if the bot process crashes, so Railway `/healthz` can pass and the real bot error remains visible in Deploy Logs.

## Required Railway Variables for one service

```env
RAILWAY_MODE=all
DISCORD_TOKEN=your_real_new_bot_token
MONGODB_URI=your_real_mongodb_uri
MONGODB_DB=mem_store
GUILD_ID=your_numeric_discord_server_id
DASHBOARD_PASSWORD=choose_password
DASHBOARD_SECRET=long_random_secret
```

Optional Discord IDs must be numbers only or blank.
