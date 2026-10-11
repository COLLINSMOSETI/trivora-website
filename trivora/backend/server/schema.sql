-- Trivora database schema (SQLite). Applied automatically every time the backend starts.

CREATE TABLE IF NOT EXISTS admins (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Everyone who filled in the contact form
CREATE TABLE IF NOT EXISTS enquiries (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL,
    email      TEXT NOT NULL,
    phone      TEXT,
    service    TEXT NOT NULL,
    budget     TEXT,
    message    TEXT NOT NULL,
    status     TEXT NOT NULL DEFAULT 'new',
    notes      TEXT,
    ip         TEXT,
    notified   INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_enquiries_status  ON enquiries(status);
CREATE INDEX IF NOT EXISTS idx_enquiries_created ON enquiries(created_at);

-- Everyone who opened the website
CREATE TABLE IF NOT EXISTS visitors (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    ip         TEXT,
    path       TEXT,
    referrer   TEXT,
    user_agent TEXT,
    device     TEXT,
    browser    TEXT,
    os         TEXT,
    is_bot     INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_visitors_created ON visitors(created_at);
