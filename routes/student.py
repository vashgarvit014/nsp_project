from flask import Blueprint, render_template, session

from models import Activity, Student
from utils import overall_attendance_stats, role_required, subject_attendance_stats

student_bp = Blueprint("student", __name__, url_prefix="/student")


def _current_student():
    return Student.query.filter_by(user_id=session["user_id"]).first_or_404()


@student_bp.route("/dashboard")
@role_required("student")
def dashboard():
    student = _current_student()

    conducted, attended, overall_pct = overall_attendance_stats(student.id)

    subject_stats = []
    unit_percentages = []
    for enrollment in student.enrollments:
        subject = enrollment.subject
        s_conducted, s_attended, s_pct = subject_attendance_stats(student.id, subject.id)
        subject_stats.append(
            {"subject": subject, "conducted": s_conducted, "attended": s_attended, "percentage": s_pct}
        )
        for unit in subject.units:
            if unit.topics:
                unit_percentages.append(unit.completion_percentage())

    curriculum_progress = round(sum(unit_percentages) / len(unit_percentages)) if unit_percentages else 0

    subject_ids = [e.subject_id for e in student.enrollments]
    upcoming_activities = (
        Activity.query.filter(Activity.subject_id.in_(subject_ids), Activity.status == "upcoming")
        .order_by(Activity.due_date)
        .limit(5)
        .all()
        if subject_ids
        else []
    )

    return render_template(
        "student_dashboard.html",
        student=student,
        overall_pct=overall_pct,
        total_subjects=len(student.enrollments),
        curriculum_progress=curriculum_progress,
        subject_stats=subject_stats,
        upcoming_activities=upcoming_activities,
    )


@student_bp.route("/profile")
@role_required("student")
def profile():
    student = _current_student()
    subject_stats = []
    for enrollment in student.enrollments:
        conducted, attended, pct = subject_attendance_stats(student.id, enrollment.subject_id)
        subject_stats.append(
            {"subject": enrollment.subject, "conducted": conducted, "attended": attended, "percentage": pct}
        )
    return render_template("profile.html", student=student, subject_stats=subject_stats, is_teacher_view=False)
