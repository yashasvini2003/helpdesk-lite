from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app import app
from database import init_database


class AppWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database = Path(self.temp_dir.name) / "web-test.db"
        app.config.update(TESTING=True, DATABASE=str(self.database))
        init_database(self.database)
        self.client = app.test_client()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_create_ticket_then_open_analytics_dashboard(self) -> None:
        response = self.client.post(
            "/tickets/new",
            data={
                "requester_name": "Yash",
                "contact_email": "yash@example.com",
                "device_type": "Laptop",
                "location": "Toronto",
                "category": "Access",
                "title": "Role access request",
                "description": "Access does not match the approved business role.",
                "priority": "High",
                "assigned_team": "Security Operations",
                "business_impact": "Single user",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Role access request", response.data)

        analytics_response = self.client.get("/analytics")
        self.assertEqual(analytics_response.status_code, 200)
        self.assertIn(b"Operational Analytics", analytics_response.data)


if __name__ == "__main__":
    unittest.main()
