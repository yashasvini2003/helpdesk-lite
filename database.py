"""Database schema and migration helpers for HelpDesk Lite."""

from __future__ import annotations

import sqlite3
from pathlib import Path


TICKET_COLUMNS = {
    "assigned_team": "TEXT NOT NULL DEFAULT 'Service Desk'",
    "business_impact": "TEXT NOT NULL DEFAULT 'Single user'",
    "sla_target_hours": "INTEGER NOT NULL DEFAULT 48",
    "escalated": "INTEGER NOT NULL DEFAULT 0",
    "resolved_at": "TEXT",
    "root_cause": "TEXT",
    "resolution_summary": "TEXT",
    "change_reference": "TEXT",
}


def connect_database(database_path: str | Path) -> sqlite3.Connection:
    """Open a SQLite connection configured for named-column access."""
    connection = sqlite3.connect(str(database_path))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_database(database_path: str | Path) -> None:
    """Create the schema and apply backward-compatible column migrations."""
    connection = connect_database(database_path)
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            requester_name TEXT NOT NULL,
            contact_email TEXT NOT NULL,
            device_type TEXT NOT NULL,
            location TEXT,
            category TEXT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL,
            troubleshooting_notes TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            assigned_team TEXT NOT NULL DEFAULT 'Service Desk',
            business_impact TEXT NOT NULL DEFAULT 'Single user',
            sla_target_hours INTEGER NOT NULL DEFAULT 48,
            escalated INTEGER NOT NULL DEFAULT 0,
            resolved_at TEXT,
            root_cause TEXT,
            resolution_summary TEXT,
            change_reference TEXT
        )
        """
    )

    existing_columns = {
        row["name"] for row in connection.execute("PRAGMA table_info(tickets)")
    }
    for column_name, definition in TICKET_COLUMNS.items():
        if column_name not in existing_columns:
            connection.execute(
                f"ALTER TABLE tickets ADD COLUMN {column_name} {definition}"
            )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS ticket_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            old_value TEXT,
            new_value TEXT,
            note TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
        )
        """
    )
    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status)"
    )
    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_tickets_priority ON tickets(priority)"
    )
    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_history_ticket ON ticket_history(ticket_id)"
    )
    connection.commit()
    connection.close()
