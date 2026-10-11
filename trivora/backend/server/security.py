"""Rate limiting, admin tokens, CORS and security headers.

The frontend and backend are separate apps, so admin sign-in uses a signed token
that the frontend sends in an `Authorization: Bearer <token>` header (no cookies,
so it works the same whether both run together or on different domains).
"""
import hashlib
import secrets
import threading
import time
from collections import defaultdict, deque
from functools import wraps

from flask import g, jsonify, request
from itsdangerous import BadSignature, URLSafeTimedSerializer

from . import config, database

# ---------------------------------------------------------------- rate limiter


class RateLimiter:
    def __init__(self):
        self.hits = defaultdict(deque)
        self.lock = threading.Lock()

    def allow(self, key, limit, window):
        now = time.time()
        with self.lock:
            q = self.hits[key]
            while q and q[0] <= now - window:
                q.popleft()
            if len(q) >= limit:
                return False
            q.append(now)
            return True


limiter = RateLimiter()


def client_ip():
    if config.TRUST_PROXY:
        forwarded = request.headers.get("X-Forwarded-For", "")
        if forwarded:
            return forwarded.split(",")[0].strip()[:64]
    return (request.remote_addr or "")[:64]


# ---------------------------------------------------------------- admin tokens
_serializer = URLSafeTimedSerializer(config.SECRET_KEY, salt="trivora-admin-token")


def _fingerprint(password_hash):
    return hashlib.sha256(password_hash.encode()).hexdigest()[:16]


def issue_token(admin_row):
    """Signed token. It embeds a password fingerprint, so changing the password signs everyone out."""
    return _serializer.dumps({"id": admin_row["id"], "pv": _fingerprint(admin_row["password_hash"])})


def _admin_from_request():
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    try:
        data = _serializer.loads(header[7:].strip(), max_age=config.TOKEN_MAX_AGE)
    except BadSignature:  # also covers expired tokens
        return None
    row = database.get_db().execute("SELECT * FROM admins WHERE id = ?", (data.get("id"),)).fetchone()
    if not row or not secrets.compare_digest(_fingerprint(row["password_hash"]), str(data.get("pv", ""))):
        return None
    return row


def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        admin = _admin_from_request()
        if admin is None:
            return jsonify(ok=False, error="Not signed in."), 401
        g.admin = admin
        return view(*args, **kwargs)

    return wrapper


# ---------------------------------------------------------------- CORS + headers
CSP = (
    "default-src 'self'; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
    "font-src https://fonts.gstatic.com; "
    "img-src 'self' data:; script-src 'self'; connect-src 'self'; "
    "frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
)


def _origin_allowed(origin):
    return bool(origin) and ("*" in config.CORS_ORIGINS or origin in config.CORS_ORIGINS)


def init_security(app):
    @app.before_request
    def preflight():
        if request.method == "OPTIONS" and request.path.startswith("/api/"):
            return app.make_response(("", 204))  # CORS headers are added in after_request
        return None

    @app.after_request
    def add_headers(resp):
        origin = request.headers.get("Origin")
        if request.path.startswith("/api/"):
            resp.headers["Cache-Control"] = "no-store"
            if _origin_allowed(origin):
                resp.headers["Access-Control-Allow-Origin"] = origin
                resp.headers["Vary"] = "Origin"
                resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
                resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PATCH, DELETE, OPTIONS"
                resp.headers["Access-Control-Max-Age"] = "600"
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("X-Frame-Options", "DENY")
        resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        if request.blueprint == "frontend":
            resp.headers.setdefault("Content-Security-Policy", CSP)
        return resp
