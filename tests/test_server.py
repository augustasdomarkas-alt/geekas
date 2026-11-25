"""Run from server/: python -m unittest discover -s tests -v"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app


class NoticeboardTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.app = create_app(Path(self.temp_dir.name) / "test.db")
        self.client = self.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_health_and_list(self):
        self.assertEqual(self.client.get("/api/health").json, {"status": "ok"})
        self.assertEqual(len(self.client.get("/api/notices").json), 3)

    def test_create_and_get_one(self):
        response = self.client.post("/api/notices", json={
            "title": "Chess", "message": "Room 8, Friday", "category": "Events"
        })
        self.assertEqual(response.status_code, 201)
        item_id = response.json["id"]
        self.assertEqual(self.client.get(f"/api/notices/{item_id}").json["title"], "Chess")

    def test_missing_notice(self):
        self.assertEqual(self.client.get("/api/notices/99999").status_code, 404)

    def test_validation(self):
        self.assertEqual(self.client.post("/api/notices", json={"title": "", "message": "x"}).status_code, 400)
        self.assertEqual(self.client.post("/api/notices", data="hi").status_code, 415)

    def test_parameterized_sql(self):
        tricky_title = "X'); DROP TABLE notices; --"
        self.assertEqual(self.client.post("/api/notices", json={
            "title": tricky_title, "message": "Safe test"
        }).status_code, 201)
        self.assertIn(tricky_title, [row["title"] for row in self.client.get("/api/notices").json])


if __name__ == "__main__":
    unittest.main()
