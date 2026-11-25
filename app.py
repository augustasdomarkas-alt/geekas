"""SL noticeboard: starter server with category filtering; native Android client is in ../android.

Read START_HERE.md in the parent folder for setup and a beginner explanation.
The database, website, POST endpoint and validation were supplied in the kit.
The new behaviour is labelled NEW FEATURE below. A small Windows database
cleanup fix is labelled BUG FIX; other additions are explanatory comments.
"""
import os
import sqlite3
from contextlib import closing
from pathlib import Path

from flask import Flask, g, jsonify, render_template_string, request

DATABASE = Path(os.environ.get("NOTICEBOARD_DB", Path(__file__).with_name("notices.db")))
ALLOWED_CATEGORIES = {"General", "Events", "Technology"}


def create_app(database=None):
    # A factory builds the app. Tests can supply a separate temporary database.
    app = Flask(__name__)
    app.config.update(DATABASE=str(database or DATABASE), MAX_CONTENT_LENGTH=4096)

    def db():
        # Reuse one connection during this request. Row lets us use column names.
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(_exc):
        # Close the connection after Flask has finished the request.
        connection = g.pop("db", None)
        if connection is not None:
            connection.close()

    with app.app_context():
        # Keep the table if it already exists. Insert example rows only if empty.
        # BUG FIX: SQLite's own 'with' saves changes but does not close the file.
        # closing() releases it reliably, avoiding locked files on Windows.
        with closing(sqlite3.connect(app.config["DATABASE"])) as connection, connection:
            connection.execute("""CREATE TABLE IF NOT EXISTS notices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                category TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )""")
            if connection.execute("SELECT COUNT(*) FROM notices").fetchone()[0] == 0:
                connection.executemany(
                    "INSERT INTO notices (title, message, category) VALUES (?, ?, ?)",
                    [
                        ("Library hours", "The library opens at 08:00.", "General"),
                        ("Robotics club", "Meet in Lab 2 on Thursday.", "Events"),
                        ("Python workshop", "Bring your laptop and Android phone.", "Technology"),
                    ],
                )

    def as_dict(row):
        return dict(row)

    @app.get("/api/health")
    def health():
        return jsonify(status="ok")

    @app.get("/api/notices")
    def list_notices():
        # NEW FEATURE (task B): read the optional part after ? in the URL.
        # Example: /api/notices?category=Events
        category = request.args.get("category")
        if category is None:
            # No filter: keep the original behaviour, newest ID first.
            rows = db().execute("SELECT * FROM notices ORDER BY id DESC").fetchall()
        else:
            # Names are case-sensitive; an empty or unknown category is an error.
            if category not in ALLOWED_CATEGORIES:
                return jsonify(error="Category must be General, Events or Technology."), 400
            # The ? is a value placeholder, not string concatenation.
            # (category,) is a tuple containing ONE value; the comma matters.
            rows = db().execute(
                "SELECT * FROM notices WHERE category = ? ORDER BY id DESC",
                (category,),
            ).fetchall()
        # Convert each database row to a dictionary, then return a JSON list.
        return jsonify([as_dict(row) for row in rows])

    @app.get("/api/notices/<int:item_id>")
    def get_notice(item_id):
        row = db().execute("SELECT * FROM notices WHERE id = ?", (item_id,)).fetchone()
        if row is None:
            return jsonify(error="Notice not found"), 404
        return jsonify(as_dict(row))

    @app.post("/api/notices")
    def create_notice():
        # Reject the wrong body format, then check field types and lengths.
        if not request.is_json:
            return jsonify(error="Send application/json"), 415
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify(error="JSON object required"), 400
        title = data.get("title")
        message = data.get("message")
        category = data.get("category", "General")
        if not isinstance(title, str) or not 1 <= len(title.strip()) <= 80:
            return jsonify(error="Title is required (1–80 characters)."), 400
        if not isinstance(message, str) or not 1 <= len(message.strip()) <= 500:
            return jsonify(error="Message is required (1–500 characters)."), 400
        if not isinstance(category, str) or category not in ALLOWED_CATEGORIES:
            return jsonify(error="Invalid category"), 400
        with db() as connection:
            # A successful 'with' block commits (saves) the INSERT to disk.
            cursor = connection.execute(
                "INSERT INTO notices (title, message, category) VALUES (?, ?, ?)",
                (title.strip(), message.strip(), category),
            )
        row = db().execute("SELECT * FROM notices WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return jsonify(as_dict(row)), 201

    @app.get("/")
    def home():
        # Same database as the API, but return HTML for a browser, not JSON.
        rows = db().execute("SELECT * FROM notices ORDER BY id DESC").fetchall()
        return render_template_string("""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>School Noticeboard</title><style>
body{font:16px system-ui,sans-serif;background:#f1f5f9;color:#0f172a;max-width:760px;margin:36px auto;padding:0 18px}
article{background:white;border:1px solid #cbd5e1;border-radius:12px;margin:12px 0;padding:18px}
small{color:#475569}h1{margin-bottom:4px}p{line-height:1.5}
</style></head><body><h1>Our Classroom News</h1><p>Powered by Python + SQLite. <a href="/api/notices">View JSON</a></p>
{% for item in notices %}<article><small>{{ item['category'] }} · #{{ item['id'] }} · {{ item['created_at'] }} UTC</small>
<h2>{{ item['title'] }}</h2><p>{{ item['message'] }}</p></article>{% endfor %}
</body></html>""", notices=rows)

    return app


app = create_app()

if __name__ == "__main__":
    # Lab-only: accessible over a trusted classroom LAN, with debugger OFF.
    app.run(host="0.0.0.0", port=5000, debug=False)
