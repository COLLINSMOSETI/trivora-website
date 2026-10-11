"""Optional: serve the ../frontend folder from this backend.

This only exists so `python run.py` starts everything with one command.
With SERVE_FRONTEND=0 the backend is a pure API and the frontend can live on any host.
"""
import os

from flask import Blueprint, abort, redirect, send_from_directory
from werkzeug.security import safe_join

from .. import config

bp = Blueprint("frontend", __name__)


@bp.get("/", defaults={"path": ""})
@bp.get("/<path:path>")
def serve(path):
    if path == "api" or path.startswith("api/"):
        abort(404)
    full = safe_join(config.FRONTEND_DIR, path)
    if full is None:
        abort(404)
    if os.path.isdir(full):
        if path and not path.endswith("/"):
            return redirect("/" + path + "/")  # /admin -> /admin/ so relative links work
        path = os.path.join(path, "index.html")
    response = send_from_directory(config.FRONTEND_DIR, path)
    if path.endswith(".html"):
        response.headers["Cache-Control"] = "no-cache"
    return response
