"""Start the Trivora backend.

    python run.py                      (development)
    gunicorn run:app                   (production)
"""
import os

from server import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    print(f"\n  Trivora backend running on http://localhost:{port}")
    print("  Website : http://localhost:%d/        (when SERVE_FRONTEND=1)" % port)
    print("  Admin   : http://localhost:%d/admin/" % port)
    print("  API     : http://localhost:%d/api/health\n" % port)
    app.run(host=os.environ.get("HOST", "0.0.0.0"), port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
