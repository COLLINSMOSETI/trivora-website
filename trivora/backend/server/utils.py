"""Small helpers: input cleaning, user-agent parsing, CSV export."""
import csv
import io
import re

from flask import Response

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]{2,}$")
PHONE_RE = re.compile(r"^[0-9+\-()\s]{7,20}$")
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
_BOT_RE = re.compile(r"bot|crawl|spider|slurp|preview|monitor|curl|wget|python-requests|headless|lighthouse")


def clean(value, max_len):
    """Strip control characters and whitespace, and cap the length."""
    if value is None:
        return ""
    return _CONTROL_CHARS.sub("", str(value)).strip()[:max_len]


def parse_ua(ua):
    """Return (device, browser, os, is_bot) from a User-Agent string."""
    low = (ua or "").lower()
    is_bot = int(bool(_BOT_RE.search(low)))
    if "ipad" in low or "tablet" in low:
        device = "Tablet"
    elif "mobi" in low or "iphone" in low:
        device = "Mobile"
    else:
        device = "Desktop"

    browser = "Other"
    for name, token in (("Edge", "edg/"), ("Opera", "opr/"), ("Chrome", "chrome/"), ("Firefox", "firefox/"), ("Safari", "safari/")):
        if token in low:
            browser = name
            break

    os_name = "Other"
    for name, token in (("Android", "android"), ("iOS", "iphone"), ("iOS", "ipad"), ("Windows", "windows"), ("macOS", "mac os"), ("Linux", "linux")):
        if token in low:
            os_name = name
            break
    return device, browser, os_name, is_bot


def safe_cell(value):
    """Stop spreadsheet formula injection in CSV exports."""
    text = "" if value is None else str(value)
    return "'" + text if text[:1] in ("=", "+", "-", "@", "\t", "\r") else text


def csv_response(filename, header, rows):
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(header)
    for row in rows:
        writer.writerow([safe_cell(c) for c in row])
    return Response(
        "﻿" + buf.getvalue(),  # BOM so Excel reads UTF-8 correctly
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
