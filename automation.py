"""Operational automation for ticket escalation and audit history."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone


def escalate_sla_breaches(connection: sqlite3.Connection) -> list[int]:
    """Escalate active tickets that exceeded their SLA and return affected IDs."""
    breached_rows = connection.execute(
        """
        SELECT id
        FROM tickets
        WHERE status IN ('Open', 'In Progress')
          AND escalated = 0
          AND (julianday('now') - julianday(created_at)) * 24 > sla_target_hours
        ORDER BY id
        """
    ).fetchall()
    ticket_ids = [row["id"] for row in breached_rows]
    if not ticket_ids:
        return []

    now = datetime.now(timezone.utc).replace(tzinfo=None).isoformat(" ")
    placeholders = ",".join("?" for _ in ticket_ids)
    connection.execute(
        f"""
        UPDATE tickets
        SET escalated = 1, updated_at = ?
        WHERE id IN ({placeholders})
        """,
        (now, *ticket_ids),
    )
    connection.executemany(
        """
        INSERT INTO ticket_history (
            ticket_id, event_type, old_value, new_value, note, created_at
        )
        VALUES (?, 'SLA escalation', 'Not escalated', 'Escalated', ?, ?)
        """,
        [
            (
                ticket_id,
                "Automatically escalated after the configured SLA was exceeded.",
                now,
            )
            for ticket_id in ticket_ids
        ],
    )
    connection.commit()
    return ticket_ids
