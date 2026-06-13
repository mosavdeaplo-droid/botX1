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


def int_env(name: str, default: int) -> int:
    """Read Discord snowflake-like variables safely.

    Railway may import placeholders from .env.example. Values like
    'your_role_id_here' must not crash the dashboard before /healthz can respond.
    """
    value = os.getenv(name, "").strip()
    if not value:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        print(f"[dashboard] ignoring invalid integer env {name}={value!r}; using default {default}", flush=True)
        return default


DEFAULT_LANGUAGE_ROLES = {
    "English": int_env("ROLE_ENGLISH", 1506219132037763092),
    "Arabic": int_env("ROLE_ARABIC", 1506219366939885669),
}
DEFAULT_GAME_ROLES = {
    "ARC Raiders": int_env("ROLE_ARC", 1506219518567911566),
    "PUBG Mobile": int_env("ROLE_PUBG_MOB", 1506219627246649455),
    "PUBG Steam": int_env("ROLE_PUBG_STEAM", 1506219763171463209),
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
