"""Load deterministic sample incidents for dashboard demonstrations."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from database import connect_database, init_database


SAMPLE_TICKETS = (
    ("VPN access fails after password reset", "Network", "High", "Open", "Infrastructure", "Multiple users", 24, 36),
    ("Monthly report export times out", "Application", "Medium", "In Progress", "Application Support", "Department", 48, 42),
    ("Laptop docking station not detected", "Hardware", "Low", "Open", "Service Desk", "Single user", 72, 18),
    ("Intermittent authentication failures", "Access", "Critical", "Open", "Security Operations", "Enterprise", 8, 12),
    ("Printer queue remains offline", "Hardware", "Low", "Resolved", "Service Desk", "Multiple users", 72, 20),
    ("CRM search returns duplicate records", "Application", "High", "Resolved", "Application Support", "Department", 24, 16),
    ("Remote connection drops during calls", "Network", "Medium", "Closed", "Infrastructure", "Multiple users", 48, 30),
    ("Incorrect role assigned after transfer", "Access", "High", "In Progress", "Security Operations", "Single user", 24, 20),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed the database with demo tickets.")
    parser.add_argument("--database", default="helpdesk.db")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    init_database(args.database)
    connection = connect_database(args.database)
    if connection.execute("SELECT COUNT(*) FROM tickets").fetchone()[0] > 0:
        connection.close()
        print("Database already contains tickets; no sample data was added.")
        return

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    for index, sample in enumerate(SAMPLE_TICKETS, start=1):
        title, category, priority, status, team, impact, sla_hours, age_hours = sample
        created_at = now - timedelta(hours=age_hours)
        resolved_at = now - timedelta(hours=max(age_hours - 4, 1)) if status in ("Resolved", "Closed") else None
        connection.execute(
            """
            INSERT INTO tickets (
                requester_name, contact_email, device_type, location, category,
                title, description, priority, status, troubleshooting_notes,
                created_at, updated_at, assigned_team, business_impact,
                sla_target_hours, resolved_at, root_cause, resolution_summary
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"Demo User {index}",
                f"demo{index}@example.com",
                "Laptop",
                "Toronto",
                category,
                title,
                "Sample issue used to demonstrate investigation, SLA, and reporting workflows.",
                priority,
                status,
                "Initial triage completed.",
                created_at.isoformat(" "),
                now.isoformat(" "),
                team,
                impact,
                sla_hours,
                resolved_at.isoformat(" ") if resolved_at else None,
                "Configuration or process variance" if resolved_at else None,
                "Validated and restored expected service" if resolved_at else None,
            ),
        )
    connection.commit()
    connection.close()
    print(f"Added {len(SAMPLE_TICKETS)} demo tickets.")


if __name__ == "__main__":
    main()
