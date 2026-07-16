"""Run the SLA escalation rule as a repeatable automation task."""

from __future__ import annotations

import argparse

from automation import escalate_sla_breaches
from database import connect_database, init_database


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Escalate active tickets that have exceeded their configured SLA."
    )
    parser.add_argument("--database", default="helpdesk.db")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    init_database(args.database)
    connection = connect_database(args.database)
    escalated_ids = escalate_sla_breaches(connection)
    connection.close()
    if escalated_ids:
        print("Escalated ticket IDs: " + ", ".join(map(str, escalated_ids)))
    else:
        print("No new SLA breaches required escalation.")


if __name__ == "__main__":
    main()
