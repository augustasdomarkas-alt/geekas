"""New tests for the halfway work. Original tests remain in test_server.py."""
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app


class HalfwayTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.database = Path(self.temp.name) / "test.db"
        self.app = create_app(self.database)
        self.client = self.app.test_client()

    def test_events_filter_excludes_other_categories(self):
        response = self.client.get("/api/notices?category=Events")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([row["title"] for row in response.json], ["Robotics club"])

    def test_unfiltered_list_keeps_all_categories_and_order(self):
        response = self.client.get("/api/notices")
        self.assertEqual(response.status_code, 200)
        self.assertEqual({r["category"] for r in response.json},
                         {"General", "Events", "Technology"})
        self.assertEqual([r["id"] for r in response.json], [3, 2, 1])

    def test_invalid_category_has_helpful_error(self):
        for category in ("", "events", "Unknown", "Events' OR 1=1 --"):
            with self.subTest(category=category):
                response = self.client.get("/api/notices", query_string={"category": category})
                self.assertEqual(response.status_code, 400)
                self.assertIn("General, Events or Technology", response.json["error"])

    def test_valid_category_with_no_matches_returns_empty_list(self):
        import sqlite3
        with closing(sqlite3.connect(self.database)) as connection, connection:
            connection.execute("DELETE FROM notices WHERE category = ?", ("Events",))
        response = self.client.get("/api/notices?category=Events")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

    def test_saved_notice_survives_new_app_instance(self):
        created = self.client.post("/api/notices", json={
            "title": "Chess club practice", "message": "Meet in Room 8 on Friday.",
            "category": "Events",
        })
        self.assertEqual(created.status_code, 201)
        restarted = create_app(self.database).test_client()
        response = restarted.get(f"/api/notices/{created.json['id']}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, created.json)

    def test_posted_notice_appears_in_webpage(self):
        self.client.post("/api/notices", json={
            "title": "Chess club practice", "message": "Meet in Room 8 on Friday."
        })
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Chess club practice", response.get_data(as_text=True))

    def test_malformed_json_returns_400(self):
        response = self.client.post("/api/notices", data="{broken",
                                    content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["error"], "JSON object required")


if __name__ == "__main__":
    unittest.main()
