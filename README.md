# Smart Curriculum Activity & Attendance Management System

A B.Tech Minor Project — a web-based platform for teachers to manage student
attendance, track curriculum/syllabus completion, and organize academic
activities, with a dedicated dashboard for students to view their own
progress.

## Problem Statement

Manual attendance registers and scattered syllabus-tracking spreadsheets make
it hard for teachers to identify at-risk students or report curriculum
progress, and give students no visibility into their own standing. This
project replaces that manual process with a single, simple web application.

## Objectives

- Provide secure, role-based login for teachers and students.
- Let teachers manage students, subjects, attendance, syllabus, and activities.
- Let students view their own attendance, syllabus progress, and activities.
- Automatically calculate attendance and curriculum-completion percentages.
- Flag students whose attendance drops below 75%.

## Features

- Secure email/password authentication with hashed passwords and sessions.
- Role-based dashboards for Teachers and Students.
- Student management: add, edit, search, filter by semester/section.
- Attendance management: one lecture session per subject/date, mark
  present/absent, edit later, automatic percentage calculation.
- Curriculum tracker: units and topics per subject, completion percentage,
  progress bars.
- Academic activity management: assignments, quizzes, seminars, workshops,
  presentations, classroom activities.
- Dashboard analytics with Chart.js bar charts.
- CSRF-protected forms and server-side validation throughout.

## Technology Stack

- **Backend:** Python, Flask, Jinja2
- **Database:** SQLite with Flask-SQLAlchemy
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js (all bundled
  locally in `static/vendor/` — no CDN or internet connection required to run)
- **Auth:** Flask sessions, Werkzeug password hashing, Flask-WTF CSRF protection

## Project Structure

```text
nsp_project/
├── app.py                 # Application factory & entry point
├── config.py               # Configuration (reads SECRET_KEY from env)
├── models.py                # SQLAlchemy models
├── utils.py                 # Auth decorators & attendance calculations
├── seed.py                  # Demo data generator
├── requirements.txt
├── routes/
│   ├── auth.py
│   ├── teacher.py
│   ├── student.py
│   ├── attendance.py
│   ├── curriculum.py
│   └── activities.py
├── templates/
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   └── vendor/               # Bootstrap, Bootstrap Icons, Chart.js (local)
├── tests/
│   ├── test_auth.py
│   ├── test_attendance.py
│   └── test_permissions.py
└── instance/
    └── app.db                # Created automatically (not committed)
```

## Installation & Setup

```bash
python -m venv venv
```

Activate the virtual environment:

- macOS/Linux: `source venv/bin/activate`
- Windows: `venv\Scripts\activate`

Install dependencies:

```bash
pip install -r requirements.txt
```

(Optional) set a custom secret key:

```bash
export SECRET_KEY="your-secret-key"      # macOS/Linux
set SECRET_KEY=your-secret-key           # Windows
```

## Database Initialization & Demo Accounts

Seeding creates the database and populates it with demonstration data (2
teachers, 15 students, 4 subjects, attendance history, syllabus units/topics,
and 9 academic activities):

```bash
python seed.py
```

**Demo accounts created:**

| Role    | Email                     | Password     |
|---------|---------------------------|--------------|
| Teacher | teacher1@scams.edu        | teacher123   |
| Teacher | teacher2@scams.edu        | teacher123   |
| Student | student1@scams.edu ... student15@scams.edu | student123 |

## Running the Application

```bash
python app.py
```

Visit **http://127.0.0.1:5000** in your browser and log in with one of the
demo accounts above.

## Running Tests

```bash
pip install pytest
python -m pytest
```

Tests cover: login (valid/invalid), role-based access control, adding/editing
students, marking attendance (including duplicate-prevention and percentage
calculation), syllabus progress updates, and activity creation.

## Screenshots

_Add screenshots of the Login page, Teacher Dashboard, Student Dashboard,
Attendance Management, and Curriculum Tracker here for your project report._

## Future Enhancements

(Documented only — not implemented in this minor-project version)

- QR-code based attendance
- Facial recognition attendance
- AI-based attendance/performance prediction
- Mobile application
- WhatsApp notifications
- Parent dashboard
- Advanced analytics
