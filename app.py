import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "change_me_in_production"
DATABASE = "helpdesk.db"


# -----------------------
# DATABASE CONNECTION
# -----------------------
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# -----------------------
# INITIALIZE DATABASE
# -----------------------
def init_db():
    conn = get_db_connection()
    conn.execute(
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
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


# Initialize DB on startup (Flask 3 safe)
with app.app_context():
    init_db()


# -----------------------
# ROUTES
# -----------------------
@app.route("/")
def home():
    return redirect(url_for("list_tickets"))


@app.route("/tickets")
def list_tickets():
    status_filter = request.args.get("status", "all")

    conn = get_db_connection()
    if status_filter == "all":
        tickets = conn.execute(
            "SELECT * FROM tickets ORDER BY created_at DESC"
        ).fetchall()
    else:
        tickets = conn.execute(
            "SELECT * FROM tickets WHERE status = ? ORDER BY created_at DESC",
            (status_filter,),
        ).fetchall()
    conn.close()

    return render_template(
        "tickets.html",
        tickets=tickets,
        status_filter=status_filter
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

        # Validate required fields
        if not requester_name or not contact_email or not device_type or not title or not description:
            flash("Please fill in all required fields (*).")
            return redirect(url_for("create_ticket"))

        now = datetime.utcnow().isoformat(" ")

        conn = get_db_connection()
        conn.execute(
            """
            INSERT INTO tickets (
                requester_name, contact_email, device_type, location, category,
                title, description, priority, status, troubleshooting_notes,
                created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            ),
        )
        conn.commit()
        conn.close()

        flash("Ticket created successfully.")
        return redirect(url_for("list_tickets"))

    return render_template("create_ticket.html")


@app.route("/tickets/<int:ticket_id>")
def ticket_detail(ticket_id):

    conn = get_db_connection()
    ticket = conn.execute(
        "SELECT * FROM tickets WHERE id = ?", (ticket_id,)
    ).fetchone()
    conn.close()

    if ticket is None:
        flash("Ticket not found.")
        return redirect(url_for("list_tickets"))

    statuses = ["Open", "In Progress", "Resolved", "Closed"]
    priorities = ["Low", "Medium", "High"]

    return render_template(
        "ticket_detail.html",
        ticket=ticket,
        statuses=statuses,
        priorities=priorities,
    )


@app.route("/tickets/<int:ticket_id>/update", methods=["POST"])
def update_ticket(ticket_id):

    status = request.form.get("status")
    priority = request.form.get("priority")
    troubleshooting_notes = request.form.get("troubleshooting_notes", "").strip()

    conn = get_db_connection()
    ticket = conn.execute(
        "SELECT * FROM tickets WHERE id = ?", (ticket_id,)
    ).fetchone()

    if ticket is None:
        conn.close()
        flash("Ticket not found.")
        return redirect(url_for("list_tickets"))

    existing_notes = ticket["troubleshooting_notes"] or ""
    now = datetime.utcnow().isoformat(" ")

    # Add timestamped note if provided
    if troubleshooting_notes:
        new_entry = f"[{now}] {troubleshooting_notes}"
        combined_notes = existing_notes + "\n" + new_entry if existing_notes else new_entry
    else:
        combined_notes = existing_notes

    conn.execute(
        """
        UPDATE tickets
        SET status = ?, priority = ?, troubleshooting_notes = ?, updated_at = ?
        WHERE id = ?
        """,
        (status, priority, combined_notes, now, ticket_id),
    )
    conn.commit()
    conn.close()

    flash("Ticket updated successfully.")
    return redirect(url_for("ticket_detail", ticket_id=ticket_id))


# -----------------------
# RUN APP
# -----------------------
if __name__ == "__main__":
    app.run(debug=True)
