from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from models import Student, Subject, SyllabusTopic, SyllabusUnit, db
from utils import role_required

curriculum_bp = Blueprint("curriculum", __name__, url_prefix="/curriculum")


@curriculum_bp.route("/subject/<int:subject_id>")
@role_required("teacher")
def subject_curriculum(subject_id):
    subject = Subject.query.filter_by(id=subject_id, created_by=session["user_id"]).first()
    if not subject:
        abort(403)
    return render_template("curriculum.html", subject=subject, is_teacher_view=True)


@curriculum_bp.route("/subject/<int:subject_id>/units/add", methods=["POST"])
@role_required("teacher")
def add_unit(subject_id):
    subject = Subject.query.filter_by(id=subject_id, created_by=session["user_id"]).first()
    if not subject:
        abort(403)

    title = request.form.get("title", "").strip()
    if not title:
        flash("Unit title is required.", "danger")
    else:
        order = len(subject.units) + 1
        db.session.add(SyllabusUnit(subject_id=subject.id, title=title, order=order))
        db.session.commit()
        flash("Unit added.", "success")

    return redirect(url_for("curriculum.subject_curriculum", subject_id=subject_id))


@curriculum_bp.route("/units/<int:unit_id>/topics/add", methods=["POST"])
@role_required("teacher")
def add_topic(unit_id):
    unit = SyllabusUnit.query.get_or_404(unit_id)
    if unit.subject.created_by != session["user_id"]:
        abort(403)

    title = request.form.get("title", "").strip()
    if not title:
        flash("Topic title is required.", "danger")
    else:
        db.session.add(SyllabusTopic(unit_id=unit.id, title=title))
        db.session.commit()
        flash("Topic added.", "success")

    return redirect(url_for("curriculum.subject_curriculum", subject_id=unit.subject_id))


@curriculum_bp.route("/topics/<int:topic_id>/toggle", methods=["POST"])
@role_required("teacher")
def toggle_topic(topic_id):
    topic = SyllabusTopic.query.get_or_404(topic_id)
    if topic.unit.subject.created_by != session["user_id"]:
        abort(403)

    topic.completed = not topic.completed
    db.session.commit()

    return redirect(url_for("curriculum.subject_curriculum", subject_id=topic.unit.subject_id))


@curriculum_bp.route("/my-subjects")
@role_required("student")
def student_curriculum():
    student = Student.query.filter_by(user_id=session["user_id"]).first_or_404()
    subjects = [e.subject for e in student.enrollments]
    return render_template("curriculum.html", subjects=subjects, is_teacher_view=False)
