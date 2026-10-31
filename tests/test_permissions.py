from tests.conftest import login
from models import Student


def test_unauthorized_dashboard_access(client):
    resp = client.get("/teacher/dashboard", follow_redirects=True)
    assert resp.request.path == "/login"


def test_student_cannot_access_teacher_dashboard(client):
    login(client, "student1@test.com")
    resp = client.get("/teacher/dashboard")
    assert resp.status_code == 403


def test_teacher_cannot_access_student_dashboard(client):
    login(client, "teacher1@test.com")
    resp = client.get("/student/dashboard")
    assert resp.status_code == 403


def test_student_sees_only_assigned_subjects(app, client):
    with app.app_context():
        student1 = Student.query.filter_by(email="student1@test.com").first()
        subject_count = len(student1.enrollments)

    login(client, "student1@test.com")
    resp = client.get("/student/dashboard")
    assert f"{subject_count}".encode() in resp.data


def test_student_cannot_view_another_students_profile_route_restricted_to_teacher(client):
    login(client, "student1@test.com")
    resp = client.get("/teacher/students/2/profile")
    assert resp.status_code == 403


def test_student_cannot_modify_teacher_data(client):
    login(client, "student1@test.com")
    resp = client.post("/teacher/subjects/add", data={"name": "Hack", "code": "HAX1", "semester": "5", "section": "A", "department": "CSE"})
    assert resp.status_code == 403
