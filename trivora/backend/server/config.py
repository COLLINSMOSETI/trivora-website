"""Central settings for the Trivora backend.

Everything configurable is read from environment variables (or backend/.env).
See backend/.env.example for the full list.
"""
import os
import secrets

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .../trivora/backend
PROJECT_DIR = os.path.dirname(BASE_DIR)  # .../trivora  (holds frontend/ and backend/)


def _load_env_file():
    """Tiny .env loader so no extra dependency is needed."""
    path = os.path.join(BASE_DIR, ".env")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env_file()


def _csv_env(name):
    return [item.strip().rstrip("/") for item in os.environ.get(name, "").split(",") if item.strip()]


# ---- Paths --------------------------------------------------------------
DATA_DIR = os.environ.get("TRIVORA_DATA_DIR", os.path.join(BASE_DIR, "data"))
DB_PATH = os.environ.get("TRIVORA_DB", os.path.join(DATA_DIR, "trivora.db"))
FRONTEND_DIR = os.path.abspath(os.environ.get("FRONTEND_DIR", os.path.join(PROJECT_DIR, "frontend")))

# ---- How the frontend is connected ---------------------------------------
# SERVE_FRONTEND=1 : this backend also serves the ../frontend folder (one command, one address).
# SERVE_FRONTEND=0 : API only - host the frontend anywhere and list its address in CORS_ORIGINS.
SERVE_FRONTEND = os.environ.get("SERVE_FRONTEND", "1") == "1"
CORS_ORIGINS = _csv_env("CORS_ORIGINS")  # e.g. https://trivora.co.ke,https://www.trivora.co.ke
TRUST_PROXY = os.environ.get("TRUST_PROXY", "0") == "1"

# ---- Company (used in emails and the admin Settings page) ----------------
# NOTE: the public website (frontend/index.html) shows its own copy of these details.
COMPANY = {
    "name": "Trivora",
    "legal": "Trivora Technologies",
    "email": "trivoratechnologies1@gmail.com",
    "phones": [
        {"display": "0703502267", "tel": "+254703502267"},
        {"display": "+254 116 918656", "tel": "+254116918656"},
        {"display": "+254 112 061280", "tel": "+254112061280"},
    ],
    "whatsapp": "254703502267",
    "starting_price": 30000,
}

# These keys must match the <option value="..."> list in the contact form (frontend/index.html).
SERVICES = {
    "website": "Website development",
    "integration": "Systems integration",
    "app": "Mobile / web app",
    "ecommerce": "E-commerce / booking system",
    "maintenance": "Maintenance & support",
    "other": "Something else",
}
STATUSES = ["new", "contacted", "in_progress", "won", "closed"]

# ---- Email notifications -------------------------------------------------
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USER = os.environ.get("SMTP_USER", COMPANY["email"])
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")  # Gmail "App password"
NOTIFY_TO = os.environ.get("NOTIFY_TO", COMPANY["email"])
SEND_AUTOREPLY = os.environ.get("SEND_AUTOREPLY", "1") == "1"

# ---- Admin sign-in tokens ------------------------------------------------
TOKEN_MAX_AGE = 8 * 60 * 60  # seconds an admin sign-in stays valid


def _load_secret_key():
    env_key = os.environ.get("SECRET_KEY")
    if env_key:
        return env_key
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, ".secret_key")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            return fh.read().strip()
    key = secrets.token_hex(32)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(key)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
    return key


SECRET_KEY = _load_secret_key()
