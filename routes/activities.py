from datetime import datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from models import Activity, Student, Subject, db
from utils import role_required

activities_bp = Blueprint("activities", __name__, url_prefix="/activities")

ACTIVITY_TYPES = ["Assignment", "Quiz", "Seminar", "Presentation", "Workshop", "Classroom Activity"]


@activities_bp.route("/")
@role_required("teacher")
def list_activities():
    teacher_id = session["user_id"]
    activities = (
        Activity.query.join(Subject)
        .filter(Subject.created_by == teacher_id)
        .order_by(Activity.due_date)
        .all()
    )
    subjects = Subject.query.filter_by(created_by=teacher_id).order_by(Subject.name).all()
    return render_template("activities.html", activities=activities, subjects=subjects, activity_types=ACTIVITY_TYPES, is_teacher_view=True)


@activities_bp.route("/add", methods=["POST"])
@role_required("teacher")
def add_activity():
    teacher_id = session["user_id"]
    subject_id = request.form.get("subject_id", type=int)
    subject = Subject.query.filter_by(id=subject_id, created_by=teacher_id).first()
    if not subject:
        abort(403)

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    activity_type = request.form.get("activity_type", "").strip()
    due_date_str = request.form.get("due_date", "").strip()

    errors = []
    if not all([title, activity_type, due_date_str]):
        errors.append("Title, type, and due date are required.")

    due_date = None
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        except ValueError:
            errors.append("Invalid due date.")

    if errors:
        for e in errors:
            flash(e, "danger")
        return redirect(url_for("activities.list_activities"))

    activity = Activity(
        subject_id=subject.id,
        title=title,
        description=description,
        activity_type=activity_type,
        due_date=due_date,
        created_by=teacher_id,
        status="upcoming",
    )
    db.session.add(activity)
    db.session.commit()
    flash("Activity created.", "success")
    return redirect(url_for("activities.list_activities"))


@activities_bp.route("/<int:activity_id>/edit", methods=["POST"])
@role_required("teacher")
def edit_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    if activity.created_by != session["user_id"]:
        abort(403)

    activity.title = request.form.get("title", activity.title).strip()
    activity.description = request.form.get("description", activity.description).strip()
    activity.activity_type = request.form.get("activity_type", activity.activity_type).strip()
    due_date_str = request.form.get("due_date")
    if due_date_str:
        try:
            activity.due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid due date.", "danger")
            return redirect(url_for("activities.list_activities"))
    activity.status = request.form.get("status", activity.status)

    db.session.commit()
    flash("Activity updated.", "success")
    return redirect(url_for("activities.list_activities"))


@activities_bp.route("/<int:activity_id>/delete", methods=["POST"])
@role_required("teacher")
def delete_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    if activity.created_by != session["user_id"]:
        abort(403)

    db.session.delete(activity)
    db.session.commit()
    flash("Activity deleted.", "info")
    return redirect(url_for("activities.list_activities"))


@activities_bp.route("/my-activities")
@role_required("student")
def student_activities():
    student = Student.query.filter_by(user_id=session["user_id"]).first_or_404()
    subject_ids = [e.subject_id for e in student.enrollments]
    activities = (
        Activity.query.filter(Activity.subject_id.in_(subject_ids)).order_by(Activity.due_date).all()
        if subject_ids
        else []
    )
    return render_template("activities.html", activities=activities, is_teacher_view=False)
