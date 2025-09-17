# from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
# from datetime import datetime, timezone
# import os
# from functools import wraps
# import requests
# from dotenv import load_dotenv
# from uuid import uuid4

# # Optional DB
# from pymongo import MongoClient
# from pymongo.errors import PyMongoError

# # Load .env if present
# load_dotenv()

# app = Flask(__name__)
# app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-me-in-prod")

# # -----------------------------
# # Data layer (MongoDB or FAKE_DB)
# # -----------------------------
# MONGO_URI = os.environ.get("MONGO_URI")  # e.g. mongodb://localhost:27017 or Atlas URI
# MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "aichat")
# MONGO_USERS_COLL = os.environ.get("MONGO_USERS_COLL", "users")
# MONGO_CONVS_COLL = os.environ.get("MONGO_CONVS_COLL", "conversations")  # NEW: conversations metadata
# MONGO_MSGS_COLL  = os.environ.get("MONGO_MSGS_COLL",  "messages")       # NEW: chat messages

# mongo_client = None
# users_coll = None
# convs_coll = None
# msgs_coll = None

# def init_mongo():
#     """Initialize Mongo once, if configured."""
#     global mongo_client, users_coll, convs_coll, msgs_coll
#     if MONGO_URI and mongo_client is None:
#         try:
#             mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
#             mongo_client.admin.command("ping")
#             db = mongo_client[MONGO_DB_NAME]
#             users_coll = db[MONGO_USERS_COLL]
#             convs_coll = db[MONGO_CONVS_COLL]
#             msgs_coll  = db[MONGO_MSGS_COLL]
#             # Indexes
#             users_coll.create_index("email", unique=True)
#             convs_coll.create_index([("user_email", 1), ("updated_at", -1)])
#             convs_coll.create_index([("user_email", 1), ("chat_id", 1)], unique=True)
#             msgs_coll.create_index([("user_email", 1), ("chat_id", 1), ("ts", 1)])
#         except Exception as e:
#             mongo_client = None
#             users_coll = convs_coll = msgs_coll = None
#             app.logger.warning(f"Mongo init failed: {e}. Falling back to FAKE_DB.")

# init_mongo()

# def using_mongo() -> bool:
#     """Return True if Mongo collections are wired up."""
#     return users_coll is not None and convs_coll is not None and msgs_coll is not None

# # FAKE DB fallback (used if Mongo not configured / reachable)
# FAKE_DB = {
#     "users": {
#         "demo@example.com": {"password": "demo123", "plan": "free", "name": "Demo User"}
#     },
#     "conversations": {  # email -> list of conv dicts
#         # "demo@example.com": [{"chat_id":"...", "title":"New chat", "created_at":"...", "updated_at":"..."}]
#     },
#     "messages": {       # chat_id -> list of messages
#         # "chat_id": [{"role":"user/assistant","text":"...","ts":"..."}]
#     }
# }

# # -----------------------------
# # User helpers
# # -----------------------------
# def get_user(email: str):
#     """Return user dict by email, from Mongo if available, else FAKE_DB."""
#     if using_mongo():
#         doc = users_coll.find_one({"email": email})
#         if not doc:
#             return None
#         return {
#             "email": doc["email"],
#             "password": doc.get("password", ""),
#             "plan": doc.get("plan", "free"),
#             "name": doc.get("name", ""),
#         }
#     return FAKE_DB["users"].get(email)

# def upsert_user(email: str, password: str = "", plan: str = "free", name: str = ""):
#     """Create or update user."""
#     if using_mongo():
#         try:
#             users_coll.update_one(
#                 {"email": email},
#                 {"$setOnInsert": {"email": email},
#                  "$set": {"password": password, "plan": plan, "name": name}},
#                 upsert=True,
#             )
#             return True
#         except PyMongoError as e:
#             app.logger.error(f"Mongo upsert error: {e}")
#             return False
#     FAKE_DB["users"].setdefault(email, {"password": password, "plan": plan, "name": name})
#     FAKE_DB["users"][email].update({"password": password, "plan": plan, "name": name})
#     return True

# def set_user_plan(email: str, plan: str):
#     """Update plan only."""
#     if using_mongo():
#         try:
#             users_coll.update_one({"email": email}, {"$set": {"plan": plan}}, upsert=True)
#             return True
#         except PyMongoError as e:
#             app.logger.error(f"Mongo plan update error: {e}")
#             return False
#     FAKE_DB["users"].setdefault(email, {"password": "", "plan": "free"})
#     FAKE_DB["users"][email]["plan"] = plan
#     return True

# # -----------------------------
# # Conversations + Messages helpers
# # -----------------------------
# def now_iso():
#     return datetime.now(timezone.utc).isoformat()

# def create_conversation(user_email: str, title: str = "New chat"):
#     chat_id = uuid4().hex
#     doc = {
#         "user_email": user_email,
#         "chat_id": chat_id,
#         "title": title,
#         "created_at": now_iso(),
#         "updated_at": now_iso(),
#     }
#     if using_mongo():
#         try:
#             convs_coll.insert_one(doc)
#             return chat_id
#         except Exception as e:
#             app.logger.error(f"Mongo create conversation error: {e}")
#             return None
#     FAKE_DB["conversations"].setdefault(user_email, [])
#     FAKE_DB["conversations"][user_email].append(doc)
#     return chat_id

# def list_conversations(user_email: str, limit: int = 100):
#     if using_mongo():
#         try:
#             cur = convs_coll.find({"user_email": user_email}).sort("updated_at", -1).limit(limit)
#             return [{"chat_id": d["chat_id"], "title": d.get("title", "New chat"),
#                      "created_at": d.get("created_at",""), "updated_at": d.get("updated_at","")} for d in cur]
#         except Exception as e:
#             app.logger.error(f"Mongo list conversations error: {e}")
#             return []
#     convs = FAKE_DB["conversations"].get(user_email, [])
#     return sorted(convs, key=lambda c: c.get("updated_at",""), reverse=True)[:limit]

# def rename_conversation(user_email: str, chat_id: str, title: str):
#     if using_mongo():
#         try:
#             res = convs_coll.update_one({"user_email": user_email, "chat_id": chat_id},
#                                         {"$set": {"title": title, "updated_at": now_iso()}})
#             return res.matched_count > 0
#         except Exception as e:
#             app.logger.error(f"Mongo rename conversation error: {e}")
#             return False
#     convs = FAKE_DB["conversations"].get(user_email, [])
#     for c in convs:
#         if c["chat_id"] == chat_id:
#             c["title"] = title
#             c["updated_at"] = now_iso()
#             return True
#     return False

# def touch_conversation(user_email: str, chat_id: str):
#     if using_mongo():
#         try:
#             convs_coll.update_one({"user_email": user_email, "chat_id": chat_id},
#                                   {"$set": {"updated_at": now_iso()}})
#         except Exception as e:
#             app.logger.error(f"Mongo touch conversation error: {e}")
#     else:
#         convs = FAKE_DB["conversations"].get(user_email, [])
#         for c in convs:
#             if c["chat_id"] == chat_id:
#                 c["updated_at"] = now_iso()

# def delete_conversation(user_email: str, chat_id: str):
#     if using_mongo():
#         try:
#             convs_coll.delete_one({"user_email": user_email, "chat_id": chat_id})
#             msgs_coll.delete_many({"user_email": user_email, "chat_id": chat_id})
#             return True
#         except Exception as e:
#             app.logger.error(f"Mongo delete conversation error: {e}")
#             return False
#     # fallback
#     convs = FAKE_DB["conversations"].get(user_email, [])
#     FAKE_DB["conversations"][user_email] = [c for c in convs if c["chat_id"] != chat_id]
#     FAKE_DB["messages"].pop(chat_id, None)
#     return True

# def save_message(user_email: str, chat_id: str, role: str, text: str):
#     doc = {"user_email": user_email, "chat_id": chat_id, "role": role, "text": text, "ts": now_iso()}
#     if using_mongo():
#         try:
#             msgs_coll.insert_one(doc)
#             touch_conversation(user_email, chat_id)
#             return True
#         except Exception as e:
#             app.logger.error(f"Mongo save message error: {e}")
#             return False
#     FAKE_DB["messages"].setdefault(chat_id, [])
#     FAKE_DB["messages"][chat_id].append(doc)
#     touch_conversation(user_email, chat_id)
#     return True

# def get_messages(user_email: str, chat_id: str, limit: int = 500):
#     if using_mongo():
#         try:
#             cur = msgs_coll.find({"user_email": user_email, "chat_id": chat_id}).sort("ts", 1).limit(limit)
#             return [{"role": d.get("role","user"), "text": d.get("text",""), "ts": d.get("ts","")} for d in cur]
#         except Exception as e:
#             app.logger.error(f"Mongo get messages error: {e}")
#             return []
#     msgs = FAKE_DB["messages"].get(chat_id, [])
#     return sorted(msgs, key=lambda m: m.get("ts",""))[:limit]

# def conversation_exists(user_email: str, chat_id: str) -> bool:
#     if using_mongo():
#         try:
#             return convs_coll.count_documents({"user_email": user_email, "chat_id": chat_id}, limit=1) == 1
#         except Exception as e:
#             app.logger.error(f"Mongo conversation exists error: {e}")
#             return False
#     convs = FAKE_DB["conversations"].get(user_email, [])
#     return any(c["chat_id"] == chat_id for c in convs)

# # -----------------------------
# # Gemini config
# # -----------------------------
# GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
# GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
# GEMINI_BASE = os.environ.get("GEMINI_BASE", "https://generativelanguage.googleapis.com")
# GEMINI_PATH = f"/v1beta/models/{GEMINI_MODEL}:generateContent"

# # -----------------------------
# # Auth
# # -----------------------------
# def login_required(view):
#     @wraps(view)
#     def wrapped(*args, **kwargs):
#         if not session.get("user_email"):
#             return redirect(url_for("login", next=request.path))
#         return view(*args, **kwargs)
#     return wrapped

# # -----------------------------
# # Routes (pages)
# # -----------------------------
# @app.route("/")
# @login_required
# def index():
#     user_email = session.get("user_email")
#     user = get_user(user_email) or {"plan": "free", "name": ""}
#     return render_template("index.html",
#                            user_email=user_email,
#                            plan=user.get("plan", "free"),
#                            name=user.get("name", ""))

# # -----------------------------
# # API: conversations
# # -----------------------------
# @app.post("/api/chats")
# @login_required
# def api_create_chat():
#     user_email = session["user_email"]
#     payload = request.get_json(silent=True) or {}
#     title = (payload.get("title") or "New chat").strip() or "New chat"
#     chat_id = create_conversation(user_email, title=title)
#     if not chat_id:
#         return jsonify({"error": "Failed to create chat"}), 500
#     return jsonify({"chat_id": chat_id, "title": title})

# @app.get("/api/chats")
# @login_required
# def api_list_chats():
#     user_email = session["user_email"]
#     convs = list_conversations(user_email, limit=200)
#     return jsonify({"chats": convs})

# @app.get("/api/chats/<chat_id>")
# @login_required
# def api_get_chat(chat_id):
#     user_email = session["user_email"]
#     if not conversation_exists(user_email, chat_id):
#         return jsonify({"error": "Not found"}), 404
#     msgs = get_messages(user_email, chat_id, limit=1000)
#     return jsonify({"chat_id": chat_id, "messages": msgs})

# @app.patch("/api/chats/<chat_id>")
# @login_required
# def api_rename_chat(chat_id):
#     user_email = session["user_email"]
#     data = request.get_json(silent=True) or {}
#     title = (data.get("title") or "").strip()
#     if not title:
#         return jsonify({"error": "Title required"}), 400
#     ok = rename_conversation(user_email, chat_id, title)
#     if not ok:
#         return jsonify({"error": "Update failed"}), 500
#     return jsonify({"ok": True})

# @app.delete("/api/chats/<chat_id>")
# @login_required
# def api_delete_chat(chat_id):
#     user_email = session["user_email"]
#     ok = delete_conversation(user_email, chat_id)
#     if not ok:
#         return jsonify({"error": "Delete failed"}), 500
#     return jsonify({"ok": True})

# # -----------------------------
# # API: messaging
# # -----------------------------
# @app.post("/api/chat")
# @login_required
# def api_chat():
#     """Send a message within a conversation (chat_id). If no chat_id, create one."""
#     user_email = session["user_email"]
#     data = request.get_json(silent=True) or {}
#     message = (data.get("message") or "").strip()
#     chat_id = (data.get("chat_id") or "").strip()

#     if not message:
#         return jsonify({"error": "Empty message"}), 400

#     # Create a new conversation if none provided
#     if not chat_id or not conversation_exists(user_email, chat_id):
#         chat_id = create_conversation(user_email, title="New chat")
#         if not chat_id:
#             return jsonify({"error": "Failed to create chat"}), 500

#     # Save user message
#     save_message(user_email, chat_id, "user", message)

#     # Generate and save assistant reply
#     reply = generate_reply(message)
#     save_message(user_email, chat_id, "assistant", reply)

#     # If it’s the first user message, set title from it (first ~40 chars)
#     conv_msgs = get_messages(user_email, chat_id, limit=2)
#     if len(conv_msgs) <= 2:
#         short = (message[:40] + "…") if len(message) > 40 else message
#         if short.strip():
#             rename_conversation(user_email, chat_id, short)

#     return jsonify({
#         "chat_id": chat_id,
#         "reply": reply,
#         "timestamp": datetime.utcnow().isoformat() + "Z"
#     })

# # (Optional) legacy: return last N messages across all chats
# @app.get("/api/history")
# @login_required
# def api_history_legacy():
#     # Kept for backward compatibility if your UI still calls it.
#     # Returns recent conversations (titles only).
#     user_email = session["user_email"]
#     convs = list_conversations(user_email, limit=50)
#     return jsonify({"chats": convs})

# # -----------------------------
# # Login / Logout / Subscribe
# # -----------------------------
# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         email = (request.form.get("email") or "").strip().lower()
#         password = request.form.get("password") or ""
#         user = get_user(email)

#         if user and user.get("password") == password:
#             session["user_email"] = email
#             flash("Logged in successfully.", "success")
#             return redirect(request.args.get("next") or url_for("index"))

#         flash("Invalid credentials.", "error")
#         return render_template("login.html", show="login")

#     show = request.args.get("tab", "login")
#     return render_template("login.html", show=show)

# @app.get("/logout")
# @login_required
# def logout():
#     session.clear()
#     flash("Logged out.", "info")
#     return redirect(url_for("login"))

# @app.route("/subscribe", methods=["GET", "POST"])
# @login_required
# def subscribe():
#     email = session["user_email"]
#     user = get_user(email) or {"password": "", "plan": "free"}
#     if request.method == "POST":
#         plan = request.form.get("plan") or "free"
#         if plan not in ("free", "pro"):
#             flash("Unknown plan.", "error")
#             return redirect(url_for("subscribe"))
#         ok = set_user_plan(email, plan)
#         if not ok:
#             flash("Failed to update subscription.", "error")
#             return redirect(url_for("subscribe"))
#         flash(f"Subscription updated to {plan}.", "success")
#         return redirect(url_for("index"))
#     return render_template("subscribe.html", current_plan=user.get("plan", "free"))

# # -----------------------------
# # LLM call
# # -----------------------------
# def generate_reply(msg: str) -> str:
#     if not msg:
#         return "Say something and I'll respond!"
#     if not GEMINI_API_KEY:
#         return "GEMINI_API_KEY not set. Please configure it in your environment or .env file."

#     try:
#         url = f"{GEMINI_BASE.rstrip('/')}{GEMINI_PATH}?key={GEMINI_API_KEY}"
#         payload = {"contents": [{"role": "user", "parts": [{"text": msg}]}]}
#         headers = {"Content-Type": "application/json"}
#         resp = requests.post(url, json=payload, headers=headers, timeout=60)

#         if not resp.ok:
#             try:
#                 err = resp.json()
#             except Exception:
#                 err = {"error": {"message": resp.text}}
#             return f"[Gemini HTTP {resp.status_code}: {err.get('error', {}).get('message', 'Unknown error')}]"

#         data = resp.json()
#         candidates = data.get("candidates", [])
#         if not candidates:
#             return "[Gemini: no candidates returned]"
#         parts = candidates[0].get("content", {}).get("parts", [])
#         text = "".join(p.get("text", "") for p in parts)
#         return text or "[Gemini returned empty text]"

#     except Exception as e:
#         return f"[Gemini error: {e}]"

# # -----------------------------
# # Main
# # -----------------------------
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=True)



from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from datetime import datetime, timezone
import os
from functools import wraps
import requests
from dotenv import load_dotenv
from uuid import uuid4

# Optional DB
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Load .env if present
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-me-in-prod")

# -----------------------------
# Data layer (MongoDB or FAKE_DB)
# -----------------------------
MONGO_URI = os.environ.get("MONGO_URI")  # e.g. mongodb://localhost:27017 or Atlas URI
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "aichat")
MONGO_USERS_COLL = os.environ.get("MONGO_USERS_COLL", "users")
MONGO_CONVS_COLL = os.environ.get("MONGO_CONVS_COLL", "conversations")  # conversations metadata
MONGO_MSGS_COLL  = os.environ.get("MONGO_MSGS_COLL",  "messages")       # chat messages

mongo_client = None
users_coll = None
convs_coll = None
msgs_coll = None

def init_mongo():
    """Initialize Mongo once, if configured."""
    global mongo_client, users_coll, convs_coll, msgs_coll
    if MONGO_URI and mongo_client is None:
        try:
            mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
            mongo_client.admin.command("ping")
            db = mongo_client[MONGO_DB_NAME]
            users_coll = db[MONGO_USERS_COLL]
            convs_coll = db[MONGO_CONVS_COLL]
            msgs_coll  = db[MONGO_MSGS_COLL]
            # Indexes
            users_coll.create_index("email", unique=True)
            convs_coll.create_index([("user_email", 1), ("updated_at", -1)])
            convs_coll.create_index([("user_email", 1), ("chat_id", 1)], unique=True)
            msgs_coll.create_index([("user_email", 1), ("chat_id", 1), ("ts", 1)])
        except Exception as e:
            mongo_client = None
            users_coll = convs_coll = msgs_coll = None
            app.logger.warning(f"Mongo init failed: {e}. Falling back to FAKE_DB.")

init_mongo()

def using_mongo() -> bool:
    """Return True if Mongo collections are wired up."""
    return users_coll is not None and convs_coll is not None and msgs_coll is not None

# FAKE DB fallback (used if Mongo not configured / reachable)
FAKE_DB = {
    "users": {
        "demo@example.com": {"password": "demo123", "plan": "free", "name": "Demo User"}
    },
    "conversations": {},  # email -> list of conv dicts
    "messages": {}        # chat_id -> list of messages
}

# -----------------------------
# User helpers
# -----------------------------
def get_user(email: str):
    """Return user dict by email, from Mongo if available, else FAKE_DB."""
    if using_mongo():
        doc = users_coll.find_one({"email": email})
        if not doc:
            return None
        return {
            "email": doc["email"],
            "password": doc.get("password", ""),
            "plan": doc.get("plan", "free"),
            "name": doc.get("name", ""),
        }
    return FAKE_DB["users"].get(email)

def upsert_user(email: str, password: str = "", plan: str = "free", name: str = ""):
    """Create or update user."""
    if using_mongo():
        try:
            users_coll.update_one(
                {"email": email},
                {"$setOnInsert": {"email": email},
                 "$set": {"password": password, "plan": plan, "name": name}},
                upsert=True,
            )
            return True
        except PyMongoError as e:
            app.logger.error(f"Mongo upsert error: {e}")
            return False
    FAKE_DB["users"].setdefault(email, {"password": password, "plan": plan, "name": name})
    FAKE_DB["users"][email].update({"password": password, "plan": plan, "name": name})
    return True

def set_user_plan(email: str, plan: str):
    """Update plan only."""
    if using_mongo():
        try:
            users_coll.update_one({"email": email}, {"$set": {"plan": plan}}, upsert=True)
            return True
        except PyMongoError as e:
            app.logger.error(f"Mongo plan update error: {e}")
            return False
    FAKE_DB["users"].setdefault(email, {"password": "", "plan": "free"})
    FAKE_DB["users"][email]["plan"] = plan
    return True

# -----------------------------
# Conversations + Messages helpers
# -----------------------------
def now_iso():
    return datetime.now(timezone.utc).isoformat()

def create_conversation(user_email: str, title: str = "New chat"):
    chat_id = uuid4().hex
    doc = {
        "user_email": user_email,
        "chat_id": chat_id,
        "title": title,
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    if using_mongo():
        try:
            convs_coll.insert_one(doc)
            return chat_id
        except Exception as e:
            app.logger.error(f"Mongo create conversation error: {e}")
            return None
    FAKE_DB["conversations"].setdefault(user_email, [])
    FAKE_DB["conversations"][user_email].append(doc)
    return chat_id

def list_conversations(user_email: str, limit: int = 100):
    if using_mongo():
        try:
            cur = convs_coll.find({"user_email": user_email}).sort("updated_at", -1).limit(limit)
            return [{"chat_id": d["chat_id"], "title": d.get("title", "New chat"),
                     "created_at": d.get("created_at",""), "updated_at": d.get("updated_at","")} for d in cur]
        except Exception as e:
            app.logger.error(f"Mongo list conversations error: {e}")
            return []
    convs = FAKE_DB["conversations"].get(user_email, [])
    return sorted(convs, key=lambda c: c.get("updated_at",""), reverse=True)[:limit]

def rename_conversation(user_email: str, chat_id: str, title: str):
    if using_mongo():
        try:
            res = convs_coll.update_one({"user_email": user_email, "chat_id": chat_id},
                                        {"$set": {"title": title, "updated_at": now_iso()}})
            return res.matched_count > 0
        except Exception as e:
            app.logger.error(f"Mongo rename conversation error: {e}")
            return False
    convs = FAKE_DB["conversations"].get(user_email, [])
    for c in convs:
        if c["chat_id"] == chat_id:
            c["title"] = title
            c["updated_at"] = now_iso()
            return True
    return False

def touch_conversation(user_email: str, chat_id: str):
    if using_mongo():
        try:
            convs_coll.update_one({"user_email": user_email, "chat_id": chat_id},
                                  {"$set": {"updated_at": now_iso()}})
        except Exception as e:
            app.logger.error(f"Mongo touch conversation error: {e}")
    else:
        convs = FAKE_DB["conversations"].get(user_email, [])
        for c in convs:
            if c["chat_id"] == chat_id:
                c["updated_at"] = now_iso()

def delete_conversation(user_email: str, chat_id: str):
    if using_mongo():
        try:
            convs_coll.delete_one({"user_email": user_email, "chat_id": chat_id})
            msgs_coll.delete_many({"user_email": user_email, "chat_id": chat_id})
            return True
        except Exception as e:
            app.logger.error(f"Mongo delete conversation error: {e}")
            return False
    # fallback
    convs = FAKE_DB["conversations"].get(user_email, [])
    FAKE_DB["conversations"][user_email] = [c for c in convs if c["chat_id"] != chat_id]
    FAKE_DB["messages"].pop(chat_id, None)
    return True

def save_message(user_email: str, chat_id: str, role: str, text: str):
    doc = {"user_email": user_email, "chat_id": chat_id, "role": role, "text": text, "ts": now_iso()}
    if using_mongo():
        try:
            msgs_coll.insert_one(doc)
            touch_conversation(user_email, chat_id)
            return True
        except Exception as e:
            app.logger.error(f"Mongo save message error: {e}")
            return False
    FAKE_DB["messages"].setdefault(chat_id, [])
    FAKE_DB["messages"][chat_id].append(doc)
    touch_conversation(user_email, chat_id)
    return True

def get_messages(user_email: str, chat_id: str, limit: int = 500):
    if using_mongo():
        try:
            cur = msgs_coll.find({"user_email": user_email, "chat_id": chat_id}).sort("ts", 1).limit(limit)
            return [{"role": d.get("role","user"), "text": d.get("text",""), "ts": d.get("ts","")} for d in cur]
        except Exception as e:
            app.logger.error(f"Mongo get messages error: {e}")
            return []
    msgs = FAKE_DB["messages"].get(chat_id, [])
    return sorted(msgs, key=lambda m: m.get("ts",""))[:limit]

def conversation_exists(user_email: str, chat_id: str) -> bool:
    if using_mongo():
        try:
            return convs_coll.count_documents({"user_email": user_email, "chat_id": chat_id}, limit=1) == 1
        except Exception as e:
            app.logger.error(f"Mongo conversation exists error: {e}")
            return False
    convs = FAKE_DB["conversations"].get(user_email, [])
    return any(c["chat_id"] == chat_id for c in convs)

# -----------------------------
# Gemini config
# -----------------------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_BASE = os.environ.get("GEMINI_BASE", "https://generativelanguage.googleapis.com")
GEMINI_PATH = f"/v1beta/models/{GEMINI_MODEL}:generateContent"

# -----------------------------
# Auth
# -----------------------------
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_email"):
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped

# -----------------------------
# Routes (pages)
# -----------------------------
@app.route("/")
@login_required
def index():
    user_email = session.get("user_email")
    user = get_user(user_email) or {"plan": "free", "name": ""}
    return render_template("index.html",
                           user_email=user_email,
                           plan=user.get("plan", "free"),
                           name=user.get("name", ""))

# -----------------------------
# API: conversations
# -----------------------------
@app.post("/api/chats")
@login_required
def api_create_chat():
    user_email = session["user_email"]
    payload = request.get_json(silent=True) or {}
    title = (payload.get("title") or "New chat").strip() or "New chat"
    chat_id = create_conversation(user_email, title=title)
    if not chat_id:
        return jsonify({"error": "Failed to create chat"}), 500
    return jsonify({"chat_id": chat_id, "title": title})

@app.get("/api/chats")
@login_required
def api_list_chats():
    user_email = session["user_email"]
    convs = list_conversations(user_email, limit=200)
    return jsonify({"chats": convs})

@app.get("/api/chats/<chat_id>")
@login_required
def api_get_chat(chat_id):
    user_email = session["user_email"]
    if not conversation_exists(user_email, chat_id):
        return jsonify({"error": "Not found"}), 404
    msgs = get_messages(user_email, chat_id, limit=1000)
    return jsonify({"chat_id": chat_id, "messages": msgs})

@app.patch("/api/chats/<chat_id>")
@login_required
def api_rename_chat(chat_id):
    user_email = session["user_email"]
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "Title required"}), 400
    ok = rename_conversation(user_email, chat_id, title)
    if not ok:
        return jsonify({"error": "Update failed"}), 500
    return jsonify({"ok": True})

@app.delete("/api/chats/<chat_id>")
@login_required
def api_delete_chat(chat_id):
    user_email = session["user_email"]
    ok = delete_conversation(user_email, chat_id)
    if not ok:
        return jsonify({"error": "Delete failed"}), 500
    return jsonify({"ok": True})

# -----------------------------
# API: messaging
# -----------------------------
@app.post("/api/chat")
@login_required
def api_chat():
    """Send a message within a conversation (chat_id). If no chat_id, create one."""
    user_email = session["user_email"]
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    chat_id = (data.get("chat_id") or "").strip()

    if not message:
        return jsonify({"error": "Empty message"}), 400

    # Create a new conversation if none provided
    if not chat_id or not conversation_exists(user_email, chat_id):
        chat_id = create_conversation(user_email, title="New chat")
        if not chat_id:
            return jsonify({"error": "Failed to create chat"}), 500

    # Save user message
    save_message(user_email, chat_id, "user", message)

    # Generate and save assistant reply
    reply = generate_reply(message)
    save_message(user_email, chat_id, "assistant", reply)

    # If it’s the first user message, set title from it (first ~40 chars)
    conv_msgs = get_messages(user_email, chat_id, limit=2)
    if len(conv_msgs) <= 2:
        short = (message[:40] + "…") if len(message) > 40 else message
        if short.strip():
            rename_conversation(user_email, chat_id, short)

    return jsonify({
        "chat_id": chat_id,
        "reply": reply,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

# (Optional) legacy: recent conversations (titles only)
@app.get("/api/history")
@login_required
def api_history_legacy():
    user_email = session["user_email"]
    convs = list_conversations(user_email, limit=50)
    return jsonify({"chats": convs})

# -----------------------------
# Login / Register / Logout / Subscribe
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        user = get_user(email)

        if user and user.get("password") == password:
            session["user_email"] = email
            flash("Logged in successfully.", "success")
            return redirect(request.args.get("next") or url_for("index"))

        flash("Invalid credentials.", "error")
        return render_template("login.html", show="login")

    show = request.args.get("tab", "login")
    return render_template("login.html", show=show)

@app.route("/register", methods=["POST"])
def register():
    name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""
    confirm_password = request.form.get("confirm_password") or ""

    # Basic validations
    if not email or not password:
        flash("Email and password are required.", "error")
        return render_template("login.html", show="register", prefill_email=email)
    if password != confirm_password:
        flash("Passwords do not match.", "error")
        return render_template("login.html", show="register", prefill_email=email)

    # Already exists?
    if get_user(email):
        flash("An account with that email already exists. Please log in.", "info")
        return render_template("login.html", show="login", prefill_email=email)

    # Create user
    ok = upsert_user(email, password=password, plan="free", name=name)
    if not ok:
        flash("Could not create account. Please try again.", "error")
        return render_template("login.html", show="register", prefill_email=email)

    # Same page flow: switch to login tab and prefill email
    flash("Account created. Please log in.", "success")
    return render_template("login.html", show="login", prefill_email=email)

@app.get("/logout")
@login_required
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("login"))

@app.route("/subscribe", methods=["GET", "POST"])
@login_required
def subscribe():
    email = session["user_email"]
    user = get_user(email) or {"password": "", "plan": "free"}
    if request.method == "POST":
        plan = request.form.get("plan") or "free"
        if plan not in ("free", "pro"):
            flash("Unknown plan.", "error")
            return redirect(url_for("subscribe"))
        ok = set_user_plan(email, plan)
        if not ok:
            flash("Failed to update subscription.", "error")
            return redirect(url_for("subscribe"))
        flash(f"Subscription updated to {plan}.", "success")
        return redirect(url_for("index"))
    return render_template("subscribe.html", current_plan=user.get("plan", "free"))

# -----------------------------
# LLM call
# -----------------------------
def generate_reply(msg: str) -> str:
    if not msg:
        return "Say something and I'll respond!"
    if not GEMINI_API_KEY:
        return "GEMINI_API_KEY not set. Please configure it in your environment or .env file."

    try:
        url = f"{GEMINI_BASE.rstrip('/')}{GEMINI_PATH}?key={GEMINI_API_KEY}"
        payload = {"contents": [{"role": "user", "parts": [{"text": msg}]}]}
        headers = {"Content-Type": "application/json"}
        resp = requests.post(url, json=payload, headers=headers, timeout=60)

        if not resp.ok:
            try:
                err = resp.json()
            except Exception:
                err = {"error": {"message": resp.text}}
            return f"[Gemini HTTP {resp.status_code}: {err.get('error', {}).get('message', 'Unknown error')}]"

        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            return "[Gemini: no candidates returned]"
        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts)
        return text or "[Gemini returned empty text]"

    except Exception as e:
        return f"[Gemini error: {e}]"

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=True)
