"""Trivora backend application factory."""
from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

from . import config, database
from .routes import admin, auth, frontend, public
from .security import init_security


def create_app():
    app = Flask(__name__, static_folder=None)
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = 64 * 1024
    app.json.sort_keys = False

    database.init_app(app)  # creates tables + first admin
    init_security(app)  # CORS + security headers

    app.register_blueprint(public.bp)  # /api/contact, /api/track, /api/health
    app.register_blueprint(auth.bp)  # /api/admin/login, /me, /password
    app.register_blueprint(admin.bp)  # /api/admin/stats, /enquiries, /visitors, /export/*
    if config.SERVE_FRONTEND:
        app.register_blueprint(frontend.bp)  # serves ../frontend (must be registered last)

    @app.errorhandler(HTTPException)
    def api_errors(err):
        if request.path.startswith("/api/"):
            return jsonify(ok=False, error=err.description or err.name), err.code
        return err

    return app
