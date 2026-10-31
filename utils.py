from functools import wraps

from flask import abort, redirect, session, url_for

from models import Attendance, ClassSession


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped


def role_required(role):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("auth.login"))
            if session.get("role") != role:
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorator


def subject_attendance_stats(student_id, subject_id):
    """Return (conducted, attended, percentage) for a student in a subject."""
    records = (
        Attendance.query.join(ClassSession)
        .filter(Attendance.student_id == student_id, ClassSession.subject_id == subject_id)
        .all()
    )
    conducted = len(records)
    attended = sum(1 for r in records if r.status == "present")
    percentage = round((attended / conducted) * 100) if conducted else 0
    return conducted, attended, percentage


def overall_attendance_stats(student_id):
    records = Attendance.query.filter(Attendance.student_id == student_id).all()
    conducted = len(records)
    attended = sum(1 for r in records if r.status == "present")
    percentage = round((attended / conducted) * 100) if conducted else 0
    return conducted, attended, percentage
