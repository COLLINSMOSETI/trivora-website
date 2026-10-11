"""Admin authentication API."""
from flask import Blueprint, g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from .. import config
from ..database import get_db
from ..security import admin_required, client_ip, issue_token, limiter
from ..utils import clean

bp = Blueprint("auth", __name__, url_prefix="/api/admin")

_DUMMY_HASH = generate_password_hash("not-a-real-password")  # keeps timing similar for unknown users


@bp.post("/login")
def login():
    if not limiter.allow(f"login:{client_ip()}", 8, 900):
        return jsonify(ok=False, error="Too many attempts. Wait 15 minutes and try again."), 429
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(ok=False, error="Please send the sign-in form as JSON."), 400

    username = clean(data.get("username"), 60)
    password = str(data.get("password", ""))[:200]
    row = get_db().execute("SELECT * FROM admins WHERE username = ?", (username,)).fetchone()
    valid = check_password_hash(row["password_hash"] if row else _DUMMY_HASH, password)
    if not (row and valid):
        return jsonify(ok=False, error="Incorrect username or password."), 401

    return jsonify(
        ok=True,
        token=issue_token(row),
        expires_in=config.TOKEN_MAX_AGE,
        admin={"username": row["username"]},
    )


@bp.get("/me")
@admin_required
def me():
    """Confirms the token is valid and gives the dashboard its labels (single source of truth)."""
    return jsonify(
        ok=True,
        admin={"username": g.admin["username"]},
        meta={"services": config.SERVICES, "statuses": config.STATUSES, "company": config.COMPANY},
    )


@bp.post("/password")
@admin_required
def change_password():
    data = request.get_json(silent=True) or {}
    current = str(data.get("current", ""))[:200]
    new = str(data.get("new", ""))[:200]
    if len(new) < 10:
        return jsonify(ok=False, error="New password must be at least 10 characters."), 400
    if not check_password_hash(g.admin["password_hash"], current):
        return jsonify(ok=False, error="Current password is incorrect."), 400
    db = get_db()
    db.execute("UPDATE admins SET password_hash = ? WHERE id = ?", (generate_password_hash(new), g.admin["id"]))
    db.commit()
    return jsonify(ok=True, message="Password updated. Please sign in again.")
