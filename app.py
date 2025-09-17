# from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
# from datetime import datetime
# import os
# from functools import wraps
# import requests
# from dotenv import load_dotenv

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

# mongo_client = None
# users_coll = None

# def init_mongo():
#     """Initialize Mongo once, if configured."""
#     global mongo_client, users_coll
#     if MONGO_URI and mongo_client is None:
#         try:
#             mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
#             # Trigger a ping to fail fast if unreachable
#             mongo_client.admin.command("ping")
#             db = mongo_client[MONGO_DB_NAME]
#             users_coll = db[MONGO_USERS_COLL]
#             # Ensure index on email
#             users_coll.create_index("email", unique=True)
#         except Exception as e:
#             # Fallback to FAKE_DB if Mongo not reachable
#             mongo_client = None
#             users_coll = None
#             app.logger.warning(f"Mongo init failed: {e}. Falling back to FAKE_DB.")

# init_mongo()

# def using_mongo() -> bool:
#     """Return True if a Mongo collection is wired up."""
#     return users_coll is not None

# # FAKE DB fallback (used if Mongo not configured / reachable)
# FAKE_DB = {
#     "users": {
#         "demo@example.com": {"password": "demo123", "plan": "free"}
#     }
# }

# def get_user(email: str):
#     """Return user dict by email, from Mongo if available, else FAKE_DB."""
#     if using_mongo():
#         doc = users_coll.find_one({"email": email})
#         if not doc:
#             return None
#         return {"email": doc["email"], "password": doc.get("password", ""), "plan": doc.get("plan", "free")}
#     # Fallback
#     return FAKE_DB["users"].get(email)

# def upsert_user(email: str, password: str = "", plan: str = "free"):
#     """Create or update user."""
#     if using_mongo():
#         try:
#             users_coll.update_one(
#                 {"email": email},
#                 {"$setOnInsert": {"email": email},
#                  "$set": {"password": password, "plan": plan}},
#                 upsert=True,
#             )
#             return True
#         except PyMongoError as e:
#             app.logger.error(f"Mongo upsert error: {e}")
#             return False
#     # Fallback
#     FAKE_DB["users"].setdefault(email, {"password": password, "plan": plan})
#     # If already existed, update fields
#     FAKE_DB["users"][email].update({"password": password, "plan": plan})
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
#     # Fallback
#     FAKE_DB["users"].setdefault(email, {"password": "", "plan": "free"})
#     FAKE_DB["users"][email]["plan"] = plan
#     return True

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
# # Routes
# # -----------------------------
# @app.route("/")
# @login_required
# def index():
#     user_email = session.get("user_email")
#     user = get_user(user_email) or {"plan": "free"}
#     return render_template("index.html", user_email=user_email, plan=user.get("plan", "free"))

# @app.post("/api/chat")
# @login_required
# def chat():
#     data = request.get_json(silent=True) or {}
#     message = (data.get("message") or "").strip()
#     reply = generate_reply(message)
#     return jsonify({
#         "reply": reply,
#         "timestamp": datetime.utcnow().isoformat() + "Z"
#     })

# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         email = (request.form.get("email") or "").strip().lower()
#         password = request.form.get("password") or ""
#         user = get_user(email)
#         if user:
#             if user.get("password") == password:
#                 session["user_email"] = email
#                 flash("Logged in successfully.", "success")
#                 return redirect(request.args.get("next") or url_for("index"))
#             else:
#                 flash("Invalid credentials.", "error")
#         else:
#             # Optional: auto-provision demo users (comment out if not desired)
#             created = upsert_user(email, password=password, plan="free")
#             if created:
#                 session["user_email"] = email
#                 flash("Account created and logged in.", "success")
#                 return redirect(request.args.get("next") or url_for("index"))
#             flash("Could not create account.", "error")
#     return render_template("login.html")

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
#         payload = {
#             "contents": [
#                 {"role": "user", "parts": [{"text": msg}]}
#             ]
#         }
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
#     # Bind to 0.0.0.0 if running in a container; change as you like
#     app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=True)

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from datetime import datetime
import os
from functools import wraps
import requests
from dotenv import load_dotenv

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

mongo_client = None
users_coll = None

def init_mongo():
    """Initialize Mongo once, if configured."""
    global mongo_client, users_coll
    if MONGO_URI and mongo_client is None:
        try:
            mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
            # Trigger a ping to fail fast if unreachable
            mongo_client.admin.command("ping")
            db = mongo_client[MONGO_DB_NAME]
            users_coll = db[MONGO_USERS_COLL]
            # Ensure index on email
            users_coll.create_index("email", unique=True)
        except Exception as e:
            # Fallback to FAKE_DB if Mongo not reachable
            mongo_client = None
            users_coll = None
            app.logger.warning(f"Mongo init failed: {e}. Falling back to FAKE_DB.")

init_mongo()

def using_mongo() -> bool:
    """Return True if a Mongo collection is wired up."""
    return users_coll is not None

# FAKE DB fallback (used if Mongo not configured / reachable)
FAKE_DB = {
    "users": {
        "demo@example.com": {"password": "demo123", "plan": "free", "name": "Demo User"}
    }
}

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
    # Fallback
    return FAKE_DB["users"].get(email)

def upsert_user(email: str, password: str = "", plan: str = "free", name: str = ""):
    """Create or update user."""
    if using_mongo():
        try:
            users_coll.update_one(
                {"email": email},
                {
                    "$setOnInsert": {"email": email},
                    "$set": {"password": password, "plan": plan, "name": name},
                },
                upsert=True,
            )
            return True
        except PyMongoError as e:
            app.logger.error(f"Mongo upsert error: {e}")
            return False
    # Fallback
    FAKE_DB["users"].setdefault(email, {"password": password, "plan": plan, "name": name})
    # If already existed, update fields
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
    # Fallback
    FAKE_DB["users"].setdefault(email, {"password": "", "plan": "free"})
    FAKE_DB["users"][email]["plan"] = plan
    return True

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
# Routes
# -----------------------------
@app.route("/")
@login_required
def index():
    user_email = session.get("user_email")
    user = get_user(user_email) or {"plan": "free", "name": ""}
    return render_template("index.html", user_email=user_email, plan=user.get("plan", "free"), name=user.get("name", ""))

@app.post("/api/chat")
@login_required
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    reply = generate_reply(message)
    return jsonify({
        "reply": reply,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

# --- Updated LOGIN route: renders login.html with show tab ---
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

        # If no user or wrong password, show error and keep on login tab
        flash("Invalid credentials.", "error")
        return render_template("login.html", show="login")

    # GET: support /login?tab=register to open register pane
    show = request.args.get("tab", "login")
    return render_template("login.html", show=show)

# --- New REGISTER route: creates user then logs in (or switch to manual login if you prefer) ---
@app.route("/register", methods=["POST"])
def register():
    name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""
    confirm_password = request.form.get("confirm_password") or ""

    # Basic validations
    if not email or not password:
        flash("Email and password are required.", "error")
        return render_template("login.html", show="register")
    if password != confirm_password:
        flash("Passwords do not match.", "error")
        return render_template("login.html", show="register")
    if get_user(email):
        flash("An account with that email already exists. Please log in.", "error")
        return render_template("login.html", show="login")

    ok = upsert_user(email, password=password, plan="free", name=name)
    if not ok:
        flash("Could not create account. Please try again.", "error")
        return render_template("login.html", show="register")

    # Auto-login after registration
    session["user_email"] = email
    flash("Account created and logged in.", "success")
    return redirect(url_for("index"))

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
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": msg}]}
            ]
        }
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
    # Bind to 0.0.0.0 if running in a container; change as you like
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=True)
