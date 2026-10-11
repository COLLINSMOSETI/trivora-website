"""SQLite connection handling, schema set-up and first admin account."""
import os
import secrets
import sqlite3

from flask import g
from werkzeug.security import generate_password_hash

from . import config

SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")


def connect():
    """Open a new connection (used directly by background threads)."""
    conn = sqlite3.connect(config.DB_PATH, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_db():
    """Per-request connection."""
    if "db" not in g:
        g.db = connect()
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)
    conn = connect()
    try:
        conn.execute("PRAGMA journal_mode = WAL")
        with open(SCHEMA_PATH, encoding="utf-8") as fh:
            conn.executescript(fh.read())
        ensure_admin(conn)
    finally:
        conn.close()


def ensure_admin(conn):
    """Create the first admin account if none exists."""
    if conn.execute("SELECT COUNT(*) FROM admins").fetchone()[0]:
        return
    username = os.environ.get("ADMIN_USERNAME", "admin")
    password = os.environ.get("ADMIN_PASSWORD")
    generated = False
    if not password:
        password = secrets.token_urlsafe(12)
        generated = True
    try:
        conn.execute(
            "INSERT INTO admins (username, password_hash) VALUES (?, ?)",
            (username, generate_password_hash(password)),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return  # another worker created it first
    if generated:
        print("\n" + "=" * 62)
        print(" TRIVORA ADMIN ACCOUNT CREATED (shown once - save it!)")
        print(f"   Username : {username}")
        print(f"   Password : {password}")
        print(" Sign in at /admin/ and change it under Settings.")
        print("=" * 62 + "\n", flush=True)
    else:
        print(f"Admin account '{username}' created from ADMIN_PASSWORD.", flush=True)


def init_app(app):
    app.teardown_appcontext(close_db)
    init_db()
