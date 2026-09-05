import unittest
from fastapi.testclient import TestClient

from app.main import app


class TestSchemesAPI(unittest.TestCase):
    """Integration and route tests for GET /api/schemes and GET /api/schemes/{slug}."""

    def setUp(self):
        self.client = TestClient(app)

    def test_list_all_schemes(self):
        """Verify GET /api/schemes returns 200 with all 53 curated schemes."""
        response = self.client.get("/api/schemes")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_schemes", data)
        self.assertEqual(data["total_schemes"], 53)
        self.assertIn("categories", data)
        self.assertEqual(len(data["schemes"]), 53)

        # Check required fields on first scheme
        first = data["schemes"][0]
        self.assertIn("slug", first)
        self.assertIn("name", first)
        self.assertIn("category", first)
        self.assertIn("summary", first)
        self.assertIn("image", first)
        self.assertIn("source", first)

    def test_list_schemes_filtered_by_category(self):
        """Verify GET /api/schemes?category=Students filters appropriately."""
        response = self.client.get("/api/schemes?category=Students")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreater(data["total_schemes"], 0)
        for s in data["schemes"]:
            self.assertEqual(s["category"], "Students")

    def test_get_scheme_by_valid_slug(self):
        """Verify GET /api/schemes/pm-kisan returns PM-KISAN details."""
        response = self.client.get("/api/schemes/pm-kisan")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["slug"], "pm-kisan")
        self.assertIn("PM-KISAN", data["name"])
        self.assertEqual(data["category"], "Farmers")
        self.assertGreater(len(data["benefits"]), 0)
        self.assertGreater(len(data["documents"]), 0)

    def test_get_scheme_by_invalid_slug(self):
        """Verify GET /api/schemes/non-existent returns 404."""
        response = self.client.get("/api/schemes/non-existent-scheme-slug-12345")
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("detail", data)


if __name__ == "__main__":
    unittest.main()
