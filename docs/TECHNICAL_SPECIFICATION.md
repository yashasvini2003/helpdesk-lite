# Technical Specification

## 1. Purpose

HelpDesk Lite supports the intake, investigation, escalation, and reporting of operational technology issues. The solution demonstrates how business requirements can be translated into a small working system with documented rules, SQL-based analysis, audit history, and repeatable Python automation.

## 2. Stakeholders

| Stakeholder | Need |
|---|---|
| Requester | Record an issue and provide sufficient business context |
| Service desk analyst | Triage, investigate, update, and resolve work |
| Operational team | Receive correctly routed and escalated issues |
| Business manager | Understand issue volume, trends, SLA exposure, and data quality |
| Engineering/support team | Maintain a testable solution and clear technical artifacts |

## 3. Solution scope

### In scope

- Ticket intake and validation
- Priority-based SLA targets
- Assignment, escalation, investigation, root-cause, and resolution fields
- Status and change audit history
- Operational analytics using SQL
- Automated SLA-breach escalation using Python
- CSV and JSON report outputs for downstream analysis

### Out of scope

- Enterprise authentication and authorization
- Email, SMS, or paging integrations
- Production monitoring integrations
- Cloud hosting and high-availability infrastructure

## 4. Architecture and interfaces

| Layer | Technology | Responsibility |
|---|---|---|
| User interface | Flask templates, Bootstrap | Intake, investigation, filtering, and dashboards |
| Application | Python, Flask | Validation, workflow rules, routing, and report delivery |
| Analytics | Python, SQL | Aggregation, recurring-issue analysis, SLA risk, and data-quality checks |
| Data | SQLite | Ticket records, operational fields, and audit events |
| Automation | Python CLI | Scheduled analysis and SLA escalation |

Upstream inputs are ticket submissions and analyst updates. Downstream outputs are the analytics dashboard, an SLA-risk CSV, and a JSON operations report that can be consumed by reporting or visualization tools.

## 5. Business rules

| Rule | Definition |
|---|---|
| BR-01 | New tickets begin with `Open` status. |
| BR-02 | SLA targets are assigned by priority: Critical 8h, High 24h, Medium 48h, Low 72h. |
| BR-03 | A ticket is at risk after consuming 75% of its SLA target. |
| BR-04 | Active tickets exceeding their SLA can be automatically escalated. |
| BR-05 | Resolved or closed tickets record a resolution timestamp. Reopened tickets clear it. |
| BR-06 | Status, priority, assignment, escalation, and investigation updates are auditable. |
| BR-07 | SQL statements that include user input use parameter binding. |

## 6. Data model

### `tickets`

Stores requester information, issue context, workflow state, operational ownership, SLA configuration, investigation findings, resolution details, and timestamps.

### `ticket_history`

Stores an immutable sequence of ticket events. Each entry identifies the event type, previous and new values, an optional note, and the event timestamp.

The relationship is one ticket to many history events. Foreign-key enforcement and supporting indexes are enabled during connection and schema initialization.

## 7. SQL analysis

The analytics module uses:

- Conditional aggregation for active, escalated, and breached counts
- Date calculations for ticket age and mean resolution time
- A common table expression for category-level root-cause analysis
- A window function for category share of total volume
- `CASE` expressions to classify SLA risk
- Data-quality queries to identify missing investigation and resolution fields

## 8. Non-functional requirements

- **Maintainability:** schema, analytics, automation, and web concerns are separated into modules.
- **Auditability:** material workflow changes create history records.
- **Data integrity:** required fields, controlled workflow values, foreign keys, and parameterized queries are used.
- **Portability:** the solution uses Python, Flask, and SQLite with no external service dependency.
- **Testability:** analytics, escalation rules, ticket creation, and dashboard access have automated tests.
- **Usability:** responsive tables, clear filters, risk indicators, and export actions are available.

## 9. Release and rollback

Changes are validated with `python -m unittest discover -v` before release. Database initialization uses additive migrations for existing ticket databases. Application code can be rolled back independently; a database backup should be captured before releasing schema changes in a deployed environment.

## 10. Acceptance criteria

- A valid ticket can be created and assigned an SLA target.
- Analysts can update workflow, impact, ownership, escalation, root cause, and resolution information.
- The dashboard summarizes ticket volume, SLA breaches, recurring categories, and data-quality findings.
- The automation flags active SLA breaches and writes an audit event.
- Reports can be exported as CSV and JSON.
- Automated tests pass.
