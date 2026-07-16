from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from analytics import build_analysis
from automation import escalate_sla_breaches
from database import connect_database, init_database


class AnalyticsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database = Path(self.temp_dir.name) / "test.db"
        init_database(self.database)
        self.connection = connect_database(self.database)
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        rows = [
            ("VPN unavailable", "Network", "High", "Open", 24, now - timedelta(hours=30), None),
            ("Wi-Fi unstable", "Network", "Medium", "In Progress", 48, now - timedelta(hours=40), None),
            ("App error", "Application", "High", "Resolved", 24, now - timedelta(hours=10), now - timedelta(hours=2)),
        ]
        self.connection.executemany(
            """
            INSERT INTO tickets (
                requester_name, contact_email, device_type, title, description,
                category, priority, status, created_at, updated_at,
                sla_target_hours, resolved_at
            )
            VALUES ('Test User', 'test@example.com', 'Laptop', ?, 'Test', ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    title,
                    category,
                    priority,
                    status,
                    created.isoformat(" "),
                    (resolved or now).isoformat(" "),
                    sla,
                    resolved.isoformat(" ") if resolved else None,
                )
                for title, category, priority, status, sla, created, resolved in rows
            ],
        )
        self.connection.commit()

    def tearDown(self) -> None:
        self.connection.close()
        self.temp_dir.cleanup()

    def test_analysis_returns_summary_root_causes_and_sla_risk(self) -> None:
        analysis = build_analysis(self.connection)
        self.assertEqual(analysis["summary"]["total_tickets"], 3)
        self.assertEqual(analysis["summary"]["active_tickets"], 2)
        self.assertEqual(analysis["summary"]["sla_breaches"], 1)
        self.assertEqual(analysis["root_causes"][0]["category"], "Network")
        self.assertEqual(len(analysis["sla_risks"]), 2)

    def test_automation_escalates_only_breached_active_ticket(self) -> None:
        escalated_ids = escalate_sla_breaches(self.connection)
        self.assertEqual(len(escalated_ids), 1)
        ticket = self.connection.execute(
            "SELECT escalated FROM tickets WHERE id = ?", (escalated_ids[0],)
        ).fetchone()
        self.assertEqual(ticket["escalated"], 1)
        history_count = self.connection.execute(
            "SELECT COUNT(*) FROM ticket_history WHERE event_type = 'SLA escalation'"
        ).fetchone()[0]
        self.assertEqual(history_count, 1)


if __name__ == "__main__":
    unittest.main()
