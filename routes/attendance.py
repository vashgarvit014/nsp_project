from datetime import date, datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from models import Attendance, ClassSession, Student, Subject, db
from utils import role_required, subject_attendance_stats

attendance_bp = Blueprint("attendance", __name__, url_prefix="/attendance")


def _teacher_subjects():
    return Subject.query.filter_by(created_by=session["user_id"]).order_by(Subject.name).all()


@attendance_bp.route("/mark", methods=["GET", "POST"])
@role_required("teacher")
def mark():
    subjects = _teacher_subjects()
    subject_id = request.args.get("subject_id", type=int) or request.form.get("subject_id", type=int)
    session_date_str = request.args.get("session_date") or request.form.get("session_date")

    selected_subject = None
    enrolled_students = []
    existing_records = {}

    if subject_id:
        selected_subject = Subject.query.filter_by(id=subject_id, created_by=session["user_id"]).first()
        if not selected_subject:
            abort(403)
        enrolled_students = [e.student for e in selected_subject.enrollments]

    if request.method == "POST":
        if not selected_subject:
            flash("Please select a valid subject.", "danger")
            return redirect(url_for("attendance.mark"))

        try:
            session_date = datetime.strptime(session_date_str, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            flash("Please provide a valid date.", "danger")
            return redirect(url_for("attendance.mark", subject_id=subject_id))

        class_session = ClassSession.query.filter_by(subject_id=subject_id, session_date=session_date).first()
        if class_session is None:
            class_session = ClassSession(
                subject_id=subject_id, session_date=session_date, created_by=session["user_id"]
            )
            db.session.add(class_session)
            db.session.flush()

        for student in enrolled_students:
            status = request.form.get(f"status_{student.id}", "absent")
            record = Attendance.query.filter_by(session_id=class_session.id, student_id=student.id).first()
            if record:
                record.status = status
            else:
                db.session.add(Attendance(session_id=class_session.id, student_id=student.id, status=status))

        db.session.commit()
        flash(f"Attendance saved for {selected_subject.name} on {session_date}.", "success")
        return redirect(url_for("attendance.mark", subject_id=subject_id, session_date=session_date_str))

    if selected_subject and session_date_str:
        try:
            session_date = datetime.strptime(session_date_str, "%Y-%m-%d").date()
            class_session = ClassSession.query.filter_by(subject_id=subject_id, session_date=session_date).first()
            if class_session:
                existing_records = {
                    r.student_id: r.status for r in class_session.attendance_records
                }
        except ValueError:
            pass

    return render_template(
        "attendance.html",
        subjects=subjects,
        selected_subject=selected_subject,
        enrolled_students=enrolled_students,
        session_date=session_date_str or "",
        existing_records=existing_records,
        today=date.today().isoformat(),
    )


@attendance_bp.route("/report")
@role_required("teacher")
def report():
    subjects = _teacher_subjects()
    subject_id = request.args.get("subject_id", type=int)
    selected_subject = None
    rows = []

    if subject_id:
        selected_subject = Subject.query.filter_by(id=subject_id, created_by=session["user_id"]).first()
        if not selected_subject:
            abort(403)
        for enrollment in selected_subject.enrollments:
            conducted, attended, pct = subject_attendance_stats(enrollment.student_id, subject_id)
            rows.append(
                {
                    "student": enrollment.student,
                    "conducted": conducted,
                    "attended": attended,
                    "percentage": pct,
                }
            )

    return render_template(
        "attendance_report.html", subjects=subjects, selected_subject=selected_subject, rows=rows
    )
