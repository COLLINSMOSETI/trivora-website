"""Admin dashboard API (every route needs a valid admin token)."""
from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify, request

from .. import config
from ..database import get_db
from ..security import admin_required
from ..utils import clean, csv_response

bp = Blueprint("admin", __name__, url_prefix="/api/admin")


def _nairobi_today():
    return (datetime.now(timezone.utc) + timedelta(hours=3)).date()


@bp.get("/stats")
@admin_required
def stats():
    db = get_db()
    today = _nairobi_today().isoformat()

    def one(sql, *args):
        return db.execute(sql, args).fetchone()[0]

    totals = {
        "enquiries_total": one("SELECT COUNT(*) FROM enquiries"),
        "enquiries_new": one("SELECT COUNT(*) FROM enquiries WHERE status = 'new'"),
        "enquiries_today": one("SELECT COUNT(*) FROM enquiries WHERE date(created_at,'+3 hours') = ?", today),
        "visits_total": one("SELECT COUNT(*) FROM visitors WHERE is_bot = 0"),
        "visits_today": one("SELECT COUNT(*) FROM visitors WHERE is_bot = 0 AND date(created_at,'+3 hours') = ?", today),
        "unique_visitors": one("SELECT COUNT(DISTINCT ip) FROM visitors WHERE is_bot = 0"),
    }

    days = [(_nairobi_today() - timedelta(days=i)).isoformat() for i in range(13, -1, -1)]
    visit_rows = dict(
        db.execute(
            "SELECT date(created_at,'+3 hours') d, COUNT(*) FROM visitors "
            "WHERE is_bot = 0 AND date(created_at,'+3 hours') >= ? GROUP BY d",
            (days[0],),
        ).fetchall()
    )
    enquiry_rows = dict(
        db.execute(
            "SELECT date(created_at,'+3 hours') d, COUNT(*) FROM enquiries "
            "WHERE date(created_at,'+3 hours') >= ? GROUP BY d",
            (days[0],),
        ).fetchall()
    )
    series = [{"date": d, "visits": visit_rows.get(d, 0), "enquiries": enquiry_rows.get(d, 0)} for d in days]

    by_service = [
        {"service": r[0], "count": r[1]}
        for r in db.execute("SELECT service, COUNT(*) FROM enquiries GROUP BY service ORDER BY COUNT(*) DESC")
    ]
    by_device = [
        {"device": r[0] or "Unknown", "count": r[1]}
        for r in db.execute(
            "SELECT device, COUNT(*) FROM visitors WHERE is_bot = 0 GROUP BY device ORDER BY COUNT(*) DESC"
        )
    ]
    return jsonify(ok=True, stats=totals, series=series, by_service=by_service, by_device=by_device)


@bp.get("/enquiries")
@admin_required
def list_enquiries():
    status = clean(request.args.get("status"), 20)
    q = clean(request.args.get("q"), 100)
    try:
        limit = max(1, min(int(request.args.get("limit", 200)), 500))
        offset = max(0, int(request.args.get("offset", 0)))
    except ValueError:
        limit, offset = 200, 0

    where, args = [], []
    if status in config.STATUSES:
        where.append("status = ?")
        args.append(status)
    if q:
        like = f"%{q}%"
        where.append("(name LIKE ? OR email LIKE ? OR phone LIKE ? OR message LIKE ?)")
        args += [like, like, like, like]
    clause = ("WHERE " + " AND ".join(where)) if where else ""

    db = get_db()
    total = db.execute(f"SELECT COUNT(*) FROM enquiries {clause}", args).fetchone()[0]
    rows = db.execute(
        f"SELECT * FROM enquiries {clause} ORDER BY id DESC LIMIT ? OFFSET ?", args + [limit, offset]
    ).fetchall()
    return jsonify(ok=True, total=total, items=[dict(r) for r in rows])


@bp.patch("/enquiries/<int:enquiry_id>")
@admin_required
def update_enquiry(enquiry_id):
    data = request.get_json(silent=True) or {}
    fields, args = [], []
    if "status" in data:
        status = clean(data["status"], 20)
        if status not in config.STATUSES:
            return jsonify(ok=False, error="Invalid status."), 400
        fields.append("status = ?")
        args.append(status)
    if "notes" in data:
        fields.append("notes = ?")
        args.append(clean(data["notes"], 2000))
    if not fields:
        return jsonify(ok=False, error="Nothing to update."), 400

    db = get_db()
    cur = db.execute(f"UPDATE enquiries SET {', '.join(fields)} WHERE id = ?", args + [enquiry_id])
    db.commit()
    if cur.rowcount == 0:
        return jsonify(ok=False, error="Enquiry not found."), 404
    return jsonify(ok=True)


@bp.delete("/enquiries/<int:enquiry_id>")
@admin_required
def delete_enquiry(enquiry_id):
    db = get_db()
    cur = db.execute("DELETE FROM enquiries WHERE id = ?", (enquiry_id,))
    db.commit()
    if cur.rowcount == 0:
        return jsonify(ok=False, error="Enquiry not found."), 404
    return jsonify(ok=True)


@bp.get("/visitors")
@admin_required
def list_visitors():
    show_bots = request.args.get("bots") == "1"
    try:
        limit = max(1, min(int(request.args.get("limit", 100)), 500))
        offset = max(0, int(request.args.get("offset", 0)))
    except ValueError:
        limit, offset = 100, 0
    clause = "" if show_bots else "WHERE is_bot = 0"

    db = get_db()
    total = db.execute(f"SELECT COUNT(*) FROM visitors {clause}").fetchone()[0]
    rows = db.execute(
        f"SELECT id, ip, path, referrer, device, browser, os, is_bot, created_at FROM visitors {clause} "
        "ORDER BY id DESC LIMIT ? OFFSET ?",
        (limit, offset),
    ).fetchall()
    return jsonify(ok=True, total=total, items=[dict(r) for r in rows])


@bp.get("/export/enquiries.csv")
@admin_required
def export_enquiries():
    rows = get_db().execute(
        "SELECT id, created_at, name, email, phone, service, budget, status, message, notes "
        "FROM enquiries ORDER BY id DESC"
    ).fetchall()
    return csv_response(
        "trivora-enquiries.csv",
        ["ID", "Received (UTC)", "Name", "Email", "Phone", "Service", "Budget", "Status", "Message", "Notes"],
        [tuple(r) for r in rows],
    )


@bp.get("/export/visitors.csv")
@admin_required
def export_visitors():
    rows = get_db().execute(
        "SELECT id, created_at, ip, path, referrer, device, browser, os FROM visitors WHERE is_bot = 0 ORDER BY id DESC"
    ).fetchall()
    return csv_response(
        "trivora-visitors.csv",
        ["ID", "Time (UTC)", "IP", "Page", "Referrer", "Device", "Browser", "OS"],
        [tuple(r) for r in rows],
    )
