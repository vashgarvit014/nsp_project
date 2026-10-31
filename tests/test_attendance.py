from datetime import date

from tests.conftest import login
from models import Activity, Attendance, ClassSession, Student, Subject, SyllabusTopic, SyllabusUnit, db


def test_add_student(app, client):
    login(client, "teacher1@test.com")
    resp = client.post(
        "/teacher/students/add",
        data={
            "full_name": "New Student", "roll_number": "CS99", "email": "new@test.com",
            "semester": "5", "section": "A", "department": "CSE", "password": "pass123",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    with app.app_context():
        assert Student.query.filter_by(roll_number="CS99").first() is not None


def test_edit_student(app, client):
    login(client, "teacher1@test.com")
    with app.app_context():
        student_id = Student.query.filter_by(roll_number="CS01").first().id

    resp = client.post(
        f"/teacher/students/{student_id}/edit",
        data={
            "full_name": "Updated Name", "roll_number": "CS01", "email": "student1@test.com",
            "semester": "5", "section": "A", "department": "CSE",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    with app.app_context():
        assert Student.query.get(student_id).full_name == "Updated Name"


def test_mark_attendance_creates_one_session(app, client):
    login(client, "teacher1@test.com")
    with app.app_context():
        subject = Subject.query.first()
        student1, student2 = Student.query.order_by(Student.id).all()

    today = date.today().isoformat()
    resp = client.post(
        "/attendance/mark",
        data={
            "subject_id": subject.id, "session_date": today,
            f"status_{student1.id}": "present", f"status_{student2.id}": "absent",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200

    with app.app_context():
        sessions = ClassSession.query.filter_by(subject_id=subject.id, session_date=date.today()).all()
        assert len(sessions) == 1
        records = Attendance.query.filter_by(session_id=sessions[0].id).all()
        assert len(records) == 2


def test_prevent_duplicate_attendance_record_on_resubmit(app, client):
    login(client, "teacher1@test.com")
    with app.app_context():
        subject = Subject.query.first()
        student1, student2 = Student.query.order_by(Student.id).all()

    today = date.today().isoformat()
    data = {
        "subject_id": subject.id, "session_date": today,
        f"status_{student1.id}": "present", f"status_{student2.id}": "present",
    }
    client.post("/attendance/mark", data=data, follow_redirects=True)
    data[f"status_{student1.id}"] = "absent"
    client.post("/attendance/mark", data=data, follow_redirects=True)

    with app.app_context():
        sessions = ClassSession.query.filter_by(subject_id=subject.id, session_date=date.today()).all()
        assert len(sessions) == 1
        record = Attendance.query.filter_by(session_id=sessions[0].id, student_id=student1.id).first()
        assert record.status == "absent"
        assert Attendance.query.filter_by(session_id=sessions[0].id).count() == 2


def test_attendance_percentage_calculation(app, client):
    login(client, "teacher1@test.com")

    # create 4 sessions manually with a known present/absent pattern
    with app.app_context():
        subject = Subject.query.first()
        student = Student.query.filter_by(roll_number="CS01").first()
        statuses = ["present", "present", "present", "absent"]
        for i, status in enumerate(statuses):
            d = date.today().replace(day=1)
            session_date = d.replace(day=min(28, d.day + i))
            cs = ClassSession(subject_id=subject.id, session_date=session_date, created_by=subject.created_by)
            db.session.add(cs)
            db.session.flush()
            db.session.add(Attendance(session_id=cs.id, student_id=student.id, status=status))
        db.session.commit()

    from utils import subject_attendance_stats
    with app.app_context():
        subject = Subject.query.first()
        student = Student.query.filter_by(roll_number="CS01").first()
        conducted, attended, pct = subject_attendance_stats(student.id, subject.id)
        assert conducted == 4
        assert attended == 3
        assert pct == 75


def test_zero_classes_no_division_error(app):
    with app.app_context():
        student = Student.query.filter_by(roll_number="CS02").first()
        subject = Subject.query.first()
        from utils import subject_attendance_stats
        conducted, attended, pct = subject_attendance_stats(student.id, subject.id)
        assert conducted == 0
        assert pct == 0


def test_update_syllabus_progress(app, client):
    login(client, "teacher1@test.com")
    with app.app_context():
        topic = SyllabusTopic.query.first()
        unit = SyllabusUnit.query.get(topic.unit_id)
        assert unit.completion_percentage() == 0
        topic_id = topic.id

    client.post(f"/curriculum/topics/{topic_id}/toggle", follow_redirects=True)

    with app.app_context():
        unit = SyllabusUnit.query.first()
        assert unit.completion_percentage() == 100


def test_add_academic_activity(app, client):
    login(client, "teacher1@test.com")
    with app.app_context():
        subject = Subject.query.first()

    resp = client.post(
        "/activities/add",
        data={
            "subject_id": subject.id, "title": "New Quiz", "activity_type": "Quiz",
            "due_date": date.today().isoformat(), "description": "Quick quiz",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    with app.app_context():
        assert Activity.query.filter_by(title="New Quiz").first() is not None


def test_dashboard_statistics_match_database(app, client):
    login(client, "teacher1@test.com")
    with app.app_context():
        expected_total_students = Student.query.count()

    resp = client.get("/teacher/dashboard")
    assert f"{expected_total_students}".encode() in resp.data
