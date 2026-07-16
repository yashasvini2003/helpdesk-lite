import csv
import io
import os
from datetime import datetime, timezone

from flask import Flask, Response, current_app, flash, redirect, render_template, request, url_for

from analytics import build_analysis, get_sla_risk_tickets
from automation import escalate_sla_breaches
from database import connect_database, init_database

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", "development-only-key"),
    DATABASE=os.environ.get("HELPDESK_DATABASE", "helpdesk.db"),
)

ALLOWED_STATUSES = ("Open", "In Progress", "Resolved", "Closed")
ALLOWED_PRIORITIES = ("Low", "Medium", "High", "Critical")
SLA_HOURS = {"Low": 72, "Medium": 48, "High": 24, "Critical": 8}


# -----------------------
# DATABASE CONNECTION
# -----------------------
def get_db_connection():
    return connect_database(current_app.config["DATABASE"])


# -----------------------
# INITIALIZE DATABASE
# -----------------------
def utc_now() -> str:
    return datetime.now(timezone.utc).replace(tzinfo=None).isoformat(" ")


# Initialize DB on startup (Flask 3 safe)
with app.app_context():
    init_database(app.config["DATABASE"])


# -----------------------
# ROUTES
# -----------------------
@app.route("/")
def home():
    return redirect(url_for("list_tickets"))


@app.route("/tickets")
def list_tickets():
    status_filter = request.args.get("status", "all")
    priority_filter = request.args.get("priority", "all")

    conn = get_db_connection()
    conditions = []
    parameters = []
    if status_filter in ALLOWED_STATUSES:
        conditions.append("status = ?")
        parameters.append(status_filter)
    if priority_filter in ALLOWED_PRIORITIES:
        conditions.append("priority = ?")
        parameters.append(priority_filter)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    tickets = conn.execute(
        f"SELECT * FROM tickets {where_clause} ORDER BY created_at DESC",
        parameters,
    ).fetchall()
    conn.close()

    return render_template(
        "tickets.html",
        tickets=tickets,
        status_filter=status_filter,
        priority_filter=priority_filter,
        statuses=ALLOWED_STATUSES,
        priorities=ALLOWED_PRIORITIES,
    )


@app.route("/tickets/new", methods=["GET", "POST"])
def create_ticket():

    if request.method == "POST":
        requester_name = request.form["requester_name"].strip()
        contact_email = request.form["contact_email"].strip()
        device_type = request.form["device_type"].strip()
        location = request.form["location"].strip()
        category = request.form["category"].strip()
        title = request.form["title"].strip()
        description = request.form["description"].strip()
        priority = request.form["priority"].strip()
        assigned_team = request.form.get("assigned_team", "Service Desk").strip()
        business_impact = request.form.get("business_impact", "Single user").strip()

        # Validate required fields
        if not all((requester_name, contact_email, device_type, title, description)):
            flash("Please fill in all required fields (*).")
            return redirect(url_for("create_ticket"))
        if priority not in ALLOWED_PRIORITIES:
            flash("Select a valid priority.")
            return redirect(url_for("create_ticket"))

        now = utc_now()

        conn = get_db_connection()
        conn.execute(
            """
            INSERT INTO tickets (
                requester_name, contact_email, device_type, location, category,
                title, description, priority, status, troubleshooting_notes,
                created_at, updated_at, assigned_team, business_impact,
                sla_target_hours
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                requester_name,
                contact_email,
                device_type,
                location,
                category,
                title,
                description,
                priority,
                "Open",
                "",
                now,
                now,
                assigned_team or "Service Desk",
                business_impact or "Single user",
                SLA_HOURS[priority],
            ),
        )
        ticket_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.execute(
            """
            INSERT INTO ticket_history (
                ticket_id, event_type, new_value, note, created_at
            )
            VALUES (?, 'Ticket created', 'Open', 'Request recorded and triaged.', ?)
            """,
            (ticket_id, now),
        )
        conn.commit()
        conn.close()

        flash("Ticket created successfully.")
        return redirect(url_for("list_tickets"))

    return render_template(
        "create_ticket.html",
        priorities=ALLOWED_PRIORITIES,
    )


@app.route("/tickets/<int:ticket_id>")
def ticket_detail(ticket_id):

    conn = get_db_connection()
    ticket = conn.execute(
        "SELECT * FROM tickets WHERE id = ?", (ticket_id,)
    ).fetchone()
    history = conn.execute(
        """
        SELECT * FROM ticket_history
        WHERE ticket_id = ?
        ORDER BY created_at DESC, id DESC
        """,
        (ticket_id,),
    ).fetchall()
    conn.close()

    if ticket is None:
        flash("Ticket not found.")
        return redirect(url_for("list_tickets"))

    return render_template(
        "ticket_detail.html",
        ticket=ticket,
        history=history,
        statuses=ALLOWED_STATUSES,
        priorities=ALLOWED_PRIORITIES,
    )


@app.route("/tickets/<int:ticket_id>/update", methods=["POST"])
def update_ticket(ticket_id):

    status = request.form.get("status")
    priority = request.form.get("priority")
    troubleshooting_notes = request.form.get("troubleshooting_notes", "").strip()
    assigned_team = request.form.get("assigned_team", "Service Desk").strip()
    business_impact = request.form.get("business_impact", "Single user").strip()
    root_cause = request.form.get("root_cause", "").strip()
    resolution_summary = request.form.get("resolution_summary", "").strip()
    change_reference = request.form.get("change_reference", "").strip()
    escalated = 1 if request.form.get("escalated") == "on" else 0

    if status not in ALLOWED_STATUSES or priority not in ALLOWED_PRIORITIES:
        flash("The requested status or priority is invalid.")
        return redirect(url_for("ticket_detail", ticket_id=ticket_id))

    conn = get_db_connection()
    ticket = conn.execute(
        "SELECT * FROM tickets WHERE id = ?", (ticket_id,)
    ).fetchone()

    if ticket is None:
        conn.close()
        flash("Ticket not found.")
        return redirect(url_for("list_tickets"))

    existing_notes = ticket["troubleshooting_notes"] or ""
    now = utc_now()

    # Add timestamped note if provided
    if troubleshooting_notes:
        new_entry = f"[{now}] {troubleshooting_notes}"
        combined_notes = existing_notes + "\n" + new_entry if existing_notes else new_entry
    else:
        combined_notes = existing_notes

    resolved_at = ticket["resolved_at"]
    if status in ("Resolved", "Closed") and not resolved_at:
        resolved_at = now
    elif status in ("Open", "In Progress"):
        resolved_at = None

    conn.execute(
        """
        UPDATE tickets
        SET status = ?, priority = ?, troubleshooting_notes = ?, updated_at = ?,
            assigned_team = ?, business_impact = ?, sla_target_hours = ?,
            escalated = ?, resolved_at = ?, root_cause = ?,
            resolution_summary = ?, change_reference = ?
        WHERE id = ?
        """,
        (
            status,
            priority,
            combined_notes,
            now,
            assigned_team or "Service Desk",
            business_impact or "Single user",
            SLA_HOURS[priority],
            escalated,
            resolved_at,
            root_cause,
            resolution_summary,
            change_reference,
            ticket_id,
        ),
    )

    history_events = []
    for event_type, old_value, new_value in (
        ("Status changed", ticket["status"], status),
        ("Priority changed", ticket["priority"], priority),
        ("Assignment changed", ticket["assigned_team"], assigned_team),
        ("Escalation changed", str(bool(ticket["escalated"])), str(bool(escalated))),
    ):
        if old_value != new_value:
            history_events.append(
                (ticket_id, event_type, old_value, new_value, None, now)
            )
    if troubleshooting_notes:
        history_events.append(
            (
                ticket_id,
                "Investigation note",
                None,
                None,
                troubleshooting_notes,
                now,
            )
        )
    conn.executemany(
        """
        INSERT INTO ticket_history (
            ticket_id, event_type, old_value, new_value, note, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        history_events,
    )
    conn.commit()
    conn.close()

    flash("Ticket updated successfully.")
    return redirect(url_for("ticket_detail", ticket_id=ticket_id))


@app.route("/analytics")
def analytics_dashboard():
    connection = get_db_connection()
    analysis = build_analysis(connection)
    connection.close()
    return render_template("analytics.html", analysis=analysis)


@app.route("/analytics/export")
def export_sla_report():
    connection = get_db_connection()
    risk_tickets = get_sla_risk_tickets(connection)
    connection.close()

    output = io.StringIO()
    fieldnames = [
        "id",
        "title",
        "priority",
        "status",
        "assigned_team",
        "business_impact",
        "sla_target_hours",
        "age_hours",
        "sla_consumed_percent",
        "risk_status",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(risk_tickets)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=sla-risk-report.csv"},
    )


@app.route("/automation/triage", methods=["POST"])
def run_automated_triage():
    connection = get_db_connection()
    escalated_ids = escalate_sla_breaches(connection)
    connection.close()
    if escalated_ids:
        flash(f"Escalated {len(escalated_ids)} SLA-breached ticket(s).")
    else:
        flash("No new SLA breaches required escalation.")
    return redirect(url_for("analytics_dashboard"))


# -----------------------
# RUN APP
# -----------------------
if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
