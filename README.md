# MEM Store Bot + Dashboard

Discord bot + Flask dashboard for MEM Store. This repo is prepared for Railway deployment.

## Railway deploy

Push this repo to GitHub, then create a Railway service from the GitHub repo.

Railway start command is already set in `railway.json`:

```bash
python railway_start.py
```

The dashboard listens on Railway's `$PORT` through Gunicorn. Railway requires the public web service to bind to `0.0.0.0:$PORT` for HTTP traffic.

## Required Railway Variables

Add these in Railway > Service > Variables:

```env
DISCORD_TOKEN=<new Discord bot token>
MONGODB_URI=<MongoDB connection string>
GUILD_ID=<Discord server ID>
DASHBOARD_PASSWORD=<dashboard login password>
DASHBOARD_SECRET=<long random secret>
RAILWAY_MODE=all
```

Optional but recommended:

```env
MONGODB_DB=mem_store
GIF_URL=
LOGO_URL=
TICKET_CHANNEL_ID=<channel id>
ORDER_CHANNEL_ID=<channel id>
WELCOME_CHANNEL_ID=<channel id>
LOG_CHANNEL_ID=<channel id>
LEADERBOARD_CHANNEL_ID=<channel id>
LINKS_ALLOWED_CHANNEL=<channel id>
SELF_ROLES_CHANNEL_ID=<channel id>
FEEDBACK_CHANNEL_ID=<channel id>
TICKET_CATEGORY_ID=<category id>
STAFF_ROLE_ID=<role id>
MEMBER_ROLE_ID=<role id>
SECURITY_ROLE_ID=<role id>
ROLE_ENGLISH=<role id>
ROLE_ARABIC=<role id>
ROLE_ARC=<role id>
ROLE_PUBG_MOB=<role id>
ROLE_PUBG_STEAM=<role id>
```

## Railway modes

```env
RAILWAY_MODE=all        # dashboard + bot in one Railway service
RAILWAY_MODE=dashboard  # dashboard only
RAILWAY_MODE=bot        # Discord bot only
```

For production, the cleanest Railway setup is two services from the same GitHub repo:

1. Dashboard service: `RAILWAY_MODE=dashboard`
2. Bot service: `RAILWAY_MODE=bot`

The one-service mode still works for normal bot + dashboard usage.

## Local run

```bash
pip install -r requirements.txt
cp .env.example .env
# Fill .env with real values locally only.
python railway_start.py
```

Or run separately:

```bash
python bot.py
python app.py
```

## Features

- Ticket system: Sell / Buy / Partner tickets, claim, close, rating.
- Seller leaderboard.
- Welcome and leave messages.
- AutoMod: bad words, anti-spam, anti-links, anti-mention spam.
- Self roles through Discord buttons.
- Moderation commands: warn, ban, kick, timeout, unwarn, warnings, blacklist.
- Dashboard pages: home, analytics, tickets, marketplace, moderation, logs, roles, welcome, security, embeds, settings, voice.
- Voice relay with browser push-to-talk. On Railway, public browser PTT may require `WS_URL` pointing to a public websocket/TCP proxy because the voice relay uses a separate WebSocket port.

## Security notes

Do not commit real tokens or MongoDB URIs. Use Railway Variables.

If a Discord token was ever committed to GitHub, reset it in Discord Developer Portal before deploying.
