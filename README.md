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

## Deployment

Two supported options, depending on what you want:

### Option A — Render (simplest, plain SQLite)

[Render](https://render.com) runs Flask as a normal long-lived process with
a writable filesystem, so plain SQLite works with no extra setup.

1. Push this repo to GitHub (already done if you're reading this there).
2. On [render.com](https://render.com), click **New > Web Service** and
   connect this GitHub repo. Render will detect `render.yaml` and
   pre-fill the build/start commands automatically.
3. If configuring manually instead, set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python -c "from seed import seed_if_empty; seed_if_empty()" && gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Environment Variable:** `SECRET_KEY` — any random string (Render can
     generate one for you).
4. Deploy. The start command seeds demo accounts automatically the first
   time, and leaves data alone on later restarts as long as the database
   already has users.

**Free-tier caveat:** Render's free web services use an ephemeral disk, so if
the service fully spins down from inactivity and a new instance is created,
the SQLite database resets and reseeds itself with fresh demo data. This is
fine for a project demo but isn't durable storage — for a real deployment
you'd want Render's paid persistent disk, or Option B below.

### Option B — Vercel + Turso (serverless, persistent)

Vercel's Python functions have a read-only, ephemeral filesystem, so plain
SQLite doesn't work there — writes vanish between requests and aren't shared
across concurrent instances. [Turso](https://turso.tech) is a free hosted
database that speaks the SQLite protocol (libSQL) over the network, so the
app keeps using SQLAlchemy/SQLite semantics but gets real persistence on
Vercel. This repo already contains `api/index.py` (the Vercel entrypoint),
`api/requirements.txt` (adds the `sqlalchemy-libsql` dialect, kept separate
from the root `requirements.txt` so local/Render setups stay simple), and
`vercel.json`.

1. **Create a free Turso database:**
   ```bash
   curl -sSfL https://get.tur.so/install.sh | bash
   turso auth login              # opens a browser to sign up/log in
   turso db create nsp-project
   turso db show nsp-project --url      # -> TURSO_DATABASE_URL
   turso db tokens create nsp-project   # -> TURSO_AUTH_TOKEN
   ```
2. **Import the repo into Vercel:** [vercel.com/new](https://vercel.com/new) →
   select this GitHub repo → it will detect `vercel.json` automatically.
3. **Set environment variables** in the Vercel project settings:
   - `SECRET_KEY` — any random string
   - `TURSO_DATABASE_URL` — from step 1 (with or without the `libsql://`
     prefix, either works)
   - `TURSO_AUTH_TOKEN` — from step 1
4. Deploy. The first request creates the schema and seeds demo accounts on
   the Turso database automatically; subsequent deploys/cold-starts leave
   existing data alone since it's a real persistent database now.

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
