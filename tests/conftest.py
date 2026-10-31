import pytest

from app import create_app
from models import (
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


@pytest.fixture
def app():
    flask_app = create_app()
    flask_app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        WTF_CSRF_ENABLED=False,
    )

    with flask_app.app_context():
        db.drop_all()
        db.create_all()

        teacher1 = User(email="teacher1@test.com", name="Teacher One", role="teacher")
        teacher1.set_password("pass123")
        teacher2 = User(email="teacher2@test.com", name="Teacher Two", role="teacher")
        teacher2.set_password("pass123")
        db.session.add_all([teacher1, teacher2])
        db.session.flush()

        subject = Subject(
            name="Data Structures", code="CS101", semester=5, section="A",
            department="CSE", created_by=teacher1.id,
        )
        db.session.add(subject)
        db.session.flush()

        unit = SyllabusUnit(subject_id=subject.id, title="Unit 1", order=1)
        db.session.add(unit)
        db.session.flush()
        db.session.add(SyllabusTopic(unit_id=unit.id, title="Arrays", completed=False))

        student1_user = User(email="student1@test.com", name="Student One", role="student")
        student1_user.set_password("pass123")
        student2_user = User(email="student2@test.com", name="Student Two", role="student")
        student2_user.set_password("pass123")
        db.session.add_all([student1_user, student2_user])
        db.session.flush()

        student1 = Student(
            user_id=student1_user.id, full_name="Student One", roll_number="CS01",
            email="student1@test.com", semester=5, section="A", department="CSE",
        )
        student2 = Student(
            user_id=student2_user.id, full_name="Student Two", roll_number="CS02",
            email="student2@test.com", semester=5, section="A", department="CSE",
        )
        db.session.add_all([student1, student2])
        db.session.flush()

        db.session.add(StudentSubjectEnrollment(student_id=student1.id, subject_id=subject.id))
        db.session.add(StudentSubjectEnrollment(student_id=student2.id, subject_id=subject.id))
        db.session.commit()

    yield flask_app

    with flask_app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def login(client, email, password="pass123"):
    return client.post("/login", data={"email": email, "password": password}, follow_redirects=True)
