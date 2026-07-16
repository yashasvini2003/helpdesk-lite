"""SQL-driven operational analytics used by the web dashboard and CLI reports."""

from __future__ import annotations

import sqlite3
from typing import Any


ACTIVE_STATUSES = ("Open", "In Progress")


def _rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]


def get_summary_metrics(connection: sqlite3.Connection) -> dict[str, Any]:
    """Return portfolio-level service metrics using conditional SQL aggregation."""
    row = connection.execute(
        """
        SELECT
            COUNT(*) AS total_tickets,
            SUM(CASE WHEN status IN ('Open', 'In Progress') THEN 1 ELSE 0 END)
                AS active_tickets,
            SUM(CASE WHEN escalated = 1 THEN 1 ELSE 0 END) AS escalated_tickets,
            SUM(
                CASE
                    WHEN status IN ('Open', 'In Progress')
                     AND (julianday('now') - julianday(created_at)) * 24
                         > sla_target_hours
                    THEN 1 ELSE 0
                END
            ) AS sla_breaches,
            ROUND(
                AVG(
                    CASE
                        WHEN resolved_at IS NOT NULL
                        THEN (julianday(resolved_at) - julianday(created_at)) * 24
                    END
                ),
                2
            ) AS average_resolution_hours
        FROM tickets
        """
    ).fetchone()
    metrics = dict(row)
    return {key: (0 if value is None else value) for key, value in metrics.items()}


def get_root_cause_summary(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    """Rank recurring categories to support root-cause investigation."""
    rows = connection.execute(
        """
        WITH category_metrics AS (
            SELECT
                COALESCE(NULLIF(TRIM(category), ''), 'Uncategorized') AS category,
                COUNT(*) AS ticket_count,
                SUM(CASE WHEN status IN ('Open', 'In Progress') THEN 1 ELSE 0 END)
                    AS active_count,
                SUM(CASE WHEN escalated = 1 THEN 1 ELSE 0 END)
                    AS escalated_count,
                ROUND(
                    AVG((julianday(updated_at) - julianday(created_at)) * 24),
                    2
                ) AS average_age_hours
            FROM tickets
            GROUP BY COALESCE(NULLIF(TRIM(category), ''), 'Uncategorized')
        )
        SELECT
            category,
            ticket_count,
            active_count,
            escalated_count,
            average_age_hours,
            ROUND(ticket_count * 100.0 / SUM(ticket_count) OVER (), 1)
                AS share_percent
        FROM category_metrics
        ORDER BY ticket_count DESC, category ASC
        LIMIT 10
        """
    ).fetchall()
    return _rows_to_dicts(rows)


def get_sla_risk_tickets(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    """Identify active tickets that have consumed at least 75% of their SLA."""
    rows = connection.execute(
        """
        SELECT
            id,
            title,
            priority,
            status,
            assigned_team,
            business_impact,
            sla_target_hours,
            ROUND((julianday('now') - julianday(created_at)) * 24, 1)
                AS age_hours,
            ROUND(
                ((julianday('now') - julianday(created_at)) * 24)
                / NULLIF(sla_target_hours, 0) * 100,
                1
            ) AS sla_consumed_percent,
            CASE
                WHEN escalated = 1 THEN 'Escalated'
                WHEN (julianday('now') - julianday(created_at)) * 24
                     > sla_target_hours THEN 'Breached'
                ELSE 'At risk'
            END AS risk_status
        FROM tickets
        WHERE status IN ('Open', 'In Progress')
          AND (
                escalated = 1
                OR (julianday('now') - julianday(created_at)) * 24
                   >= sla_target_hours * 0.75
              )
        ORDER BY
            CASE risk_status
                WHEN 'Breached' THEN 1
                WHEN 'Escalated' THEN 2
                ELSE 3
            END,
            sla_consumed_percent DESC
        """
    ).fetchall()
    return _rows_to_dicts(rows)


def get_data_quality_findings(connection: sqlite3.Connection) -> dict[str, int]:
    """Measure missing fields that could block investigation or reporting."""
    row = connection.execute(
        """
        SELECT
            SUM(CASE WHEN category IS NULL OR TRIM(category) = '' THEN 1 ELSE 0 END)
                AS missing_category,
            SUM(CASE WHEN location IS NULL OR TRIM(location) = '' THEN 1 ELSE 0 END)
                AS missing_location,
            SUM(
                CASE
                    WHEN status IN ('Resolved', 'Closed')
                     AND (resolution_summary IS NULL OR TRIM(resolution_summary) = '')
                    THEN 1 ELSE 0
                END
            ) AS missing_resolution,
            SUM(
                CASE
                    WHEN status IN ('Resolved', 'Closed')
                     AND (root_cause IS NULL OR TRIM(root_cause) = '')
                    THEN 1 ELSE 0
                END
            ) AS missing_root_cause
        FROM tickets
        """
    ).fetchone()
    findings = dict(row)
    return {key: (0 if value is None else value) for key, value in findings.items()}


def build_analysis(connection: sqlite3.Connection) -> dict[str, Any]:
    """Build the complete analysis payload shared by UI and automation scripts."""
    return {
        "summary": get_summary_metrics(connection),
        "root_causes": get_root_cause_summary(connection),
        "sla_risks": get_sla_risk_tickets(connection),
        "data_quality": get_data_quality_findings(connection),
    }
