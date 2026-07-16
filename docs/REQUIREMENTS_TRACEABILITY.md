# Requirements Traceability Matrix

| ID | Business requirement | Solution component | Verification |
|---|---|---|---|
| FR-01 | Record complete operational requests | `/tickets/new`, `tickets` table | Web workflow test |
| FR-02 | Apply priority-based SLA targets | `SLA_HOURS`, create/update routes | Web workflow test and code review |
| FR-03 | Track assignment, impact, escalation, and resolution | Ticket detail workflow | Manual acceptance test |
| FR-04 | Preserve a history of operational changes | `ticket_history` table | Automation test and manual workflow |
| FR-05 | Identify recurring issue categories | Root-cause SQL CTE | Analytics unit test |
| FR-06 | Identify tickets approaching or exceeding SLA | SLA-risk SQL query | Analytics unit test |
| FR-07 | Automatically escalate SLA breaches | `escalate_sla_breaches()` | Automation unit test |
| FR-08 | Summarize missing operational data | Data-quality SQL query | Analytics unit test |
| FR-09 | Provide downstream report artifacts | CSV route and JSON CLI | Export smoke test |
| NFR-01 | Prevent SQL injection from filter input | Parameterized SQL queries | Code review |
| NFR-02 | Support existing databases | Additive schema migration | Migration smoke test |
| NFR-03 | Validate changes before release | GitHub Actions and unittest suite | CI workflow |
