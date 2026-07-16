"""Generate a reusable JSON operations report from the ticket database."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from analytics import build_analysis
from database import connect_database, init_database


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run SQL-based ticket analysis and export the findings as JSON."
    )
    parser.add_argument(
        "--database",
        default="helpdesk.db",
        help="Path to the SQLite database (default: helpdesk.db).",
    )
    parser.add_argument(
        "--output",
        default="reports/operations-analysis.json",
        help="Destination JSON report path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    init_database(args.database)
    connection = connect_database(args.database)
    analysis = build_analysis(connection)
    connection.close()

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_database": str(Path(args.database)),
        **analysis,
    }
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Analysis written to {output_path}")


if __name__ == "__main__":
    main()
