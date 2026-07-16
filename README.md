# HelpDesk Lite — Technical Operations Analytics

HelpDesk Lite is a self-directed Python and SQL project that translates operational support requirements into a working ticket, investigation, escalation, and reporting workflow. It combines a Flask application with SQLite analytics, repeatable Python automation, technical specifications, use cases, process models, requirements traceability, and automated tests.

## Business problem

Operational teams need more than a list of tickets. They need consistent intake data, clear ownership, SLA visibility, documented investigation findings, audit history, and concise reporting that helps stakeholders understand where attention is required.

This project demonstrates that business-to-technology translation through:

- Structured issue intake and validation
- Priority, impact, assignment, and escalation workflows
- Root-cause and resolution documentation
- SQL analysis of recurring issues, SLA exposure, resolution time, and data quality
- Python automation for SLA triage and JSON reporting
- CSV output for downstream reporting tools
- Technical specifications, use cases, process diagrams, and a traceability matrix
- Automated tests and GitHub Actions validation

## Technology

- **Python 3.12** — application logic, automation, report generation, and testing
- **Flask** — web routes and user workflows
- **SQLite / SQL** — persistence, aggregation, CTEs, window functions, and risk queries
- **Bootstrap / Jinja** — responsive user interface
- **GitHub Actions** — automated validation during release changes

## Core workflow

1. Record a request with business and technical context.
2. Assign priority, impact, ownership, and a priority-based SLA.
3. Investigate, document findings, and track auditable changes.
4. Escalate tickets manually or through the Python SLA automation.
5. Record root cause, resolution, and related change references.
6. Review operational trends and export reports for stakeholders.

## Analytics and scripting

`analytics.py` runs SQL queries that calculate:

- Total, active, escalated, and SLA-breached ticket counts
- Average resolution time
- Recurring issue categories and their share of total volume
- Tickets that consumed at least 75% of their SLA
- Missing category, location, root-cause, and resolution information

Generate a JSON report:

```bash
python -m scripts.analyze_tickets --database helpdesk.db
```

Run automated SLA triage:

```bash
python -m scripts.triage_sla --database helpdesk.db
```

Load deterministic demonstration data into an empty database:

```bash
python -m scripts.seed_demo_data --database helpdesk.db
```

## Run locally

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

macOS or Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

## Test

```bash
python -m unittest discover -v
python -m compileall -q .
```

## Technical artifacts

- [Technical specification](docs/TECHNICAL_SPECIFICATION.md)
- [Use cases and process model](docs/USE_CASES_AND_PROCESS.md)
- [Requirements traceability](docs/REQUIREMENTS_TRACEABILITY.md)
- [Release notes](docs/RELEASE_NOTES.md)

## Scope note

This is a portfolio demonstration, not a deployed enterprise service. Authentication, notifications, production monitoring integrations, and high-availability infrastructure are intentionally outside its current scope.
