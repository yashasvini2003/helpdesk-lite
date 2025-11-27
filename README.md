# HelpDesk Lite – Simple IT Support Ticket System

HelpDesk Lite is a small web application I built to understand how IT support teams manage tickets, troubleshoot technical issues, and keep track of ongoing user problems. In many workplaces, employees raise support requests when something is not working, and IT teams use ticketing systems to record the issue, update its progress, and document every step taken. I wanted to learn this process properly, so I created my own basic help desk system to practice how a real support environment works.

---

## Project Walkthrough Video (YouTube)
*I will update this section with my YouTube link once my video is ready.*
**YouTube Link:** *Coming soon…*

---

## What This App Does

### 1. Create Support Tickets
Users can submit a ticket by filling out:
- Requester name  
- Email  
- Device type (desktop, laptop, printer, mobile device, etc.)  
- Issue title  
- Description  
- Priority (Low, Medium, High)

### 2. View All Tickets
All submitted tickets are shown in a clean, easy-to-read table with:
- Ticket ID  
- Title  
- Requester  
- Device type  
- Priority  
- Status  
- Created date  

You can also filter tickets by their status so you can quickly see what needs attention.

### 3. Update Tickets
When you click on a ticket, you can:
- Change the ticket status  
- Update the priority  
- Add troubleshooting notes  

When new notes are added, they are automatically time-stamped so you can keep track of what happened and when.

### 4. Follow an IT Support Workflow
The app uses a very simple but realistic workflow that IT support teams commonly follow:

**Open → In Progress → Resolved → Closed**

This helped me understand how issues move from being reported to being fully resolved.

---

## Tech Stack

I built this with simple tools so I could focus more on the logic and process rather than complex setups.

- Python  
- Flask  
- SQLite (database file that gets created automatically)  
- HTML  
- CSS  
- Bootstrap for quick styling  

The goal was to keep everything lightweight and practical.

---

## How to Run the Project

### 1. Clone the repository
git clone https://github.com/yashasvini2003/helpdesk-lite.git

cd helpdesk-lite


### 2. Create a virtual environment
python -m venv venv


### 3. Activate the virtual environment
**Windows** - 
venv\Scripts\activate

**macOS / Linux** - 
source venv/bin/activate


### 4. Install Flask
pip install flask


### 5. Run the application
python app.py


Once the server is running, open your browser and go to:
http://127.0.0.1:5000



You can then create tickets, update them, add troubleshooting notes, and try the basic IT support workflow.

---

## Why I Built This Project

I wanted something practical that shows I understand how IT support works in real companies. Most IT teams rely heavily on ticketing systems, and building one from scratch helped me learn:
- How tickets are created and tracked  
- How status changes work  
- Why documenting troubleshooting steps is important  
- How IT support organizes and prioritizes tasks  
- What the lifecycle of a technical issue looks like  

This project helped me connect the theoretical concepts from my program to something hands-on.

---

## What I Learned

Building this project taught me:
- How help desk systems function behind the scenes  
- How incident workflows are structured  
- How to organize and update tickets  
- Writing clear troubleshooting steps  
- How to use Flask to build a web application  
- How to connect a Python app to a database (SQLite)  
- How to structure a simple, clean project  

Most importantly, it helped me understand the perspective of someone working in technical support and how important communication and documentation are.

---

## Future Improvements

Here are some ideas I may add in the future:
- Login system (staff vs normal users)  
- Option to upload screenshots  
- Email notifications when ticket status changes  
- Better search and filtering  
- Dashboard for statistics  

---

## Final Thoughts

HelpDesk Lite may be a small project, but creating it helped me understand the everyday workflow of IT support teams. It gave me a better understanding of how issues are logged, tracked, updated, and resolved. This project also helped me improve my troubleshooting process and learn to think like someone working in technical support.  

Thank you for checking out my project!
