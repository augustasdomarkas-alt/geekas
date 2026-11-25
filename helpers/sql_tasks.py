"""Completed lesson 04 SQL exercises, with short explanations."""
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "notices.db"
if not DB.exists():
    raise SystemExit("Run app.py once to create notices.db first.")

with sqlite3.connect(DB) as connection:
    print("TASK 1: Show all notice titles:")
    for row in connection.execute("SELECT title FROM notices ORDER BY id"):
        print(" -", row[0])

    print("\nTASK 2: Show only Technology notices:")
    # WHERE keeps only rows whose category equals the supplied value.
    for row in connection.execute(
        "SELECT title, category FROM notices WHERE category = ?", ("Technology",)
    ):
        print(" -", row)

    print("\nTASK 3: Count all notices:")
    # COUNT(*) returns one row with one number. [0] extracts that number.
    count = connection.execute("SELECT COUNT(*) FROM notices").fetchone()[0]
    print("Total notices:", count)

    print("\nTASK 4 (challenge): Print the title of the newest notice:")
    # Highest auto-generated ID = most recently inserted notice in this demo.
    # LIMIT 1 asks for only one row. An empty table returns None.
    newest = connection.execute(
        "SELECT title FROM notices ORDER BY id DESC LIMIT 1"
    ).fetchone()
    print(newest[0] if newest else "No notices yet.")
