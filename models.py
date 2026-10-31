from datetime import date, datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'teacher' or 'student'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("Student", back_populates="user", uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_teacher(self):
        return self.role == "teacher"

    def is_student(self):
        return self.role == "student"


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    roll_number = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    section = db.Column(db.String(10), nullable=False)
    department = db.Column(db.String(80), nullable=False)

    user = db.relationship("User", back_populates="student")
    enrollments = db.relationship("StudentSubjectEnrollment", back_populates="student", cascade="all, delete-orphan")
    attendance_records = db.relationship("Attendance", back_populates="student", cascade="all, delete-orphan")

    __table_args__ = (
        db.UniqueConstraint("roll_number", "semester", "section", "department", name="uq_roll_scope"),
    )


class Subject(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(30), unique=True, nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    section = db.Column(db.String(10), nullable=False)
    department = db.Column(db.String(80), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    enrollments = db.relationship("StudentSubjectEnrollment", back_populates="subject", cascade="all, delete-orphan")
    sessions = db.relationship("ClassSession", back_populates="subject", cascade="all, delete-orphan")
    units = db.relationship("SyllabusUnit", back_populates="subject", cascade="all, delete-orphan", order_by="SyllabusUnit.order")
    activities = db.relationship("Activity", back_populates="subject", cascade="all, delete-orphan")


class StudentSubjectEnrollment(db.Model):
    __tablename__ = "student_subject_enrollments"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False)

    student = db.relationship("Student", back_populates="enrollments")
    subject = db.relationship("Subject", back_populates="enrollments")

    __table_args__ = (
        db.UniqueConstraint("student_id", "subject_id", name="uq_student_subject"),
    )


class ClassSession(db.Model):
    __tablename__ = "class_sessions"

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False)
    session_date = db.Column(db.Date, nullable=False, default=date.today)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    subject = db.relationship("Subject", back_populates="sessions")
    attendance_records = db.relationship("Attendance", back_populates="session", cascade="all, delete-orphan")

    __table_args__ = (
        db.UniqueConstraint("subject_id", "session_date", name="uq_subject_date"),
    )


class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("class_sessions.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    status = db.Column(db.String(10), nullable=False)  # 'present' or 'absent'

    session = db.relationship("ClassSession", back_populates="attendance_records")
    student = db.relationship("Student", back_populates="attendance_records")

    __table_args__ = (
        db.UniqueConstraint("session_id", "student_id", name="uq_session_student"),
    )


class SyllabusUnit(db.Model):
    __tablename__ = "syllabus_units"

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    order = db.Column(db.Integer, default=0)

    subject = db.relationship("Subject", back_populates="units")
    topics = db.relationship("SyllabusTopic", back_populates="unit", cascade="all, delete-orphan")

    def completion_percentage(self):
        topics = self.topics
        if not topics:
            return 0
        completed = sum(1 for t in topics if t.completed)
        return round((completed / len(topics)) * 100)


class SyllabusTopic(db.Model):
    __tablename__ = "syllabus_topics"

    id = db.Column(db.Integer, primary_key=True)
    unit_id = db.Column(db.Integer, db.ForeignKey("syllabus_units.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)

    unit = db.relationship("SyllabusUnit", back_populates="topics")


class Activity(db.Model):
    __tablename__ = "activities"

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, default="")
    activity_type = db.Column(db.String(30), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(20), default="upcoming")  # upcoming / completed

    subject = db.relationship("Subject", back_populates="activities")
