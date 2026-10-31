"""Seed the database with demonstration data for the Smart Curriculum &
Attendance Management System.

Usage:
    python seed.py              # drop everything and reseed from scratch
    python -c "from seed import seed_if_empty; seed_if_empty()"
                                 # used on deploy: seed only if the database
                                 # has no users yet, otherwise leave data alone
"""
import random
from datetime import date, timedelta

from app import create_app
from models import (
    Activity,
    Attendance,
    ClassSession,
    Student,
    StudentSubjectEnrollment,
    Subject,
    SyllabusTopic,
    SyllabusUnit,
    User,
    db,
)

DEPARTMENT = "Computer Science"
SEMESTER = 5
SECTION = "A"

TEACHERS = [
    {"email": "teacher1@scams.edu", "name": "Dr. Anjali Sharma", "password": "teacher123"},
    {"email": "teacher2@scams.edu", "name": "Prof. Rakesh Verma", "password": "teacher123"},
]

STUDENT_NAMES = [
    "Aarav Singh", "Priya Patel", "Rohan Gupta", "Sneha Reddy", "Vikram Nair",
    "Ananya Iyer", "Karan Mehta", "Divya Joshi", "Arjun Rao", "Ishita Kapoor",
    "Siddharth Menon", "Neha Chawla", "Aditya Pillai", "Riya Desai", "Manish Kulkarni",
]

SUBJECTS = [
    {"name": "Data Structures", "code": "CS501"},
    {"name": "Database Management Systems", "code": "CS502"},
    {"name": "Operating Systems", "code": "CS503"},
    {"name": "Computer Networks", "code": "CS504"},
]

SYLLABUS = {
    "Data Structures": [
        ("Unit 1: Introduction", ["Arrays", "Time Complexity", "Abstract Data Types"]),
        ("Unit 2: Linked Lists", ["Singly Linked List", "Doubly Linked List", "Circular Linked List"]),
        ("Unit 3: Stacks and Queues", ["Stack Operations", "Queue Operations", "Applications"]),
        ("Unit 4: Trees and Graphs", ["Binary Trees", "Binary Search Trees", "Graph Traversal"]),
        ("Unit 5: Searching and Sorting", ["Linear/Binary Search", "Bubble/Merge Sort", "Quick Sort"]),
    ],
    "Database Management Systems": [
        ("Unit 1: Introduction to DBMS", ["DBMS Architecture", "Data Models"]),
        ("Unit 2: Relational Model", ["Relational Algebra", "Keys and Constraints"]),
        ("Unit 3: SQL", ["DDL and DML", "Joins", "Subqueries"]),
        ("Unit 4: Normalization", ["1NF, 2NF, 3NF", "BCNF"]),
    ],
    "Operating Systems": [
        ("Unit 1: OS Basics", ["Processes", "Threads"]),
        ("Unit 2: Scheduling", ["CPU Scheduling Algorithms", "Deadlocks"]),
        ("Unit 3: Memory Management", ["Paging", "Segmentation"]),
    ],
    "Computer Networks": [
        ("Unit 1: Network Basics", ["OSI Model", "TCP/IP Model"]),
        ("Unit 2: Data Link Layer", ["Error Detection", "MAC Protocols"]),
        ("Unit 3: Network Layer", ["IP Addressing", "Routing Algorithms"]),
    ],
}

ACTIVITIES = [
    ("Assignment 1: Arrays & Linked Lists", "Assignment", "Data Structures", 5),
    ("Quiz on SQL Joins", "Quiz", "Database Management Systems", 3),
    ("Seminar: Deadlock Avoidance", "Seminar", "Operating Systems", 10),
    ("Workshop: Subnetting Practice", "Workshop", "Computer Networks", 7),
    ("Assignment 2: Tree Traversals", "Assignment", "Data Structures", 14),
    ("Presentation: Normalization Case Study", "Presentation", "Database Management Systems", 12),
    ("Classroom Activity: Scheduling Simulation", "Classroom Activity", "Operating Systems", -2),
    ("Quiz on OSI Layers", "Quiz", "Computer Networks", -5),
    ("Assignment 3: Sorting Algorithms", "Assignment", "Data Structures", -8),
]


def populate():
    """Create demo data. Assumes an app context is already active and the
    schema already exists (tables empty or freshly created)."""
    teacher_users = []
    for t in TEACHERS:
        user = User(email=t["email"], name=t["name"], role="teacher")
        user.set_password(t["password"])
        db.session.add(user)
        teacher_users.append(user)
    db.session.flush()

    subjects = {}
    for i, subj in enumerate(SUBJECTS):
        creator = teacher_users[i % len(teacher_users)]
        subject = Subject(
            name=subj["name"],
            code=subj["code"],
            semester=SEMESTER,
            section=SECTION,
            department=DEPARTMENT,
            created_by=creator.id,
        )
        db.session.add(subject)
        subjects[subj["name"]] = subject
    db.session.flush()

    for subject_name, units in SYLLABUS.items():
        subject = subjects[subject_name]
        for order, (unit_title, topics) in enumerate(units, start=1):
            unit = SyllabusUnit(subject_id=subject.id, title=unit_title, order=order)
            db.session.add(unit)
            db.session.flush()
            for topic_title in topics:
                completed = random.random() < 0.6
                db.session.add(SyllabusTopic(unit_id=unit.id, title=topic_title, completed=completed))
    db.session.flush()

    students = []
    for idx, name in enumerate(STUDENT_NAMES, start=1):
        email = f"student{idx}@scams.edu"
        user = User(email=email, name=name, role="student")
        user.set_password("student123")
        db.session.add(user)
        db.session.flush()

        student = Student(
            user_id=user.id,
            full_name=name,
            roll_number=f"CS{SEMESTER}{idx:02d}",
            email=email,
            semester=SEMESTER,
            section=SECTION,
            department=DEPARTMENT,
        )
        db.session.add(student)
        students.append(student)
    db.session.flush()

    for student in students:
        for subject in subjects.values():
            db.session.add(StudentSubjectEnrollment(student_id=student.id, subject_id=subject.id))
    db.session.flush()

    today = date.today()
    for subject in subjects.values():
        creator_id = subject.created_by
        for days_ago in range(15, 0, -1):
            session_date = today - timedelta(days=days_ago)
            if session_date.weekday() >= 5:
                continue
            class_session = ClassSession(
                subject_id=subject.id, session_date=session_date, created_by=creator_id
            )
            db.session.add(class_session)
            db.session.flush()

            for student in students:
                attendance_chance = 0.5 if student.roll_number.endswith(("01", "02", "03")) else 0.88
                status = "present" if random.random() < attendance_chance else "absent"
                db.session.add(
                    Attendance(session_id=class_session.id, student_id=student.id, status=status)
                )

    for title, activity_type, subject_name, offset_days in ACTIVITIES:
        subject = subjects[subject_name]
        due_date = today + timedelta(days=offset_days)
        status = "completed" if offset_days < 0 else "upcoming"
        db.session.add(
            Activity(
                subject_id=subject.id,
                title=title,
                description=f"{activity_type} for {subject_name}.",
                activity_type=activity_type,
                due_date=due_date,
                created_by=subject.created_by,
                status=status,
            )
        )

    db.session.commit()

    print("Database seeded successfully.")
    print("\nDemo Teacher Accounts:")
    for t in TEACHERS:
        print(f"  email: {t['email']}  password: {t['password']}")
    print("\nDemo Student Accounts (password: student123):")
    for idx in range(1, len(STUDENT_NAMES) + 1):
        print(f"  email: student{idx}@scams.edu")


def seed():
    """Drop and recreate the schema, then populate with fresh demo data."""
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        populate()


def seed_if_empty():
    """Create the schema if missing, and populate only if there are no
    users yet. Safe to run on every deploy/restart without wiping data
    a teacher or student has already entered."""
    app = create_app()
    with app.app_context():
        db.create_all()
        if User.query.count() == 0:
            populate()
        else:
            print("Database already has data — skipping seed.")


if __name__ == "__main__":
    seed()
