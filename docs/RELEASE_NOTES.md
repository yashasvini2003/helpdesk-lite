# Release Notes

## Version 2.0 — Technical Business Analysis and Operations Analytics

### Added

- Priority-based SLA targets and automated breach escalation
- Operational assignment, business impact, root-cause, resolution, and change-reference fields
- Audit history for material ticket changes
- SQL-driven analytics for service metrics, recurring issues, SLA exposure, and data quality
- CSV and JSON reporting for downstream analysis
- Python command-line scripts for repeatable reporting and triage
- Technical specification, use cases, process model, and requirements traceability
- Automated analytics, automation, and web workflow tests
- GitHub Actions validation for release changes

### Changed

- Ticket filters now support status and priority.
- Existing databases receive additive column migrations during initialization.
- Application configuration supports environment-based database and secret settings.

### Repository hygiene

- Removed the committed local virtual environment; dependencies remain reproducible through `requirements.txt`.

### Known limitations

- Authentication and role-based permissions are not implemented.
- Notifications and enterprise monitoring integrations are outside the current scope.
- SQLite is suitable for the demonstration workload, not a high-concurrency production deployment.
