# MEM Store Railway Ready — Full code to copy
Replace/add these files in your GitHub repo using the exact paths below.

## `.env.example`
```env
# Railway Variables / Environment Variables
# Do not put real secrets in GitHub. Add real values inside Railway Variables only.

DISCORD_TOKEN=your_discord_bot_token_here
MONGODB_URI=your_mongodb_connection_string_here
MONGODB_DB=mem_store
GUILD_ID=your_discord_server_id_here
DASHBOARD_PASSWORD=choose_a_dashboard_password_here
DASHBOARD_SECRET=choose_a_long_random_secret_here

# Railway startup mode:
# all = dashboard + bot in one Railway service
# dashboard = dashboard only
# bot = Discord bot only
RAILWAY_MODE=all

# Dashboard / branding
GIF_URL=
LOGO_URL=

# Voice Relay
# WS_PORT is internal in one-service mode.
# Browser Push-to-Talk needs WS_URL to point to a public websocket/TCP proxy if Railway does not expose WS_PORT directly.
WS_PORT=8765
WS_URL=

# Optional Discord IDs. Defaults exist in bot.py, but setting them in Railway is cleaner.
TICKET_CHANNEL_ID=your_ticket_panel_channel_id_here
ORDER_CHANNEL_ID=your_order_log_channel_id_here
WELCOME_CHANNEL_ID=your_welcome_channel_id_here
LOG_CHANNEL_ID=your_log_channel_id_here
LEADERBOARD_CHANNEL_ID=your_leaderboard_channel_id_here
LINKS_ALLOWED_CHANNEL=your_links_allowed_channel_id_here
SELF_ROLES_CHANNEL_ID=your_self_roles_channel_id_here
FEEDBACK_CHANNEL_ID=your_feedback_channel_id_here
TICKET_CATEGORY_ID=your_ticket_category_id_here
STAFF_ROLE_ID=your_staff_role_id_here
MEMBER_ROLE_ID=your_member_role_id_here
SECURITY_ROLE_ID=your_security_role_id_here
ROLE_ENGLISH=your_english_role_id_here
ROLE_ARABIC=your_arabic_role_id_here
ROLE_ARC=your_arc_raiders_role_id_here
ROLE_PUBG_MOB=your_pubg_mobile_role_id_here
ROLE_PUBG_STEAM=your_pubg_steam_role_id_here
```

## `.gitignore`
```gitignore
.env
*.env
__pycache__/
*.py[cod]
.Python
.venv/
venv/
.env.local
.env.*.local
.DS_Store
*.log
```

## `Procfile`
```Procfile
web: python railway_start.py
```

## `README.md`
```markdown
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
```

## `requirements.txt`
```text
py-cord==2.4.1
aiohttp==3.8.6
pymongo==4.6.1
dnspython==2.6.1
flask==3.0.3
gunicorn==22.0.0
requests==2.32.3
websockets==12.0
PyNaCl==1.5.0
python-dotenv==1.0.1
```

## `runtime.txt`
```text
python-3.11.9
```

## `railway.json`
```json
{
  "$schema": "https://railway.com/railway.schema.json",
  "build": {
    "builder": "RAILPACK"
  },
  "deploy": {
    "startCommand": "python railway_start.py",
    "healthcheckPath": "/healthz",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

## `railway_start.py`
```python
import os
import signal
import subprocess
import sys
import time


def _env_mode() -> str:
    return os.getenv("RAILWAY_MODE", "all").strip().lower()


def _gunicorn_cmd() -> list[str]:
    port = os.getenv("PORT", "5001")
    workers = os.getenv("WEB_CONCURRENCY", "1")
    timeout = os.getenv("GUNICORN_TIMEOUT", "120")
    return [
        sys.executable,
        "-m",
        "gunicorn",
        "app:app",
        "--bind",
        f"0.0.0.0:{port}",
        "--workers",
        workers,
        "--timeout",
        timeout,
        "--access-logfile",
        "-",
        "--error-logfile",
        "-",
    ]


def _bot_cmd() -> list[str]:
    return [sys.executable, "bot.py"]


def _start(cmd: list[str], name: str) -> subprocess.Popen:
    print(f"[railway] starting {name}: {' '.join(cmd)}", flush=True)
    return subprocess.Popen(cmd)


def _terminate(processes: list[subprocess.Popen]) -> None:
    for proc in processes:
        if proc.poll() is None:
            proc.terminate()
    deadline = time.time() + 15
    while time.time() < deadline:
        if all(proc.poll() is not None for proc in processes):
            return
        time.sleep(0.25)
    for proc in processes:
        if proc.poll() is None:
            proc.kill()


def main() -> int:
    mode = _env_mode()
    processes: list[subprocess.Popen] = []

    if mode in {"all", "web", "dashboard"}:
        processes.append(_start(_gunicorn_cmd(), "dashboard"))
    if mode in {"all", "bot", "worker"}:
        processes.append(_start(_bot_cmd(), "discord-bot"))

    if not processes:
        print(f"[railway] invalid RAILWAY_MODE={mode!r}. Use all, dashboard, or bot.", flush=True)
        return 2

    shutting_down = False

    def handle_signal(signum, frame):
        nonlocal shutting_down
        if shutting_down:
            return
        shutting_down = True
        print(f"[railway] received signal {signum}; stopping processes...", flush=True)
        _terminate(processes)

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    try:
        while True:
            for proc in processes:
                code = proc.poll()
                if code is not None:
                    print(f"[railway] process exited with code {code}; stopping remaining processes.", flush=True)
                    _terminate(processes)
                    return int(code or 0)
            time.sleep(1)
    finally:
        _terminate(processes)


if __name__ == "__main__":
    raise SystemExit(main())
```

## `app.py`
```python
import os
from datetime import datetime, timezone
from functools import wraps

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

import requests
from bson import ObjectId
from flask import Flask, redirect, render_template, request, session, url_for
from pymongo import MongoClient, DESCENDING

app = Flask(__name__)
app.secret_key = os.getenv("DASHBOARD_SECRET") or os.getenv("SECRET_KEY") or "change-this-dashboard-secret"

MONGODB_URI = os.getenv("MONGODB_URI", "").strip()
DB_NAME = os.getenv("MONGODB_DB", "mem_store")
_mongo_client = None
_db = None

DEFAULT_FOOTER = "Powered by MEM Development | Deaplo"
DEFAULT_EMBED_COLOR = "#1a2332"
LOG_TYPES = ["all", "moderation", "ticket", "member", "message", "order", "automod", "voice", "general"]
DEFAULT_BAD_WORDS = [
    "fuck", "shit", "bitch", "asshole", "bastard", "cunt", "damn", "dick",
    "pussy", "nigga", "nigger", "faggot", "retard", "whore", "slut",
    "كس", "زب", "طيز", "منيوك", "شرموط", "عرص", "خول", "متناك",
    "كلب", "حمار", "زنيك", "نيك", "ابن الشرموطة", "ابن الكلب",
    "يلعن", "العن", "لعنة", "قحبة", "وسخ",
]

DEFAULT_LANGUAGE_ROLES = {
    "English": int(os.getenv("ROLE_ENGLISH", "1506219132037763092")),
    "Arabic": int(os.getenv("ROLE_ARABIC", "1506219366939885669")),
}
DEFAULT_GAME_ROLES = {
    "ARC Raiders": int(os.getenv("ROLE_ARC", "1506219518567911566")),
    "PUBG Mobile": int(os.getenv("ROLE_PUBG_MOB", "1506219627246649455")),
    "PUBG Steam": int(os.getenv("ROLE_PUBG_STEAM", "1506219763171463209")),
}


def get_db():
    global _mongo_client, _db
    if not MONGODB_URI:
        raise RuntimeError("MONGODB_URI is missing. Add it to Railway Variables / Environment Variables.")
    if _db is None:
        _mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        _db = _mongo_client[DB_NAME]
    return _db


def is_logged_in():
    return session.get("logged_in") is True


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not is_logged_in():
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper


def object_id(value):
    try:
        return ObjectId(value)
    except Exception:
        return None


def to_int(value, default=None):
    try:
        if value is None or value == "":
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def fmt_time(value):
    if not value:
        return "—"
    if isinstance(value, str):
        return value[:16].replace("T", " ")
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M")
    return str(value)


def fmt_duration(seconds):
    seconds = int(seconds or 0)
    minutes, sec = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m"
    if minutes:
        return f"{minutes}m {sec}s"
    return f"{sec}s"


def mention(user_id):
    return f"<@{user_id}>" if user_id else "—"


def get_config(key, default=None):
    doc = get_db()["config"].find_one({"key": key}) or {}
    if default:
        merged = default.copy()
        merged.update(doc)
        return merged
    return doc


def save_config(key, data):
    data = dict(data)
    data["key"] = key
    data["updated_at"] = datetime.now(timezone.utc)
    get_db()["config"].update_one({"key": key}, {"$set": data}, upsert=True)


def delete_by_id(collection, item_id):
    oid = object_id(item_id)
    if oid:
        get_db()[collection].delete_one({"_id": oid})


def leaderboard_rows(limit=50):
    rows = []
    for rank, doc in enumerate(get_db()["leaderboard"].find().sort("positive", DESCENDING).limit(limit), start=1):
        total = int(doc.get("total", 0))
        positive = int(doc.get("positive", 0))
        negative = max(total - positive, 0)
        ratio = round((positive / total) * 100) if total else 0
        seller_id = doc.get("seller_id")
        rows.append({
            "id": str(doc.get("_id")),
            "rank": rank,
            "seller_id": seller_id,
            "username": doc.get("seller_name") or mention(seller_id),
            "total": total,
            "positive": positive,
            "negative": negative,
            "ratio": ratio,
        })
    return rows


def log_rows(query=None, limit=100):
    rows = []
    query = query or {}
    for doc in get_db()["logs"].find(query).sort("timestamp", DESCENDING).limit(limit):
        rows.append({
            "id": str(doc.get("_id")),
            "type": doc.get("type", "general"),
            "title": doc.get("title", "Log"),
            "description": doc.get("description", ""),
            "time": fmt_time(doc.get("timestamp")),
        })
    return rows


def ticket_rows(limit=100):
    rows = []
    for doc in get_db()["tickets"].find().sort("opened_at", DESCENDING).limit(limit):
        rows.append({
            "id": str(doc.get("_id")),
            "username": doc.get("username") or mention(doc.get("user_id")),
            "user_id": doc.get("user_id", "—"),
            "type": doc.get("type", "N/A"),
            "seller": mention(doc.get("seller_id")) if doc.get("seller_id") else "Unclaimed",
            "status": doc.get("status", "open"),
            "time": fmt_time(doc.get("opened_at")),
        })
    return rows


def warning_rows(limit=100):
    rows = []
    for doc in get_db()["warnings"].find().sort("timestamp", DESCENDING).limit(limit):
        rows.append({
            "id": str(doc.get("_id")),
            "username": doc.get("username") or mention(doc.get("user_id")),
            "user_id": doc.get("user_id", "—"),
            "reason": doc.get("reason", "No reason provided"),
            "by": mention(doc.get("by")),
            "time": fmt_time(doc.get("timestamp")),
        })
    return rows


def blacklist_rows(limit=100):
    rows = []
    for doc in get_db()["blacklist"].find().sort("added_at", DESCENDING).limit(limit):
        rows.append({
            "id": str(doc.get("_id")),
            "username": doc.get("username") or mention(doc.get("user_id")),
            "user_id": doc.get("user_id", "—"),
            "reason": doc.get("reason", "No reason provided"),
        })
    return rows


def moderation_stats():
    db = get_db()
    return {
        "total": db["warnings"].count_documents({}),
        "bans": db["logs"].count_documents({"title": {"$regex": "Banned", "$options": "i"}}),
        "kicks": db["logs"].count_documents({"title": {"$regex": "Kicked", "$options": "i"}}),
        "timeouts": db["logs"].count_documents({"title": {"$regex": "Timed Out|Timeout", "$options": "i"}}),
    }


def ticket_stats():
    db = get_db()
    return {
        "total": db["tickets"].count_documents({}),
        "sell": db["tickets"].count_documents({"type": "Sell"}),
        "buy": db["tickets"].count_documents({"type": "Buy"}),
        "partner": db["tickets"].count_documents({"type": "Partner"}),
    }


def home_stats():
    db = get_db()
    return {
        "tickets": db["tickets"].count_documents({}),
        "orders": db["logs"].count_documents({"type": "order"}),
        "warnings": db["warnings"].count_documents({}),
        "voice_calls": db["voice_calls"].count_documents({}),
    }


def analytics_stats():
    stats = home_stats()
    stats["logs"] = get_db()["logs"].count_documents({})
    stats.update(ticket_stats())
    return stats


def type_counts():
    counts = {t: 0 for t in LOG_TYPES if t != "all"}
    pipeline = [{"$group": {"_id": "$type", "count": {"$sum": 1}}}]
    for row in get_db()["logs"].aggregate(pipeline):
        counts[row.get("_id") or "general"] = row.get("count", 0)
    return {k: v for k, v in counts.items() if v}


def current_settings():
    defaults = {
        "log_channel": os.getenv("LOG_CHANNEL_ID", "1505308788780040222"),
        "ticket_channel": os.getenv("TICKET_CHANNEL_ID", "1505921799978881105"),
        "order_channel": os.getenv("ORDER_CHANNEL_ID", "1504265744719020122"),
        "feedback_channel": os.getenv("FEEDBACK_CHANNEL_ID", "1506926493798764635"),
        "welcome_channel": os.getenv("WELCOME_CHANNEL_ID", "1505922477753368740"),
        "lb_channel": os.getenv("LEADERBOARD_CHANNEL_ID", "1505922561903562812"),
        "footer": DEFAULT_FOOTER,
        "embed_color": DEFAULT_EMBED_COLOR,
        "systems": {
            "tickets": True,
            "orders": True,
            "welcome": True,
            "automod": True,
            "leaderboard": True,
            "logging": True,
        },
    }
    return get_config("settings", defaults)


@app.route("/healthz")
def healthz():
    return {"status": "ok"}, 200


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        expected = os.getenv("DASHBOARD_PASSWORD", "")
        if not expected:
            return render_template("login.html", error="DASHBOARD_PASSWORD is missing in environment variables.")
        if request.form.get("password") == expected:
            session["logged_in"] = True
            return redirect(url_for("home"))
        return render_template("login.html", error="Wrong password.")
    return render_template("login.html", error=None)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def home():
    return render_template(
        "home.html",
        stats=home_stats(),
        top_sellers=leaderboard_rows(3),
        recent_logs=log_rows(limit=8),
    )


@app.route("/analytics")
@login_required
def analytics():
    return render_template(
        "analytics.html",
        stats=analytics_stats(),
        type_counts=type_counts(),
        top_sellers=leaderboard_rows(5),
    )


@app.route("/tickets")
@login_required
def tickets():
    defaults = {"title": "🎫 MEM Store | Ticket Center", "footer": DEFAULT_FOOTER, "description": ""}
    return render_template("tickets.html", stats=ticket_stats(), tickets=ticket_rows(), config=get_config("ticket_config", defaults))


@app.route("/save_ticket_config", methods=["POST"])
@login_required
def save_ticket_config():
    save_config("ticket_config", {
        "title": request.form.get("title", "").strip(),
        "footer": request.form.get("footer", DEFAULT_FOOTER).strip(),
        "category_id": request.form.get("category_id", "").strip(),
        "log_channel": request.form.get("log_channel", "").strip(),
        "description": request.form.get("description", "").strip(),
    })
    return redirect(url_for("tickets"))


@app.route("/delete_ticket/<item_id>", methods=["POST"])
@login_required
def delete_ticket(item_id):
    delete_by_id("tickets", item_id)
    return redirect(url_for("tickets"))


@app.route("/marketplace")
@login_required
def marketplace():
    return render_template(
        "marketplace.html",
        leaderboard=leaderboard_rows(),
        orders=log_rows({"type": "order"}, limit=20),
        feedback=log_rows({"title": {"$regex": "Feedback", "$options": "i"}}, limit=20),
    )


@app.route("/reset_leaderboard", methods=["POST"])
@login_required
def reset_leaderboard():
    get_db()["leaderboard"].delete_many({})
    return redirect(url_for("marketplace"))


@app.route("/delete_seller/<item_id>", methods=["POST"])
@login_required
def delete_seller(item_id):
    delete_by_id("leaderboard", item_id)
    return redirect(url_for("marketplace"))


@app.route("/moderation")
@login_required
def moderation():
    return render_template(
        "moderation.html",
        stats=moderation_stats(),
        warns=warning_rows(),
        blacklist=blacklist_rows(),
    )


@app.route("/delete_warning/<item_id>", methods=["POST"])
@login_required
def delete_warning(item_id):
    delete_by_id("warnings", item_id)
    return redirect(request.referrer or url_for("moderation"))


@app.route("/clear_user_warnings/<user_id>", methods=["POST"])
@login_required
def clear_user_warnings(user_id):
    get_db()["warnings"].delete_many({"user_id": to_int(user_id, user_id)})
    return redirect(request.referrer or url_for("moderation"))


@app.route("/add_blacklist", methods=["POST"])
@login_required
def add_blacklist():
    user_id = to_int(request.form.get("user_id"), request.form.get("user_id"))
    reason = request.form.get("reason", "No reason provided")
    get_db()["blacklist"].update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id, "reason": reason, "added_at": datetime.now(timezone.utc)}},
        upsert=True,
    )
    return redirect(request.referrer or url_for("moderation"))


@app.route("/remove_blacklist/<item_id>", methods=["POST"])
@login_required
def remove_blacklist(item_id):
    delete_by_id("blacklist", item_id)
    return redirect(request.referrer or url_for("moderation"))


@app.route("/logs")
@login_required
def logs():
    current_type = request.args.get("type", "all")
    query = {} if current_type == "all" else {"type": current_type}
    return render_template(
        "logs.html",
        stats=moderation_stats(),
        logs=log_rows(query, limit=200),
        log_types=LOG_TYPES,
        current_type=current_type,
    )


@app.route("/clear_logs", methods=["POST"])
@login_required
def clear_logs():
    get_db()["logs"].delete_many({})
    return redirect(url_for("logs"))


@app.route("/roles")
@login_required
def roles():
    cfg = get_config("roles_config", {"language_roles": DEFAULT_LANGUAGE_ROLES, "game_roles": DEFAULT_GAME_ROLES})
    return render_template("roles.html", language_roles=cfg.get("language_roles", DEFAULT_LANGUAGE_ROLES), game_roles=cfg.get("game_roles", DEFAULT_GAME_ROLES))


@app.route("/save_roles", methods=["POST"])
@login_required
def save_roles():
    lang_names = request.form.getlist("lang_name")
    lang_ids = request.form.getlist("lang_id")
    game_names = request.form.getlist("game_name")
    game_ids = request.form.getlist("game_id")

    def build_map(names, ids):
        result = {}
        for name, role_id in zip(names, ids):
            name = (name or "").strip()
            role_id = to_int(role_id)
            if name and role_id:
                result[name] = role_id
        return result

    save_config("roles_config", {
        "language_roles": build_map(lang_names, lang_ids),
        "game_roles": build_map(game_names, game_ids),
    })
    return redirect(url_for("roles"))


@app.route("/welcome")
@login_required
def welcome():
    return render_template("welcome.html", config=get_config("welcome_config", {}))


@app.route("/save_welcome", methods=["POST"])
@login_required
def save_welcome():
    save_config("welcome_config", {
        "welcome_channel": request.form.get("welcome_channel", "").strip(),
        "member_role": request.form.get("member_role", "").strip(),
        "message": request.form.get("message", "").strip(),
        "leave_message": request.form.get("leave_message", "").strip(),
    })
    return redirect(url_for("welcome"))


@app.route("/security")
@login_required
def security():
    sec_defaults = {
        "anti_raid": False,
        "anti_bot": False,
        "anti_scam": True,
        "anti_mention": True,
        "anti_spam": True,
        "anti_links": True,
        "spam_limit": 5,
        "spam_window": 5,
        "mention_limit": 5,
    }
    bw_cfg = get_config("bad_words", {"words": DEFAULT_BAD_WORDS})
    return render_template("security.html", config=get_config("security_config", sec_defaults), bad_words=bw_cfg.get("words", DEFAULT_BAD_WORDS))


@app.route("/save_security", methods=["POST"])
@login_required
def save_security():
    bool_keys = ["anti_raid", "anti_bot", "anti_scam", "anti_mention", "anti_spam", "anti_links"]
    data = {key: key in request.form for key in bool_keys}
    data.update({
        "spam_limit": to_int(request.form.get("spam_limit"), 5),
        "spam_window": to_int(request.form.get("spam_window"), 5),
        "mention_limit": to_int(request.form.get("mention_limit"), 5),
    })
    save_config("security_config", data)
    bad_words = [w.strip() for w in request.form.get("bad_words_list", "").splitlines() if w.strip()]
    save_config("bad_words", {"words": bad_words or DEFAULT_BAD_WORDS})
    return redirect(url_for("security"))


@app.route("/settings")
@login_required
def settings():
    return render_template("settings.html", config=current_settings())


@app.route("/save_settings", methods=["POST"])
@login_required
def save_settings():
    systems = {
        "tickets": "sys_tickets" in request.form,
        "orders": "sys_orders" in request.form,
        "welcome": "sys_welcome" in request.form,
        "automod": "sys_automod" in request.form,
        "leaderboard": "sys_leaderboard" in request.form,
        "logging": "sys_logging" in request.form,
    }
    save_config("settings", {
        "log_channel": request.form.get("log_channel", "").strip(),
        "ticket_channel": request.form.get("ticket_channel", "").strip(),
        "order_channel": request.form.get("order_channel", "").strip(),
        "feedback_channel": request.form.get("feedback_channel", "").strip(),
        "welcome_channel": request.form.get("welcome_channel", "").strip(),
        "lb_channel": request.form.get("lb_channel", "").strip(),
        "footer": request.form.get("footer", DEFAULT_FOOTER).strip(),
        "embed_color": request.form.get("embed_color", DEFAULT_EMBED_COLOR),
        "systems": systems,
    })
    return redirect(url_for("settings"))


@app.route("/embeds")
@login_required
def embeds():
    return render_template("embeds.html", saved_embeds=saved_embed_rows(), flash_msg=None, form_data={})


def saved_embed_rows():
    rows = []
    for doc in get_db()["saved_embeds"].find().sort("created_at", DESCENDING).limit(50):
        rows.append({
            "id": str(doc.get("_id")),
            "title": doc.get("title", ""),
            "description": doc.get("description", ""),
        })
    return rows


def hex_to_int(value):
    try:
        return int((value or DEFAULT_EMBED_COLOR).strip().lstrip("#"), 16)
    except Exception:
        return 0x1A2332


@app.route("/send_embed", methods=["POST"])
@login_required
def send_embed():
    form_data = dict(request.form)
    token = os.getenv("DISCORD_TOKEN", "").strip()
    channel_id = request.form.get("channel_id", "").strip()
    if not token:
        return render_template("embeds.html", saved_embeds=saved_embed_rows(), flash_msg="❌ DISCORD_TOKEN is missing.", form_data=form_data)
    if not channel_id:
        return render_template("embeds.html", saved_embeds=saved_embed_rows(), flash_msg="❌ Channel ID is required.", form_data=form_data)

    embed = {
        "title": request.form.get("title", "")[:256],
        "description": request.form.get("description", "")[:4096],
        "color": hex_to_int(request.form.get("color")),
        "footer": {"text": request.form.get("footer") or DEFAULT_FOOTER},
    }
    image_url = request.form.get("image_url", "").strip()
    thumbnail = request.form.get("thumbnail", "").strip()
    if image_url:
        embed["image"] = {"url": image_url}
    if thumbnail:
        embed["thumbnail"] = {"url": thumbnail}

    resp = requests.post(
        f"https://discord.com/api/v10/channels/{channel_id}/messages",
        headers={"Authorization": f"Bot {token}", "Content-Type": "application/json"},
        json={"embeds": [embed]},
        timeout=15,
    )
    if resp.status_code not in (200, 201, 204):
        return render_template("embeds.html", saved_embeds=saved_embed_rows(), flash_msg=f"❌ Discord API error: {resp.status_code}", form_data=form_data)

    if "save_embed" in request.form:
        get_db()["saved_embeds"].insert_one({
            "title": embed.get("title", ""),
            "description": embed.get("description", ""),
            "color": request.form.get("color", DEFAULT_EMBED_COLOR),
            "footer": embed.get("footer", {}).get("text", DEFAULT_FOOTER),
            "image_url": image_url,
            "thumbnail": thumbnail,
            "created_at": datetime.now(timezone.utc),
        })
    return render_template("embeds.html", saved_embeds=saved_embed_rows(), flash_msg="✅ Embed sent successfully.", form_data={})


@app.route("/delete_embed/<item_id>", methods=["POST"])
@login_required
def delete_embed(item_id):
    delete_by_id("saved_embeds", item_id)
    return redirect(url_for("embeds"))


@app.route("/voice")
@login_required
def voice():
    calls = []
    total_seconds = 0
    for doc in get_db()["voice_calls"].find().sort("start", DESCENDING).limit(50):
        total_seconds += int(doc.get("duration", 0) or 0)
        calls.append({
            "channel": doc.get("channel", "Unknown"),
            "started_by": doc.get("started_by_name") or mention(doc.get("started_by")),
            "start": fmt_time(doc.get("start")),
            "end": fmt_time(doc.get("end")),
            "duration": fmt_duration(doc.get("duration", 0)),
        })
    ws_host = os.getenv("WS_PUBLIC_HOST") or request.host.split(":")[0]
    ws_port = os.getenv("WS_PORT", "8765")
    scheme = "wss" if request.is_secure else "ws"
    ws_url = os.getenv("WS_URL") or f"{scheme}://{ws_host}:{ws_port}"
    return render_template("voice.html", calls=calls, total_calls=len(calls), total_duration=fmt_duration(total_seconds), ws_url=ws_url)


@app.errorhandler(RuntimeError)
def runtime_error(error):
    return f"<h2>Configuration error</h2><p>{error}</p>", 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5001"))
    app.run(host="0.0.0.0", port=port)
```

## `bot.py`
```python
import discord
from discord.ext import commands
from discord.ui import View, Button
from discord import Option, PermissionOverwrite
from pymongo import MongoClient
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import asyncio
import os
import io
import re
import aiohttp
import queue
import json
import websockets
import websockets.exceptions

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# ═══════════════════════════════════════════════════════════════
#  ENVIRONMENT
# ═══════════════════════════════════════════════════════════════
def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is missing. Add it to Railway Variables / Environment Variables.")
    return value


def int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


DISCORD_TOKEN = required_env("DISCORD_TOKEN")
MONGODB_URI = required_env("MONGODB_URI")

# ═══════════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════════
GIF_URL  = os.getenv("GIF_URL", "")
LOGO_URL = os.getenv("LOGO_URL", "")

EMBED_COLOR  = 0x1a2332
FOOTER_TEXT  = "Powered by MEM Development | Deaplo"
SERVER_NAME  = "MEM Store"
GUILD_ID     = int_env("GUILD_ID", 1504256091872301116)

# ── Channels ──
TICKET_CHANNEL_ID      = int_env("TICKET_CHANNEL_ID", 1505921799978881105)
ORDER_CHANNEL_ID       = int_env("ORDER_CHANNEL_ID", 1504265744719020122)
WELCOME_CHANNEL_ID     = int_env("WELCOME_CHANNEL_ID", 1505922477753368740)
LOG_CHANNEL_ID         = int_env("LOG_CHANNEL_ID", 1505308788780040222)
LEADERBOARD_CHANNEL_ID = int_env("LEADERBOARD_CHANNEL_ID", 1505922561903562812)
LINKS_ALLOWED_CHANNEL  = int_env("LINKS_ALLOWED_CHANNEL", 1504271389656486049)
SELF_ROLES_CHANNEL_ID  = int_env("SELF_ROLES_CHANNEL_ID", 1506220242626543697)
FEEDBACK_CHANNEL_ID    = int_env("FEEDBACK_CHANNEL_ID", 1506926493798764635)

# ── Categories ──
TICKET_CATEGORY_ID = int_env("TICKET_CATEGORY_ID", 1505922835359596644)

# ── Roles ──
STAFF_ROLE_ID    = int_env("STAFF_ROLE_ID", 1504374917360128040)
MEMBER_ROLE_ID   = int_env("MEMBER_ROLE_ID", 1504383155921092808)
SECURITY_ROLE_ID = int_env("SECURITY_ROLE_ID", 1505133078111191142)
ARC_ROLE_ID      = int_env("ARC_ROLE_ID", 1506219518567911566)

LANGUAGE_ROLES = {
    "English": int_env("ROLE_ENGLISH", 1506219132037763092),
    "Arabic":  int_env("ROLE_ARABIC", 1506219366939885669),
}
GAME_ROLES = {
    "ARC Raiders": int_env("ROLE_ARC", 1506219518567911566),
    "PUBG Mobile": int_env("ROLE_PUBG_MOB", 1506219627246649455),
    "PUBG Steam":  int_env("ROLE_PUBG_STEAM", 1506219763171463209),
}

# ── Bad Words Filter ──
BAD_WORDS = [
    "fuck", "shit", "bitch", "asshole", "bastard", "cunt", "damn", "dick",
    "pussy", "nigga", "nigger", "faggot", "retard", "whore", "slut",
    "كس", "زب", "طيز", "منيوك", "شرموط", "عرص", "خول", "متناك",
    "كلب", "حمار", "زنيك", "نيك", "ابن الشرموطة", "ابن الكلب",
    "يلعن", "العن", "لعنة", "قحبة", "وسخ",
]

# ── Anti Spam ──
spam_tracker = defaultdict(list)
SPAM_LIMIT   = 5
SPAM_WINDOW  = 5

# ── WebSocket Port ──
WS_PORT = int_env("WS_PORT", 8765)

# ─────────────────────────────────────────
#  DATABASE
# ─────────────────────────────────────────
mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
DB_NAME = os.getenv("MONGODB_DB", "mem_store")
db = mongo_client[DB_NAME]


# ─────────────────────────────────────────
#  DYNAMIC DASHBOARD CONFIG HELPERS
# ─────────────────────────────────────────
def cfg_doc(key: str) -> dict:
    try:
        return db["config"].find_one({"key": key}) or {}
    except Exception:
        return {}


def settings_doc() -> dict:
    return cfg_doc("settings")


def system_enabled(name: str, default: bool = True) -> bool:
    systems = settings_doc().get("systems", {})
    return bool(systems.get(name, default))


def int_value(value, fallback: int) -> int:
    try:
        if value in (None, ""):
            return fallback
        return int(value)
    except (TypeError, ValueError):
        return fallback


def setting_int(name: str, fallback: int) -> int:
    return int_value(settings_doc().get(name), fallback)


def ticket_config_int(name: str, fallback: int) -> int:
    return int_value(cfg_doc("ticket_config").get(name), fallback)


def welcome_config_int(name: str, fallback: int) -> int:
    return int_value(cfg_doc("welcome_config").get(name), fallback)


def current_footer() -> str:
    return settings_doc().get("footer") or FOOTER_TEXT


def current_embed_color() -> int:
    raw = settings_doc().get("embed_color", "#1a2332")
    try:
        return int(str(raw).lstrip("#"), 16)
    except Exception:
        return EMBED_COLOR


def get_role_maps() -> tuple[dict, dict]:
    cfg = cfg_doc("roles_config")
    language = cfg.get("language_roles") or LANGUAGE_ROLES
    games = cfg.get("game_roles") or GAME_ROLES
    return language, games

# ─────────────────────────────────────────
#  VOICE RELAY
# ─────────────────────────────────────────
audio_queue: queue.Queue = queue.Queue(maxsize=500)
ws_clients: set = set()
voice_session: dict = {}   # {guild_id: {"channel": name, "channel_id": id, "start": iso_str}}
ws_server_task = None


class MicAudioSource(discord.AudioSource):
    FRAME_SIZE = 3840  # 20ms @ 48kHz stereo 16-bit

    def __init__(self):
        self.buffer = b''
        self.silence = b'\x00' * self.FRAME_SIZE

    def read(self) -> bytes:
        while len(self.buffer) < self.FRAME_SIZE:
            try:
                self.buffer += audio_queue.get_nowait()
            except queue.Empty:
                return self.silence
        frame = self.buffer[:self.FRAME_SIZE]
        self.buffer = self.buffer[self.FRAME_SIZE:]
        return frame

    def is_opus(self) -> bool:
        return False


async def _ws_broadcast(data: dict):
    if ws_clients:
        msg = json.dumps(data)
        await asyncio.gather(*[c.send(msg) for c in list(ws_clients)],
                             return_exceptions=True)


async def ws_handler(websocket):
    ws_clients.add(websocket)
    if bot.is_ready():
        await websocket.send(json.dumps({"type": "bot_ready", "user": str(bot.user)}))
    for guild in bot.guilds:
        if guild.voice_client and guild.voice_client.is_connected():
            sess = voice_session.get(guild.id, {})
            await websocket.send(json.dumps({
                "type": "joined",
                "channel": guild.voice_client.channel.name,
                "channel_id": guild.voice_client.channel.id,
                "start": sess.get("start", ""),
                "members": [m.name for m in guild.voice_client.channel.members if not m.bot]
            }))
            break
    try:
        async for message in websocket:
            if isinstance(message, bytes):
                try:
                    audio_queue.put_nowait(message)
                except queue.Full:
                    try:
                        audio_queue.get_nowait()
                        audio_queue.put_nowait(message)
                    except queue.Empty:
                        pass
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        ws_clients.discard(websocket)

# ─────────────────────────────────────────
#  BOT SETUP
# ─────────────────────────────────────────
intents = discord.Intents.all()
bot = discord.Bot(intents=intents)

# ─────────────────────────────────────────
#  HELPER: SEND LOG
# ─────────────────────────────────────────
async def send_log(guild, title: str, description: str, color: int = EMBED_COLOR, fields: list = None):
    if not guild or not system_enabled("logging", True):
        return
    channel_id = ticket_config_int("log_channel", setting_int("log_channel", LOG_CHANNEL_ID))
    channel = guild.get_channel(channel_id)
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.now(timezone.utc)
    )
    if fields:
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
    embed.set_footer(text=current_footer())
    if channel:
        try:
            await channel.send(embed=embed)
        except Exception:
            pass
    try:
        log_entry = {
            "guild_id":    guild.id,
            "title":       title,
            "description": description,
            "fields":      [{"name": f[0], "value": f[1]} for f in (fields or [])],
            "timestamp":   datetime.now(timezone.utc),
            "color":       color,
        }
        if any(x in title for x in ["Ban", "Kick", "Warn", "Timeout", "Timed Out", "Blacklist"]):
            log_entry["type"] = "moderation"
        elif "Ticket" in title:
            log_entry["type"] = "ticket"
        elif any(x in title for x in ["Member", "Join", "Left"]):
            log_entry["type"] = "member"
        elif any(x in title for x in ["Message", "Edit", "Delete"]):
            log_entry["type"] = "message"
        elif "Order" in title:
            log_entry["type"] = "order"
        elif any(x in title for x in ["Spam", "Link", "Bad Word", "Mention"]):
            log_entry["type"] = "automod"
        elif any(x in title for x in ["Voice", "Joined Voice", "Left Voice"]):
            log_entry["type"] = "voice"
        else:
            log_entry["type"] = "general"
        db["logs"].insert_one(log_entry)
    except Exception:
        pass

# ─────────────────────────────────────────
#  HELPER: SECURITY CHECK
# ─────────────────────────────────────────
def has_security_role():
    async def predicate(ctx):
        if not ctx.guild:
            await ctx.respond("❌ This command can only be used inside a server.", ephemeral=True)
            return False
        if ctx.author.guild_permissions.administrator:
            return True
        role = ctx.guild.get_role(SECURITY_ROLE_ID)
        if not role or role not in ctx.author.roles:
            await ctx.respond("❌ You don't have permission to use this command.", ephemeral=True)
            return False
        return True
    return commands.check(predicate)

# ─────────────────────────────────────────
#  HELPER: DISCORD API CALL
# ─────────────────────────────────────────
async def discord_api(method: str, endpoint: str, data: dict = None):
    url     = f"https://discord.com/api/v10{endpoint}"
    headers = {
        "Authorization": f"Bot {DISCORD_TOKEN}",
        "Content-Type":  "application/json",
    }
    async with aiohttp.ClientSession() as session:
        async with session.request(method, url, json=data, headers=headers) as r:
            if r.status in (200, 201, 204):
                try:
                    return await r.json()
                except Exception:
                    return {}
            return None

# ═══════════════════════════════════════════════════════════════
#  ██  TICKETS SYSTEM
# ═══════════════════════════════════════════════════════════════

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Sell", emoji="💰", style=discord.ButtonStyle.secondary, custom_id="ticket_sell")
    async def sell_button(self, button: Button, interaction: discord.Interaction):
        await open_ticket(interaction, ticket_type="Sell")

    @discord.ui.button(label="Buy", emoji="🛒", style=discord.ButtonStyle.success, custom_id="ticket_buy")
    async def buy_button(self, button: Button, interaction: discord.Interaction):
        await open_ticket(interaction, ticket_type="Buy")

    @discord.ui.button(label="Partner", emoji="🤝", style=discord.ButtonStyle.danger, custom_id="ticket_partner")
    async def partner_button(self, button: Button, interaction: discord.Interaction):
        await open_ticket(interaction, ticket_type="Partner")


class TicketControlView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", emoji="🔒", style=discord.ButtonStyle.danger, custom_id="ticket_close")
    async def close_button(self, button: Button, interaction: discord.Interaction):
        await close_ticket(interaction)

    @discord.ui.button(label="Claim", emoji="✋", style=discord.ButtonStyle.primary, custom_id="ticket_claim")
    async def claim_button(self, button: Button, interaction: discord.Interaction):
        await claim_ticket(interaction)


class TicketRatingView(View):
    def __init__(self, seller_id: int):
        super().__init__(timeout=120)
        self.seller_id = seller_id

    @discord.ui.button(label="👍 Like", style=discord.ButtonStyle.success, custom_id="rating_like")
    async def like_button(self, button: Button, interaction: discord.Interaction):
        await submit_rating(interaction, self.seller_id, is_positive=True)
        self.stop()

    @discord.ui.button(label="👎 Dislike", style=discord.ButtonStyle.danger, custom_id="rating_dislike")
    async def dislike_button(self, button: Button, interaction: discord.Interaction):
        await submit_rating(interaction, self.seller_id, is_positive=False)
        self.stop()


async def open_ticket(interaction: discord.Interaction, ticket_type: str):
    guild  = interaction.guild
    member = interaction.user
    if not guild:
        await interaction.response.send_message("❌ Tickets can only be opened inside a server.", ephemeral=True)
        return
    if not system_enabled("tickets", True):
        await interaction.response.send_message("❌ Ticket system is currently disabled.", ephemeral=True)
        return
    existing_ticket = db["tickets"].find_one({"guild_id": guild.id, "user_id": member.id, "status": "open"})
    if existing_ticket:
        channel = guild.get_channel(existing_ticket.get("channel_id"))
        if channel:
            await interaction.response.send_message(f"❌ You already have an open ticket: {channel.mention}", ephemeral=True)
            return
    await interaction.response.defer(ephemeral=True)
    category_id = ticket_config_int("category_id", TICKET_CATEGORY_ID)
    category = discord.utils.get(guild.categories, id=category_id)
    staff_role = guild.get_role(STAFF_ROLE_ID)
    overwrites = {
        guild.default_role: PermissionOverwrite(view_channel=False, send_messages=False),
        member:             PermissionOverwrite(view_channel=True, send_messages=True),
    }
    if staff_role:
        overwrites[staff_role] = PermissionOverwrite(view_channel=True, send_messages=True)
    safe_name = member.name.lower().replace(" ", "-")[:30]
    try:
        channel = await guild.create_text_channel(
            name=f"ticket-{safe_name}-{member.id}",
            category=category,
            overwrites=overwrites,
        )
    except discord.Forbidden:
        await interaction.followup.send("❌ I do not have permission to create ticket channels.", ephemeral=True)
        return
    except Exception as exc:
        await interaction.followup.send(f"❌ Failed to create ticket: {exc}", ephemeral=True)
        return
    ticket_data = {
        "guild_id":  guild.id,
        "channel_id":channel.id,
        "user_id":   member.id,
        "username":  str(member),
        "type":      ticket_type,
        "status":    "open",
        "opened_at": datetime.now(timezone.utc),
        "seller_id": None,
    }
    db["tickets"].insert_one(ticket_data)
    color_map = {"Sell": 0xF1C40F, "Buy": 0x2ECC71, "Partner": 0x5865F2}
    embed = discord.Embed(
        title=f"{'💰' if ticket_type=='Sell' else '🛒' if ticket_type=='Buy' else '🤝'} {ticket_type} Ticket",
        description=(
            f"Welcome {member.mention}!\n\n"
            f"**Type:** {ticket_type}\n"
            f"**Opened:** <t:{int(datetime.now(timezone.utc).timestamp())}:R>\n\n"
            "Please describe your request and wait for a staff member."
        ),
        color=color_map.get(ticket_type, current_embed_color()),
    )
    embed.set_footer(text=current_footer())
    if LOGO_URL:
        embed.set_thumbnail(url=LOGO_URL)
    await channel.send(embed=embed, view=TicketControlView())
    await interaction.followup.send(f"✅ Ticket opened: {channel.mention}", ephemeral=True)
    await send_log(guild, f"🎫 Ticket Opened — {ticket_type}",
                   f"**User:** {member.mention}\n**Channel:** {channel.mention}\n**Type:** {ticket_type}",
                   color=color_map.get(ticket_type, current_embed_color()))

async def close_ticket(interaction: discord.Interaction):
    channel = interaction.channel
    guild   = interaction.guild
    ticket  = db["tickets"].find_one({"channel_id": channel.id, "status": "open"})
    if not ticket:
        await interaction.response.send_message("❌ This is not an open ticket.", ephemeral=True)
        return
    await interaction.response.defer()
    seller_id = ticket.get("seller_id")
    user_id   = ticket.get("user_id")
    db["tickets"].update_one({"channel_id": channel.id}, {"$set": {"status": "closed", "closed_at": datetime.now(timezone.utc)}})
    await send_log(guild, "🔒 Ticket Closed",
                   f"**Channel:** {channel.name}\n**Type:** {ticket.get('type','N/A')}",
                   color=0xE74C3C)
    if seller_id and user_id:
        user = guild.get_member(user_id)
        if user:
            try:
                rating_embed = discord.Embed(
                    title="⭐ Rate Your Experience",
                    description=f"Please rate your transaction in **{channel.name}**.",
                    color=EMBED_COLOR,
                )
                rating_embed.set_footer(text=current_footer())
                await user.send(embed=rating_embed, view=TicketRatingView(seller_id))
            except Exception:
                pass
    await channel.delete()


async def claim_ticket(interaction: discord.Interaction):
    channel = interaction.channel
    guild   = interaction.guild
    member  = interaction.user
    staff_role = guild.get_role(STAFF_ROLE_ID)
    if not staff_role or staff_role not in member.roles:
        await interaction.response.send_message("❌ Only staff can claim tickets.", ephemeral=True)
        return
    ticket = db["tickets"].find_one({"channel_id": channel.id})
    if not ticket:
        await interaction.response.send_message("❌ Ticket not found.", ephemeral=True)
        return
    db["tickets"].update_one({"channel_id": channel.id}, {"$set": {"seller_id": member.id}})
    await interaction.response.send_message(f"✅ Ticket claimed by {member.mention}!")
    await send_log(guild, "✋ Ticket Claimed",
                   f"**Channel:** {channel.name}\n**Claimed by:** {member.mention}")


async def submit_rating(interaction: discord.Interaction, seller_id: int, is_positive: bool):
    db["leaderboard"].update_one(
        {"seller_id": seller_id},
        {"$inc": {"total": 1, "positive": 1 if is_positive else 0}, "$set": {"updated_at": datetime.now(timezone.utc)}},
        upsert=True,
    )
    emoji = "👍" if is_positive else "👎"
    await interaction.response.send_message(
        f"{emoji} Rating submitted!", ephemeral=True
    )
    guild = interaction.guild or bot.get_guild(GUILD_ID)
    if guild:
        seller = guild.get_member(seller_id)
        seller_name = seller.mention if seller else f"<@{seller_id}>"
        await send_log(
            guild,
            f"⭐ Rating — {'Positive' if is_positive else 'Negative'}",
            f"**Seller:** {seller_name}\n**By:** {interaction.user.mention}\n**Type:** {'👍 Positive' if is_positive else '👎 Negative'}",
            color=0x2ECC71 if is_positive else 0xE74C3C,
        )
    # update leaderboard embed
    await update_leaderboard(guild)


async def update_leaderboard(guild):
    if not guild or not system_enabled("leaderboard", True):
        return
    channel = guild.get_channel(setting_int("lb_channel", LEADERBOARD_CHANNEL_ID))
    if not channel:
        return
    sellers = list(db["leaderboard"].find().sort("positive", -1).limit(10))
    desc = ""
    medals = ["🥇", "🥈", "🥉"]
    for i, s in enumerate(sellers):
        total    = s.get("total", 0)
        positive = s.get("positive", 0)
        ratio    = round((positive / total) * 100) if total > 0 else 0
        medal    = medals[i] if i < 3 else f"**#{i+1}**"
        member   = guild.get_member(s["seller_id"])
        name     = member.mention if member else f"<@{s['seller_id']}>"
        desc    += f"{medal} {name} — 👍 {positive}/{total} ({ratio}%)\n"
    embed = discord.Embed(
        title="🏆 Seller Leaderboard",
        description=desc or "No data yet.",
        color=0xF1C40F,
        timestamp=datetime.now(timezone.utc),
    )
    embed.set_footer(text=current_footer())
    saved = db["config"].find_one({"key": "leaderboard_message"})
    if saved:
        try:
            msg = await channel.fetch_message(saved["message_id"])
            await msg.edit(embed=embed)
            return
        except Exception:
            pass
    msg = await channel.send(embed=embed)
    db["config"].update_one(
        {"key": "leaderboard_message"},
        {"$set": {"message_id": msg.id}},
        upsert=True,
    )

# ═══════════════════════════════════════════════════════════════
#  ██  SELF ROLES SYSTEM
# ═══════════════════════════════════════════════════════════════

class LanguageRoleView(View):
    def __init__(self):
        super().__init__(timeout=None)
        language_roles, _ = get_role_maps()
        for label, role_id in language_roles.items():
            self.add_item(LanguageRoleButton(label=label, role_id=int(role_id)))


class LanguageRoleButton(Button):
    def __init__(self, label: str, role_id: int):
        super().__init__(label=label, style=discord.ButtonStyle.secondary, custom_id=f"lang_{role_id}")
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        member = interaction.user
        guild  = interaction.guild
        role   = guild.get_role(self.role_id)
        if not role:
            await interaction.response.send_message("❌ Role not found.", ephemeral=True)
            return
        if role in member.roles:
            await member.remove_roles(role)
            await interaction.response.send_message(f"✅ Removed **{role.name}**", ephemeral=True)
        else:
            await member.add_roles(role)
            await interaction.response.send_message(f"✅ Added **{role.name}**", ephemeral=True)


class GameRoleView(View):
    def __init__(self):
        super().__init__(timeout=None)
        _, game_roles = get_role_maps()
        styles = [discord.ButtonStyle.primary, discord.ButtonStyle.success, discord.ButtonStyle.secondary]
        for i, (label, role_id) in enumerate(game_roles.items()):
            self.add_item(GameRoleButton(label=label, role_id=int(role_id), style=styles[i % len(styles)]))


class GameRoleButton(Button):
    def __init__(self, label: str, role_id: int, style):
        super().__init__(label=label, style=style, custom_id=f"game_{role_id}")
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        member = interaction.user
        guild  = interaction.guild
        role   = guild.get_role(self.role_id)
        if not role:
            await interaction.response.send_message("❌ Role not found.", ephemeral=True)
            return
        if role in member.roles:
            await member.remove_roles(role)
            await interaction.response.send_message(f"✅ Removed **{role.name}**", ephemeral=True)
        else:
            await member.add_roles(role)
            await interaction.response.send_message(f"✅ Added **{role.name}**", ephemeral=True)

# ═══════════════════════════════════════════════════════════════
#  ██  EVENTS
# ═══════════════════════════════════════════════════════════════

@bot.event
async def on_ready():
    global ws_server_task
    print(f"✅ Logged in as {bot.user} ({bot.user.id})")
    bot.add_view(TicketView())
    bot.add_view(TicketControlView())
    bot.add_view(LanguageRoleView())
    bot.add_view(GameRoleView())
    if ws_server_task is None or ws_server_task.done():
        ws_server_task = asyncio.create_task(start_ws_server())


@bot.event
async def on_member_join(member: discord.Member):
    guild = member.guild
    cfg = cfg_doc("welcome_config")
    # Auto-assign member role
    role_id = cfg.get("member_role") or MEMBER_ROLE_ID
    role = guild.get_role(int(role_id)) if role_id else None
    if role:
        try:
            await member.add_roles(role)
        except Exception:
            pass
    # Welcome message
    ch_id = cfg.get("welcome_channel") or setting_int("welcome_channel", WELCOME_CHANNEL_ID)
    channel = guild.get_channel(int_value(ch_id, WELCOME_CHANNEL_ID)) if ch_id else None
    if channel and system_enabled("welcome", True):
        msg = cfg.get("message", "We hope you have a great time.")
        count = guild.member_count
        embed = discord.Embed(
            title=f"👋 Welcome to {guild.name}!",
            description=(
                f"{member.mention} | <t:{int(datetime.now(timezone.utc).timestamp())}:R>\n\n"
                f"• Welcome **{member.name}**\n"
                f"• Our family now consists of **{count} Members**\n"
                f"• {msg}"
            ),
            color=0x2ECC71,
            timestamp=datetime.now(timezone.utc),
        )
        if LOGO_URL:
            embed.set_thumbnail(url=LOGO_URL)
        embed.set_footer(text=current_footer())
        await channel.send(embed=embed)
    await send_log(guild, "👋 Member Joined",
                   f"**User:** {member.mention}\n**Account:** <t:{int(member.created_at.timestamp())}:R>",
                   color=0x2ECC71)
    db["members"].update_one({"user_id": member.id}, {"$set": {"user_id": member.id, "joined_at": datetime.now(timezone.utc)}}, upsert=True)


@bot.event
async def on_member_remove(member: discord.Member):
    guild = member.guild
    cfg = cfg_doc("welcome_config")
    ch_id = cfg.get("welcome_channel") or setting_int("welcome_channel", WELCOME_CHANNEL_ID)
    channel = guild.get_channel(int_value(ch_id, WELCOME_CHANNEL_ID)) if ch_id else None
    if channel and system_enabled("welcome", True):
        leave_msg = cfg.get("leave_message", "Goodbye!")
        embed = discord.Embed(
            title=f"👋 {member.name} Left",
            description=leave_msg,
            color=0xE74C3C,
            timestamp=datetime.now(timezone.utc),
        )
        embed.set_footer(text=current_footer())
        await channel.send(embed=embed)
    await send_log(guild, "🚪 Member Left",
                   f"**User:** {member.name}\n**ID:** {member.id}",
                   color=0xE74C3C)


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot or not message.guild:
        return
    if not system_enabled("automod", True):
        return
    guild  = message.guild
    author = message.author
    content = message.content.lower()

    # ── Bad words ──
    bw_cfg = cfg_doc("bad_words")
    bad_list = bw_cfg.get("words", BAD_WORDS) if bw_cfg else BAD_WORDS
    for word in bad_list:
        if word.lower() in content:
            try:
                await message.delete()
            except Exception:
                pass
            await message.channel.send(f"⚠️ {author.mention} Watch your language!", delete_after=5)
            await send_log(guild, "🤬 Bad Word Detected",
                           f"**User:** {author.mention}\n**Word:** ||{word}||\n**Channel:** {message.channel.mention}",
                           color=0xE74C3C)
            return

    # ── Anti-Spam ──
    sec_cfg = cfg_doc("security_config") or {}
    if sec_cfg.get("anti_spam", True):
        spam_limit  = sec_cfg.get("spam_limit", SPAM_LIMIT)
        spam_window = sec_cfg.get("spam_window", SPAM_WINDOW)
        now = datetime.now(timezone.utc).timestamp()
        tracker = spam_tracker[author.id]
        tracker.append(now)
        spam_tracker[author.id] = [t for t in tracker if now - t < spam_window]
        if len(spam_tracker[author.id]) >= spam_limit:
            spam_tracker[author.id] = []
            try:
                await author.timeout(discord.utils.utcnow() + timedelta(minutes=10), reason="Spam detected")
            except Exception:
                pass
            await message.channel.send(f"⚠️ {author.mention} has been timed out for spamming!", delete_after=5)
            await send_log(guild, "🔇 Anti-Spam Triggered",
                           f"**User:** {author.mention}\n**Channel:** {message.channel.mention}",
                           color=0xE74C3C)
            return

    # ── Anti-Links ──
    if sec_cfg.get("anti_links", True):
        if message.channel.id != setting_int("links_allowed_channel", LINKS_ALLOWED_CHANNEL):
            url_pattern = re.compile(r"https?://|discord\.gg/|\.com|\.net|\.org|\.gg", re.IGNORECASE)
            if url_pattern.search(message.content):
                try:
                    await message.delete()
                except Exception:
                    pass
                await message.channel.send(f"🔗 {author.mention} Links are not allowed here!", delete_after=5)
                await send_log(guild, "🔗 Link Blocked",
                               f"**User:** {author.mention}\n**Channel:** {message.channel.mention}",
                               color=0xE67E22)
                return

    # ── Anti-Mention Spam ──
    mention_limit = sec_cfg.get("mention_limit", 5)
    if sec_cfg.get("anti_mention", True) and len(message.mentions) >= mention_limit:
        try:
            await message.delete()
        except Exception:
            pass
        await message.channel.send(f"⚠️ {author.mention} Too many mentions!", delete_after=5)
        await send_log(guild, "📢 Mention Spam Blocked",
                       f"**User:** {author.mention}\n**Mentions:** {len(message.mentions)}",
                       color=0xE74C3C)
        return


@bot.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    if before.author.bot:
        return
    if before.content == after.content:
        return
    await send_log(before.guild, "✏️ Message Edited",
                   f"**User:** {before.author.mention}\n**Channel:** {before.channel.mention}",
                   color=0x3498DB,
                   fields=[
                       ("Before", before.content[:512] or "(empty)", False),
                       ("After", after.content[:512] or "(empty)", False),
                   ])


@bot.event
async def on_message_delete(message: discord.Message):
    if message.author.bot:
        return
    await send_log(message.guild, "🗑️ Message Deleted",
                   f"**User:** {message.author.mention}\n**Channel:** {message.channel.mention}\n**Content:** {message.content[:512] or '(empty)'}",
                   color=0xE74C3C)


@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    if member.bot:
        return
    guild = member.guild
    if before.channel is None and after.channel is not None:
        await send_log(guild, "🔊 Member Joined Voice",
                       f"**User:** {member.mention}\n**Channel:** {after.channel.name}",
                       color=0x2ECC71)
    elif before.channel is not None and after.channel is None:
        await send_log(guild, "🔇 Member Left Voice",
                       f"**User:** {member.mention}\n**Channel:** {before.channel.name}",
                       color=0xE74C3C)
    elif before.channel != after.channel:
        await send_log(guild, "🔀 Member Switched Voice",
                       f"**User:** {member.mention}\n**From:** {before.channel.name} → **To:** {after.channel.name}",
                       color=0x3498DB)

# ═══════════════════════════════════════════════════════════════
#  ██  SLASH COMMANDS
# ═══════════════════════════════════════════════════════════════

# ── Setup Commands ──
@bot.slash_command(guild_ids=[GUILD_ID], name="setup_tickets", description="Send the ticket panel")
@has_security_role()
async def setup_tickets(ctx):
    channel = ctx.guild.get_channel(setting_int("ticket_channel", TICKET_CHANNEL_ID))
    if not channel:
        await ctx.respond("❌ Ticket channel not found.", ephemeral=True)
        return
    cfg = cfg_doc("ticket_config")
    embed = discord.Embed(
        title=cfg.get("title", "🎫 MEM Store | Ticket Center"),
        description=cfg.get("description",
            "Open a ticket to buy, sell, or partner with us.\n\n"
            "💰 **Sell** — List your items\n"
            "🛒 **Buy** — Purchase items\n"
            "🤝 **Partner** — Business inquiries"
        ),
        color=current_embed_color(),
    )
    if LOGO_URL:
        embed.set_thumbnail(url=LOGO_URL)
    if GIF_URL:
        embed.set_image(url=GIF_URL)
    embed.set_footer(text=cfg.get("footer") or current_footer())
    await channel.send(embed=embed, view=TicketView())
    await ctx.respond("✅ Ticket panel sent!", ephemeral=True)


@bot.slash_command(guild_ids=[GUILD_ID], name="setup_roles", description="Send the self-roles panel")
@has_security_role()
async def setup_roles(ctx):
    channel = ctx.guild.get_channel(setting_int("self_roles_channel", SELF_ROLES_CHANNEL_ID))
    if not channel:
        await ctx.respond("❌ Self roles channel not found.", ephemeral=True)
        return
    lang_embed = discord.Embed(
        title="🌍 Language Roles",
        description="Choose your preferred language:",
        color=EMBED_COLOR,
    )
    lang_embed.set_footer(text=current_footer())
    await channel.send(embed=lang_embed, view=LanguageRoleView())
    game_embed = discord.Embed(
        title="🎮 Game Roles",
        description="Choose the games you play:",
        color=EMBED_COLOR,
    )
    game_embed.set_footer(text=current_footer())
    await channel.send(embed=game_embed, view=GameRoleView())
    await ctx.respond("✅ Self roles panel sent!", ephemeral=True)


# ── Moderation Commands ──
@bot.slash_command(guild_ids=[GUILD_ID], name="warn", description="Warn a member")
@has_security_role()
async def warn(ctx,
               member: Option(discord.Member, "Member to warn"),
               reason: Option(str, "Reason", default="No reason provided")):
    db["warnings"].insert_one({
        "guild_id":  ctx.guild.id,
        "user_id":   member.id,
        "username":  str(member),
        "by":        ctx.author.id,
        "reason":    reason,
        "timestamp": datetime.now(timezone.utc),
    })
    warns = db["warnings"].count_documents({"guild_id": ctx.guild.id, "user_id": member.id})
    embed = discord.Embed(
        title="⚠️ Warning Issued",
        description=f"**User:** {member.mention}\n**Reason:** {reason}\n**Total Warnings:** {warns}",
        color=0xF1C40F,
    )
    embed.set_footer(text=current_footer())
    await ctx.respond(embed=embed)
    await send_log(ctx.guild, "⚠️ Member Warned",
                   f"**User:** {member.mention}\n**By:** {ctx.author.mention}\n**Reason:** {reason}\n**Total:** {warns}",
                   color=0xF1C40F)
    try:
        await member.send(f"⚠️ You were warned in **{ctx.guild.name}**\nReason: {reason}")
    except Exception:
        pass


@bot.slash_command(guild_ids=[GUILD_ID], name="ban", description="Ban a member")
@has_security_role()
async def ban(ctx,
              member: Option(discord.Member, "Member to ban"),
              reason: Option(str, "Reason", default="No reason provided")):
    try:
        await member.send(f"🔨 You were banned from **{ctx.guild.name}**\nReason: {reason}")
    except Exception:
        pass
    try:
        await member.ban(reason=reason)
    except discord.Forbidden:
        await ctx.respond("❌ I do not have permission to ban this member.", ephemeral=True)
        return
    except Exception as exc:
        await ctx.respond(f"❌ Ban failed: {exc}", ephemeral=True)
        return
    await ctx.respond(f"✅ **{member.name}** has been banned.")
    await send_log(ctx.guild, "🔨 Member Banned",
                   f"**User:** {member.mention}\n**By:** {ctx.author.mention}\n**Reason:** {reason}",
                   color=0xE74C3C)


@bot.slash_command(guild_ids=[GUILD_ID], name="kick", description="Kick a member")
@has_security_role()
async def kick(ctx,
               member: Option(discord.Member, "Member to kick"),
               reason: Option(str, "Reason", default="No reason provided")):
    try:
        await member.send(f"👢 You were kicked from **{ctx.guild.name}**\nReason: {reason}")
    except Exception:
        pass
    try:
        await member.kick(reason=reason)
    except discord.Forbidden:
        await ctx.respond("❌ I do not have permission to kick this member.", ephemeral=True)
        return
    except Exception as exc:
        await ctx.respond(f"❌ Kick failed: {exc}", ephemeral=True)
        return
    await ctx.respond(f"✅ **{member.name}** has been kicked.")
    await send_log(ctx.guild, "👢 Member Kicked",
                   f"**User:** {member.mention}\n**By:** {ctx.author.mention}\n**Reason:** {reason}",
                   color=0xE67E22)


@bot.slash_command(guild_ids=[GUILD_ID], name="timeout", description="Timeout a member")
@has_security_role()
async def timeout_cmd(ctx,
                      member: Option(discord.Member, "Member to timeout"),
                      minutes: Option(int, "Duration in minutes", default=10),
                      reason: Option(str, "Reason", default="No reason provided")):
    minutes = max(1, min(int(minutes), 40320))
    until = discord.utils.utcnow() + timedelta(minutes=minutes)
    try:
        await member.timeout(until, reason=reason)
    except discord.Forbidden:
        await ctx.respond("❌ I do not have permission to timeout this member.", ephemeral=True)
        return
    except Exception as exc:
        await ctx.respond(f"❌ Timeout failed: {exc}", ephemeral=True)
        return
    await ctx.respond(f"✅ **{member.name}** timed out for {minutes} minutes.")
    await send_log(ctx.guild, "⏰ Member Timed Out",
                   f"**User:** {member.mention}\n**By:** {ctx.author.mention}\n**Duration:** {minutes}m\n**Reason:** {reason}",
                   color=0xF39C12)

@bot.slash_command(guild_ids=[GUILD_ID], name="unwarn", description="Remove warnings from a member")
@has_security_role()
async def unwarn(ctx,
                 member: Option(discord.Member, "Member to clear warnings for")):
    result = db["warnings"].delete_many({"guild_id": ctx.guild.id, "user_id": member.id})
    await ctx.respond(f"✅ Cleared **{result.deleted_count}** warning(s) for {member.mention}.")
    await send_log(ctx.guild, "✅ Warnings Cleared",
                   f"**User:** {member.mention}\n**By:** {ctx.author.mention}\n**Count:** {result.deleted_count}",
                   color=0x2ECC71)


@bot.slash_command(guild_ids=[GUILD_ID], name="warnings", description="Check warnings for a member")
async def check_warnings(ctx,
                         member: Option(discord.Member, "Member to check")):
    warns = list(db["warnings"].find({"guild_id": ctx.guild.id, "user_id": member.id}))
    if not warns:
        await ctx.respond(f"✅ {member.mention} has no warnings.", ephemeral=True)
        return
    desc = "\n".join([f"• {w.get('reason', 'No reason')} — <t:{int(w['timestamp'].timestamp())}:R>" for w in warns[:10]])
    embed = discord.Embed(
        title=f"⚠️ Warnings for {member.name}",
        description=desc,
        color=0xF1C40F,
    )
    embed.set_footer(text=f"Total: {len(warns)} warning(s)")
    await ctx.respond(embed=embed, ephemeral=True)


@bot.slash_command(guild_ids=[GUILD_ID], name="blacklist", description="Blacklist a user")
@has_security_role()
async def blacklist(ctx,
                    member: Option(discord.Member, "Member to blacklist"),
                    reason: Option(str, "Reason", default="No reason provided")):
    db["blacklist"].update_one(
        {"user_id": member.id},
        {"$set": {"user_id": member.id, "username": str(member), "reason": reason, "added_at": datetime.now(timezone.utc), "by": ctx.author.id}},
        upsert=True,
    )
    await ctx.respond(f"🚫 **{member.name}** has been blacklisted.")
    await send_log(ctx.guild, "🚫 User Blacklisted",
                   f"**User:** {member.mention}\n**By:** {ctx.author.mention}\n**Reason:** {reason}",
                   color=0xE74C3C)


# ── Feedback Command ──
@bot.slash_command(guild_ids=[GUILD_ID], name="feedback", description="Submit feedback about a seller")
async def feedback(ctx,
                   seller: Option(discord.Member, "Seller to rate"),
                   message: Option(str, "Your feedback message")):
    channel = ctx.guild.get_channel(setting_int("feedback_channel", FEEDBACK_CHANNEL_ID))
    embed = discord.Embed(
        title="💬 New Feedback",
        description=f"**Seller:** {seller.mention}\n**By:** {ctx.author.mention}\n\n{message}",
        color=current_embed_color(),
        timestamp=datetime.now(timezone.utc),
    )
    embed.set_footer(text=current_footer())
    if channel:
        await channel.send(embed=embed)
    await ctx.respond("✅ Feedback submitted!", ephemeral=True)
    await send_log(ctx.guild, "💬 Feedback Submitted",
                   f"**Seller:** {seller.mention}\n**By:** {ctx.author.mention}\n**Message:** {message[:200]}",
                   color=0x3498DB)


# ── Order Command ──
@bot.slash_command(guild_ids=[GUILD_ID], name="order", description="Log a completed order")
@has_security_role()
async def order(ctx,
                buyer:  Option(discord.Member, "Buyer"),
                item:   Option(str, "Item/description"),
                amount: Option(str, "Amount/price")):
    if not system_enabled("orders", True):
        await ctx.respond("❌ Orders system is currently disabled.", ephemeral=True)
        return
    channel = ctx.guild.get_channel(setting_int("order_channel", ORDER_CHANNEL_ID))
    embed = discord.Embed(
        title="📦 Order Completed",
        description=(
            f"**Buyer:** {buyer.mention}\n"
            f"**Seller:** {ctx.author.mention}\n"
            f"**Item:** {item}\n"
            f"**Amount:** {amount}"
        ),
        color=0x2ECC71,
        timestamp=datetime.now(timezone.utc),
    )
    embed.set_footer(text=current_footer())
    if channel:
        await channel.send(embed=embed)
    await ctx.respond("✅ Order logged!", ephemeral=True)
    await send_log(ctx.guild, "📦 Order Logged",
                   f"**Buyer:** {buyer.mention}\n**Seller:** {ctx.author.mention}\n**Item:** {item}\n**Amount:** {amount}",
                   color=0x2ECC71)


# ═══════════════════════════════════════════════════════════════
#  ██  VOICE RELAY COMMANDS (ENHANCED)
# ═══════════════════════════════════════════════════════════════

@bot.slash_command(guild_ids=[GUILD_ID], name="join", description="Make the bot join a voice channel")
@has_security_role()
async def join_voice(ctx,
                     channel: Option(discord.VoiceChannel, "Select the voice channel to join", required=True)):
    guild = ctx.guild
    # Disconnect from existing session if any
    if guild.voice_client and guild.voice_client.is_connected():
        old_channel = guild.voice_client.channel.name
        # Save call history
        sess = voice_session.get(guild.id, {})
        if sess.get("start"):
            start_dt = datetime.fromisoformat(sess["start"])
            end_dt   = datetime.now(timezone.utc)
            duration_secs = int((end_dt - start_dt).total_seconds())
            db["voice_calls"].insert_one({
                "guild_id":    guild.id,
                "channel":     old_channel,
                "channel_id":  sess.get("channel_id"),
                "started_by":  sess.get("started_by"),
                "start":       start_dt,
                "end":         end_dt,
                "duration":    duration_secs,
            })
        await guild.voice_client.disconnect()
    try:
        vc = await channel.connect()
    except Exception as e:
        await ctx.respond(f"❌ Failed to join channel: {e}", ephemeral=True)
        return
    source = MicAudioSource()
    vc.play(source, after=lambda e: None)
    start_time = datetime.now(timezone.utc).isoformat()
    voice_session[guild.id] = {
        "channel":    channel.name,
        "channel_id": channel.id,
        "start":      start_time,
        "started_by": ctx.author.id,
        "started_by_name": ctx.author.name,
    }
    await _ws_broadcast({
        "type":       "joined",
        "channel":    channel.name,
        "channel_id": channel.id,
        "start":      start_time,
        "started_by": ctx.author.name,
        "members":    [m.name for m in channel.members if not m.bot],
    })
    embed = discord.Embed(
        title="🎙️ Voice Relay Active",
        description=(
            f"**Channel:** {channel.mention}\n"
            f"**Started by:** {ctx.author.mention}\n\n"
            "The bot is now in the voice channel.\n"
            "Use `/leave` to disconnect.\n"
            "Use the **Dashboard → Voice Relay** to speak."
        ),
        color=0x2ECC71,
        timestamp=datetime.now(timezone.utc),
    )
    embed.set_footer(text=current_footer())
    await ctx.respond(embed=embed)
    await send_log(guild, "🎙️ Voice Relay Started",
                   f"**Channel:** {channel.name}\n**By:** {ctx.author.mention}",
                   color=0x2ECC71)


@bot.slash_command(guild_ids=[GUILD_ID], name="leave", description="Disconnect the bot from voice")
@has_security_role()
async def leave_voice(ctx):
    guild = ctx.guild
    if not guild.voice_client or not guild.voice_client.is_connected():
        await ctx.respond("❌ Not in a voice channel.", ephemeral=True)
        return
    channel_name = guild.voice_client.channel.name
    sess = voice_session.get(guild.id, {})
    if sess.get("start"):
        start_dt = datetime.fromisoformat(sess["start"])
        end_dt   = datetime.now(timezone.utc)
        duration_secs = int((end_dt - start_dt).total_seconds())
        db["voice_calls"].insert_one({
            "guild_id":    guild.id,
            "channel":     channel_name,
            "channel_id":  sess.get("channel_id"),
            "started_by":  sess.get("started_by"),
            "started_by_name": sess.get("started_by_name", "Unknown"),
            "start":       start_dt,
            "end":         end_dt,
            "duration":    duration_secs,
        })
    await guild.voice_client.disconnect()
    voice_session.pop(guild.id, None)
    await _ws_broadcast({"type": "left", "channel": channel_name})
    await ctx.respond(f"✅ Disconnected from **{channel_name}**.")
    await send_log(guild, "🔇 Voice Relay Ended",
                   f"**Channel:** {channel_name}\n**By:** {ctx.author.mention}",
                   color=0xE74C3C)


@bot.slash_command(guild_ids=[GUILD_ID], name="voice_status", description="Check voice relay status")
async def voice_status(ctx):
    guild = ctx.guild
    if not guild.voice_client or not guild.voice_client.is_connected():
        await ctx.respond("🔇 Bot is not in any voice channel.", ephemeral=True)
        return
    sess    = voice_session.get(guild.id, {})
    channel = guild.voice_client.channel
    members = [m.mention for m in channel.members if not m.bot]
    start_ts = datetime.fromisoformat(sess["start"]).timestamp() if sess.get("start") else 0
    embed = discord.Embed(
        title="🎙️ Voice Relay Status",
        description=(
            f"**Channel:** {channel.mention}\n"
            f"**Started:** <t:{int(start_ts)}:R>\n"
            f"**Members:** {', '.join(members) or 'None'}"
        ),
        color=0x2ECC71,
    )
    embed.set_footer(text=current_footer())
    await ctx.respond(embed=embed, ephemeral=True)


# ── Embed Command ──
@bot.slash_command(guild_ids=[GUILD_ID], name="embed", description="Send a custom embed to a channel")
@has_security_role()
async def send_embed(ctx,
                     channel: Option(discord.TextChannel, "Target channel"),
                     title:   Option(str, "Embed title", default=""),
                     description: Option(str, "Embed description", default=""),
                     color:   Option(str, "Hex color (e.g. #1a2332)", default="#1a2332")):
    try:
        color_int = int(color.strip("#"), 16)
    except Exception:
        color_int = EMBED_COLOR
    embed = discord.Embed(title=title, description=description, color=color_int, timestamp=datetime.now(timezone.utc))
    embed.set_footer(text=current_footer())
    await channel.send(embed=embed)
    await ctx.respond(f"✅ Embed sent to {channel.mention}", ephemeral=True)


# ═══════════════════════════════════════════════════════════════
#  ██  WEBSOCKET SERVER
# ═══════════════════════════════════════════════════════════════

async def start_ws_server():
    print(f"🔌 WebSocket server starting on port {WS_PORT}")
    async with websockets.serve(ws_handler, "0.0.0.0", WS_PORT):
        await asyncio.Future()


# ═══════════════════════════════════════════════════════════════
#  ██  RUN
# ═══════════════════════════════════════════════════════════════

bot.run(DISCORD_TOKEN)
```

## `templates/logs.html`
```html
{% extends "base.html" %}
{% block title %}Logs{% endblock %}
{% block page_title %}Logs{% endblock %}
{% block page_subtitle %}Server Activity Logs{% endblock %}
{% block content %}
<div class="stats-grid">
  <div class="stat-card"><div class="stat-icon">⚠️</div><div class="stat-value">{{ stats.total }}</div><div class="stat-label">Warnings</div></div>
  <div class="stat-card"><div class="stat-icon">🔨</div><div class="stat-value">{{ stats.bans }}</div><div class="stat-label">Bans</div></div>
  <div class="stat-card"><div class="stat-icon">👢</div><div class="stat-value">{{ stats.kicks }}</div><div class="stat-label">Kicks</div></div>
  <div class="stat-card"><div class="stat-icon">⏰</div><div class="stat-value">{{ stats.timeouts }}</div><div class="stat-label">Timeouts</div></div>
</div>

<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;flex-wrap:wrap;gap:12px">
  <div style="display:flex;gap:8px;flex-wrap:wrap">
    {% for t in log_types %}
    <a href="/logs?type={{ t }}" class="btn {% if current_type == t %}btn-gold{% else %}btn-blue{% endif %}" style="font-size:11px;padding:6px 14px;letter-spacing:1px">
      {% if t == 'all' %}📋{% elif t == 'moderation' %}🛡️{% elif t == 'ticket' %}🎫{% elif t == 'member' %}👤{% elif t == 'message' %}✉️{% elif t == 'order' %}📦{% elif t == 'automod' %}🤖{% elif t == 'voice' %}🎙️{% else %}📁{% endif %}
      {{ t }}
    </a>
    {% endfor %}
  </div>
  <form method="POST" action="/clear_logs" onsubmit="return confirm('Delete all logs?')">
    <button class="btn btn-danger" type="submit" style="padding:6px 16px">🗑️ Clear All</button>
  </form>
</div>

<div class="section">
  <div class="section-header"><div class="section-title">📜 Activity</div></div>
  <div class="table-wrap">
    <div class="table-row header" style="grid-template-columns:90px 1.2fr 2fr 110px">
      <div>Type</div><div>Event</div><div>Details</div><div>Time</div>
    </div>
    {% if logs %}
      {% for l in logs %}
      <div class="table-row" style="grid-template-columns:90px 1.2fr 2fr 110px">
        <div>
          <span class="badge badge-{{ l.type }}">
            {% if l.type == 'moderation' %}🛡️{% elif l.type == 'ticket' %}🎫{% elif l.type == 'member' %}👤{% elif l.type == 'message' %}✉️{% elif l.type == 'order' %}📦{% elif l.type == 'automod' %}🤖{% elif l.type == 'voice' %}🎙️{% else %}📁{% endif %}
            {{ l.type }}
          </span>
        </div>
        <div style="font-size:13px;font-weight:600;color:var(--text)">{{ l.title }}</div>
        <div style="font-size:11px;color:var(--text-dim);line-height:1.5">{{ l.description[:120] }}{% if l.description|length > 120 %}...{% endif %}</div>
        <div style="font-size:10px;color:var(--text-dim)">{{ l.time }}</div>
      </div>
      {% endfor %}
    {% else %}
      <div class="empty-state" style="padding:40px">📭 NO LOGS{% if current_type != 'all' %} — Type: <strong>{{ current_type }}</strong>{% endif %}</div>
    {% endif %}
  </div>
  {% if logs %}
  <div style="margin-top:12px;font-size:11px;letter-spacing:1px;color:var(--text-dim);text-align:right">
    Showing <span style="color:var(--gold)">{{ logs|length }}</span> entries{% if current_type != 'all' %} — filtered by <span style="color:var(--gold)">{{ current_type }}</span>{% endif %}
  </div>
  {% endif %}
</div>
{% endblock %}
```

## `templates/voice.html`
```html
{% extends "base.html" %}
{% block title %}Voice Relay{% endblock %}
{% block page_title %}Voice Relay{% endblock %}
{% block page_subtitle %}Push-to-Talk via Browser{% endblock %}
{% block extra_style %}
<style>
.voice-layout{display:grid;grid-template-columns:340px 1fr;gap:20px;align-items:start;}
.ptt-card{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:28px;text-align:center;}
.ws-bar{display:flex;align-items:center;justify-content:center;gap:8px;font-size:11px;letter-spacing:2px;text-transform:uppercase;margin-bottom:16px;color:var(--text-dim);}
.ws-dot{width:8px;height:8px;border-radius:50%;display:inline-block;flex-shrink:0;}
.ws-dot.online{background:#22c55e;box-shadow:0 0 6px #22c55e88;animation:dpulse 2s infinite;}
.ws-dot.offline{background:var(--red);}
.ws-dot.connecting{background:var(--gold);animation:dpulse 1s infinite;}
@keyframes dpulse{0%,100%{opacity:1}50%{opacity:.3}}
.ch-badge{background:rgba(201,168,76,0.08);border:1px solid var(--gold-dim);border-radius:8px;padding:10px 16px;font-family:'Cinzel',serif;font-size:12px;color:var(--gold);letter-spacing:2px;margin-bottom:18px;min-height:40px;display:flex;align-items:center;justify-content:center;text-align:center;}
.ptt-wrap{position:relative;display:inline-flex;align-items:center;justify-content:center;margin:6px 0 12px;}
.ptt-ring{position:absolute;inset:-10px;border-radius:50%;border:2px solid transparent;transition:all .3s;pointer-events:none;}
.ptt-ring.active{border-color:var(--red);box-shadow:0 0 24px rgba(231,76,60,.4);animation:pring 1s infinite;}
@keyframes pring{0%,100%{transform:scale(1)}50%{transform:scale(1.05)}}
#ptt{width:130px;height:130px;border-radius:50%;border:3px solid var(--gold-dim);background:rgba(201,168,76,.07);color:var(--gold);font-family:'Cinzel',serif;font-size:10px;letter-spacing:2px;cursor:pointer;transition:all .15s;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:7px;outline:none;user-select:none;}
#ptt:hover:not(.off){border-color:var(--gold);background:rgba(201,168,76,.14);}
#ptt.on{background:rgba(231,76,60,.15);border-color:var(--red);color:var(--red);}
#ptt.off{opacity:.4;cursor:not-allowed;border-color:var(--text-dim);color:var(--text-dim);}
#ptt svg{width:38px;height:38px;}
.kb-hint{font-size:10px;letter-spacing:2px;color:var(--text-dim);text-transform:uppercase;margin-bottom:10px;}
.err{background:rgba(231,76,60,.1);border:1px solid rgba(231,76,60,.3);color:var(--red);border-radius:8px;padding:8px 12px;font-size:12px;margin-top:10px;display:none;}
.vstat-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:18px;}
.vstat-box{background:var(--surface2);border-radius:10px;padding:14px;text-align:center;}
.vstat-val{font-family:'Cinzel',serif;font-size:22px;color:var(--gold);}
.vstat-lbl{font-size:10px;letter-spacing:2px;color:var(--text-dim);text-transform:uppercase;margin-top:3px;}
.live-pill{display:none;background:rgba(239,68,68,.12);border:1px solid rgba(239,68,68,.3);color:var(--red);font-size:10px;letter-spacing:2px;padding:3px 10px;border-radius:99px;margin-left:8px;}
.info-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:20px;}
.info-card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:18px;}
.info-label{font-size:10px;letter-spacing:2px;color:var(--text-dim);text-transform:uppercase;margin-bottom:6px;}
.info-value{font-family:'Cinzel',serif;font-size:18px;color:var(--gold);}
.members-list{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px;}
.member-chip{background:rgba(201,168,76,0.08);border:1px solid var(--gold-dim);border-radius:99px;padding:3px 10px;font-size:11px;color:var(--text);}
</style>
{% endblock %}
{% block content %}
<div class="voice-layout">

  <!-- LEFT: PTT Card -->
  <div class="ptt-card">
    <div class="ws-bar">
      <span class="ws-dot connecting" id="wsd"></span>
      <span id="wsl">Connecting...</span>
      <span id="bname" style="display:none;color:var(--gold);margin-left:6px;font-size:11px"></span>
    </div>
    <div class="ch-badge">
      <span id="chtext" style="color:var(--text-dim)">Run /join in Discord first</span>
    </div>
    <div style="margin-bottom:10px;display:none" id="members-wrap">
      <div class="members-list" id="members-list"></div>
    </div>
    <div class="ptt-wrap">
      <div class="ptt-ring" id="pttr"></div>
      <button id="ptt" class="off"
        onmousedown="startT()" onmouseup="stopT()" onmouseleave="stopT()"
        ontouchstart="event.preventDefault();startT()"
        ontouchend="event.preventDefault();stopT()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 1a3 3 0 0 1 3 3v8a3 3 0 0 1-6 0V4a3 3 0 0 1 3-3z"/>
          <path d="M19 10v2a7 7 0 0 1-14 0v-2M12 19v4M8 23h8"/>
        </svg>
        <span id="pttlbl">PUSH TO TALK</span>
      </button>
    </div>
    <p class="kb-hint">Hold Spacebar or click</p>
    <div class="err" id="errd"></div>
    <div class="vstat-grid">
      <div class="vstat-box"><div class="vstat-val">{{ total_calls }}</div><div class="vstat-lbl">Total Calls</div></div>
      <div class="vstat-box"><div class="vstat-val">{{ total_duration }}</div><div class="vstat-lbl">Total Time</div></div>
    </div>
  </div>

  <!-- RIGHT: Info & History -->
  <div>
    <!-- Live Info -->
    <div class="section">
      <div class="section-header">
        <div class="section-title">📡 Live Connection Info</div>
        <span class="live-pill" id="livepill">● LIVE</span>
      </div>
      <div class="info-grid">
        <div class="info-card">
          <div class="info-label">Bot Status</div>
          <div class="info-value" id="bot-status-val" style="color:var(--text-dim)">Offline</div>
        </div>
        <div class="info-card">
          <div class="info-label">Voice Channel</div>
          <div class="info-value" id="vc-name" style="font-size:14px;color:var(--text-dim)">Not Connected</div>
        </div>
        <div class="info-card">
          <div class="info-label">Session Started</div>
          <div class="info-value" id="session-start" style="font-size:14px;color:var(--text-dim)">—</div>
        </div>
        <div class="info-card">
          <div class="info-label">WebSocket</div>
          <div class="info-value" id="ws-status-val" style="font-size:14px;color:var(--text-dim)">Disconnected</div>
        </div>
      </div>
    </div>

    <!-- Call History -->
    <div class="section">
      <div class="section-header"><div class="section-title">📞 Call History</div></div>
      <div class="table-wrap">
        <div class="table-row header" style="grid-template-columns:1.2fr 1fr 1fr 1fr 80px">
          <div>Channel</div><div>Started By</div><div>Start</div><div>End</div><div>Duration</div>
        </div>
        {% if calls %}
          {% for c in calls %}
          <div class="table-row" style="grid-template-columns:1.2fr 1fr 1fr 1fr 80px">
            <div style="color:var(--gold)">🔊 {{ c.channel }}</div>
            <div style="font-size:12px;color:var(--text-dim)">{{ c.started_by }}</div>
            <div style="font-size:11px;color:var(--text-dim)">{{ c.start }}</div>
            <div style="font-size:11px;color:var(--text-dim)">{{ c.end }}</div>
            <div style="font-size:12px;color:var(--green)">{{ c.duration }}</div>
          </div>
          {% endfor %}
        {% else %}
          <div class="empty-state">NO CALLS YET — Use /join in Discord to start</div>
        {% endif %}
      </div>
    </div>
  </div>
</div>

<script>
const WS_URL = {{ ws_url | tojson }};
let ws, stream, ctx, wnode, snode, talking = false;
let workletLoaded = false;

function setWS(state, label) {
  document.getElementById('wsd').className = 'ws-dot ' + state;
  document.getElementById('wsl').textContent = label;
  document.getElementById('ws-status-val').textContent = state === 'online' ? 'Connected' : state === 'connecting' ? 'Connecting...' : 'Disconnected';
  document.getElementById('ws-status-val').style.color = state === 'online' ? 'var(--green)' : state === 'connecting' ? 'var(--gold)' : 'var(--red)';
  document.getElementById('ptt').className = state === 'online' ? '' : 'off';
}

function showErr(m) {
  const e = document.getElementById('errd');
  e.textContent = m; e.style.display = m ? '' : 'none';
}

function setJoined(channel, start, members) {
  document.getElementById('chtext').textContent = '🔊 ' + channel;
  document.getElementById('chtext').style.color = '';
  document.getElementById('vc-name').textContent = channel;
  document.getElementById('vc-name').style.color = 'var(--gold)';
  document.getElementById('livepill').style.display = '';
  if (start) {
    try {
      const d = new Date(start);
      document.getElementById('session-start').textContent = d.toLocaleTimeString();
      document.getElementById('session-start').style.color = 'var(--text)';
    } catch(_) {}
  }
  if (members && members.length > 0) {
    const wrap = document.getElementById('members-wrap');
    const list = document.getElementById('members-list');
    list.innerHTML = members.map(m => `<span class="member-chip">👤 ${m}</span>`).join('');
    wrap.style.display = '';
  }
}

function setLeft() {
  document.getElementById('chtext').textContent = 'Run /join in Discord first';
  document.getElementById('chtext').style.color = 'var(--text-dim)';
  document.getElementById('vc-name').textContent = 'Not Connected';
  document.getElementById('vc-name').style.color = 'var(--text-dim)';
  document.getElementById('livepill').style.display = 'none';
  document.getElementById('session-start').textContent = '—';
  document.getElementById('session-start').style.color = 'var(--text-dim)';
  document.getElementById('members-wrap').style.display = 'none';
  if (talking) stopT();
}

function connect() {
  setWS('connecting', 'Connecting...');
  ws = new WebSocket(WS_URL);
  ws.binaryType = 'arraybuffer';
  ws.onopen = () => setWS('online', 'Online');
  ws.onmessage = (e) => {
    try {
      const m = JSON.parse(e.data);
      if (m.type === 'bot_ready') {
        document.getElementById('bname').textContent = m.user;
        document.getElementById('bname').style.display = '';
        document.getElementById('bot-status-val').textContent = m.user;
        document.getElementById('bot-status-val').style.color = 'var(--green)';
      } else if (m.type === 'joined') {
        setJoined(m.channel, m.start, m.members || []);
      } else if (m.type === 'left') {
        setLeft();
        setTimeout(() => location.reload(), 2000);
      }
    } catch(_) {}
  };
  ws.onclose = () => { setWS('offline', 'Offline'); setTimeout(connect, 3000); };
  ws.onerror = () => ws.close();
}

async function startT() {
  if (!ws || ws.readyState !== WebSocket.OPEN) return;
  talking = true;
  document.getElementById('ptt').className = 'on';
  document.getElementById('pttlbl').textContent = 'TALKING';
  document.getElementById('pttr').classList.add('active');
  showErr('');
  try {
    if (!stream) stream = await navigator.mediaDevices.getUserMedia({
      audio: { echoCancellation: true, noiseSuppression: true, sampleRate: 48000 }
    });
    if (!ctx) ctx = new AudioContext({ sampleRate: 48000 });
    await ctx.resume();
    if (!snode) snode = ctx.createMediaStreamSource(stream);
    if (!workletLoaded) {
      await ctx.audioWorklet.addModule('/static/audio-processor.js');
      workletLoaded = true;
    }
    wnode = new AudioWorkletNode(ctx, 'mic-processor');
    wnode.port.onmessage = (e) => {
      if (ws && ws.readyState === WebSocket.OPEN) ws.send(e.data);
    };
    snode.connect(wnode);
    wnode.connect(ctx.destination);
  } catch(err) { showErr('Mic error: ' + err.message); stopT(); }
}

function stopT() {
  if (!talking) return;
  talking = false;
  const state = ws?.readyState === WebSocket.OPEN;
  document.getElementById('ptt').className = state ? '' : 'off';
  document.getElementById('pttlbl').textContent = 'PUSH TO TALK';
  document.getElementById('pttr').classList.remove('active');
  try { wnode?.disconnect(); } catch(_) {}
  try { snode?.disconnect(); } catch(_) {}
  wnode = null;
}

document.addEventListener('keydown', e => {
  if (e.code === 'Space' && !e.repeat && !['INPUT','TEXTAREA'].includes(e.target.tagName)) {
    e.preventDefault(); startT();
  }
});
document.addEventListener('keyup', e => {
  if (e.code === 'Space') { e.preventDefault(); stopT(); }
});

connect();
</script>
{% endblock %}
```

## `static/audio-processor.js`
```javascript
class MicProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.buffer = [];
    this.frameSamples = 960; // 20ms at 48kHz mono before stereo expansion
  }

  process(inputs) {
    const input = inputs[0];
    if (!input || input.length === 0 || !input[0] || input[0].length === 0) {
      return true;
    }

    const mono = input[0];
    for (let i = 0; i < mono.length; i++) {
      this.buffer.push(mono[i]);
    }

    while (this.buffer.length >= this.frameSamples) {
      const pcm = new Int16Array(this.frameSamples * 2); // stereo interleaved
      for (let i = 0; i < this.frameSamples; i++) {
        const sample = Math.max(-1, Math.min(1, this.buffer[i]));
        const intSample = sample < 0 ? sample * 0x8000 : sample * 0x7FFF;
        pcm[i * 2] = intSample;
        pcm[i * 2 + 1] = intSample;
      }
      this.buffer = this.buffer.slice(this.frameSamples);
      this.port.postMessage(pcm.buffer, [pcm.buffer]);
    }
    return true;
  }
}

registerProcessor('mic-processor', MicProcessor);
```
