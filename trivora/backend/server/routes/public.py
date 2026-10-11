"""Public API used by the website. No sign-in needed."""
from flask import Blueprint, jsonify, request

from .. import config
from ..database import get_db
from ..mailer import notify_new_enquiry
from ..security import client_ip, limiter
from ..utils import EMAIL_RE, PHONE_RE, clean, parse_ua

bp = Blueprint("public", __name__, url_prefix="/api")


@bp.get("/health")
def health():
    return jsonify(ok=True, service="trivora-backend")


@bp.post("/contact")
def contact():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(ok=False, error="Please send the form as JSON."), 400
    if clean(data.get("website"), 50):  # honeypot field - bots fill it in, humans never see it
        return jsonify(ok=True, message="Thank you! We will be in touch shortly.")

    ip = client_ip()
    if not limiter.allow(f"contact:{ip}", 5, 3600):
        return jsonify(ok=False, error="Too many requests. Please try again later or call us."), 429

    name = clean(data.get("name"), 100)
    email = clean(data.get("email"), 160)
    phone = clean(data.get("phone"), 20)
    service = clean(data.get("service"), 30) or "other"
    budget = clean(data.get("budget"), 60)
    message = clean(data.get("message"), 3000)

    errors = {}
    if len(name) < 2:
        errors["name"] = "Please enter your name."
    if not EMAIL_RE.match(email):
        errors["email"] = "Please enter a valid email address."
    if phone and not PHONE_RE.match(phone):
        errors["phone"] = "Please enter a valid phone number."
    if service not in config.SERVICES:
        errors["service"] = "Please choose a service."
    if len(message) < 10:
        errors["message"] = "Please tell us a little more (at least 10 characters)."
    if errors:
        return jsonify(ok=False, error=next(iter(errors.values())), errors=errors), 400

    db = get_db()
    cur = db.execute(
        "INSERT INTO enquiries (name, email, phone, service, budget, message, ip) VALUES (?,?,?,?,?,?,?)",
        (name, email, phone, service, budget, message, ip),
    )
    db.commit()
    notify_new_enquiry(
        cur.lastrowid,
        {"name": name, "email": email, "phone": phone, "service": service, "budget": budget, "message": message},
    )
    return jsonify(ok=True, message="Thank you! Your request has been received. We will contact you shortly.")


@bp.post("/track")
def track():
    """The website calls this once per visit. Cookie-free: repeat visits are de-duplicated by IP + browser."""
    data = request.get_json(silent=True) or {}
    ip = client_ip()
    if not limiter.allow(f"track:{ip}", 60, 3600):
        return jsonify(ok=True)

    path = clean(data.get("path"), 200) or "/"
    referrer = clean(data.get("referrer"), 300)
    ua = request.headers.get("User-Agent", "")[:300]
    device, browser, os_name, is_bot = parse_ua(ua)

    db = get_db()
    if not is_bot:
        seen = db.execute(
            "SELECT 1 FROM visitors WHERE ip = ? AND user_agent = ? AND path = ? AND is_bot = 0 "
            "AND created_at > datetime('now', '-30 minutes') LIMIT 1",
            (ip, ua, path),
        ).fetchone()
        if seen:
            return jsonify(ok=True)

    db.execute(
        "INSERT INTO visitors (ip, path, referrer, user_agent, device, browser, os, is_bot) VALUES (?,?,?,?,?,?,?,?)",
        (ip, path, referrer, ua, device, browser, os_name, is_bot),
    )
    db.commit()
    return jsonify(ok=True)
