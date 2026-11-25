"""Run after starting server once: python helpers/look_inside_db.py"""
import sqlite3
from pathlib import Path

db_path = Path(__file__).resolve().parents[1] / "notices.db"
if not db_path.exists():
    print("No database yet. Start app.py once, stop it, then retry.")
    raise SystemExit(1)

with sqlite3.connect(db_path) as connection:
    connection.row_factory = sqlite3.Row
    rows = connection.execute(
        "SELECT id, title, category, created_at FROM notices ORDER BY id"
    ).fetchall()
    print("Database:", db_path)
    print("Rows found:", len(rows))
    for row in rows:
        print(f"#{row['id']}: {row['title']} ({row['category']}) - {row['created_at']}")

    print("\nCount per category:")
    for category, count in connection.execute(
        "SELECT category, COUNT(*) FROM notices GROUP BY category ORDER BY category"
    ):
        print(f"  {category}: {count}")
