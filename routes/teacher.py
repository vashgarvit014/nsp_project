from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models import (
    Activity,
    Attendance,
    ClassSession,
    Student,
    StudentSubjectEnrollment,
    Subject,
    SyllabusUnit,
    User,
    db,
)
from utils import role_required, subject_attendance_stats

teacher_bp = Blueprint("teacher", __name__, url_prefix="/teacher")


@teacher_bp.route("/dashboard")
@role_required("teacher")
def dashboard():
    teacher_id = session["user_id"]

    total_students = Student.query.count()
    total_subjects = Subject.query.filter_by(created_by=teacher_id).count()
    total_activities = Activity.query.join(Subject).filter(Subject.created_by == teacher_id).count()

    subjects = Subject.query.filter_by(created_by=teacher_id).all()

    all_percentages = []
    low_attendance_students = []
    for subject in subjects:
        for enrollment in subject.enrollments:
            conducted, attended, pct = subject_attendance_stats(enrollment.student_id, subject.id)
            if conducted:
                all_percentages.append(pct)
            if conducted and pct < 75:
                low_attendance_students.append(
                    {"student": enrollment.student, "subject": subject.name, "percentage": pct}
                )

    avg_attendance = round(sum(all_percentages) / len(all_percentages)) if all_percentages else 0

    unit_percentages = []
    for subject in subjects:
        for unit in subject.units:
            if unit.topics:
                unit_percentages.append(unit.completion_percentage())
    curriculum_completion = round(sum(unit_percentages) / len(unit_percentages)) if unit_percentages else 0

    recent_activities = (
        Activity.query.join(Subject)
        .filter(Subject.created_by == teacher_id)
        .order_by(Activity.id.desc())
        .limit(5)
        .all()
    )

    chart_labels = [s.name for s in subjects]
    chart_data = []
    for s in subjects:
        pcts = []
        for enrollment in s.enrollments:
            conducted, attended, pct = subject_attendance_stats(enrollment.student_id, s.id)
            if conducted:
                pcts.append(pct)
        chart_data.append(round(sum(pcts) / len(pcts)) if pcts else 0)

    return render_template(
        "teacher_dashboard.html",
        total_students=total_students,
        total_subjects=total_subjects,
        avg_attendance=avg_attendance,
        total_activities=total_activities,
        curriculum_completion=curriculum_completion,
        recent_activities=recent_activities,
        low_attendance_students=low_attendance_students[:10],
        subjects=subjects,
        chart_labels=chart_labels,
        chart_data=chart_data,
    )


@teacher_bp.route("/students")
@role_required("teacher")
def students():
    query = Student.query

    search = request.args.get("search", "").strip()
    semester = request.args.get("semester", "").strip()
    section = request.args.get("section", "").strip()

    if search:
        like = f"%{search}%"
        query = query.filter(db.or_(Student.full_name.ilike(like), Student.roll_number.ilike(like)))
    if semester:
        query = query.filter(Student.semester == int(semester))
    if section:
        query = query.filter(Student.section == section)

    student_list = query.order_by(Student.full_name).all()
    return render_template(
        "students.html",
        students=student_list,
        search=search,
        semester=semester,
        section=section,
    )


@teacher_bp.route("/students/add", methods=["GET", "POST"])
@role_required("teacher")
def add_student():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        roll_number = request.form.get("roll_number", "").strip()
        email = request.form.get("email", "").strip().lower()
        semester = request.form.get("semester", "").strip()
        section = request.form.get("section", "").strip()
        department = request.form.get("department", "").strip()
        password = request.form.get("password", "").strip()

        errors = []
        if not all([full_name, roll_number, email, semester, section, department, password]):
            errors.append("All fields are required.")
        if User.query.filter_by(email=email).first():
            errors.append("A user with this email already exists.")
        if semester and not semester.isdigit():
            errors.append("Semester must be a number.")

        if not errors:
            existing = Student.query.filter_by(
                roll_number=roll_number, semester=int(semester), section=section, department=department
            ).first()
            if existing:
                errors.append("A student with this roll number already exists in this semester/section/department.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("student_form.html", student=None, form=request.form)

        user = User(email=email, name=full_name, role="student")
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        student = Student(
            user_id=user.id,
            full_name=full_name,
            roll_number=roll_number,
            email=email,
            semester=int(semester),
            section=section,
            department=department,
        )
        db.session.add(student)
        db.session.commit()

        flash("Student added successfully.", "success")
        return redirect(url_for("teacher.students"))

    return render_template("student_form.html", student=None, form=None)


@teacher_bp.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
@role_required("teacher")
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        roll_number = request.form.get("roll_number", "").strip()
        email = request.form.get("email", "").strip().lower()
        semester = request.form.get("semester", "").strip()
        section = request.form.get("section", "").strip()
        department = request.form.get("department", "").strip()

        errors = []
        if not all([full_name, roll_number, email, semester, section, department]):
            errors.append("All fields are required.")
        if semester and not semester.isdigit():
            errors.append("Semester must be a number.")

        if not errors:
            duplicate = Student.query.filter(
                Student.id != student.id,
                Student.roll_number == roll_number,
                Student.semester == int(semester),
                Student.section == section,
                Student.department == department,
            ).first()
            if duplicate:
                errors.append("Another student already uses this roll number in this semester/section/department.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("student_form.html", student=student, form=request.form)

        student.full_name = full_name
        student.roll_number = roll_number
        student.email = email
        student.semester = int(semester)
        student.section = section
        student.department = department
        student.user.name = full_name
        student.user.email = email
        db.session.commit()

        flash("Student updated successfully.", "success")
        return redirect(url_for("teacher.students"))

    return render_template("student_form.html", student=student, form=None)


@teacher_bp.route("/students/<int:student_id>/profile")
@role_required("teacher")
def student_profile(student_id):
    student = Student.query.get_or_404(student_id)
    subject_stats = []
    for enrollment in student.enrollments:
        conducted, attended, pct = subject_attendance_stats(student.id, enrollment.subject_id)
        subject_stats.append(
            {
                "subject": enrollment.subject,
                "conducted": conducted,
                "attended": attended,
                "percentage": pct,
            }
        )
    enrolled_subject_ids = {e.subject_id for e in student.enrollments}
    available_subjects = [
        s for s in Subject.query.filter_by(created_by=session["user_id"]).all() if s.id not in enrolled_subject_ids
    ]

    return render_template(
        "profile.html",
        student=student,
        subject_stats=subject_stats,
        is_teacher_view=True,
        available_subjects=available_subjects,
    )


@teacher_bp.route("/students/<int:student_id>/enroll", methods=["POST"])
@role_required("teacher")
def enroll_student(student_id):
    student = Student.query.get_or_404(student_id)
    subject_id = request.form.get("subject_id")
    subject = Subject.query.get_or_404(subject_id)

    existing = StudentSubjectEnrollment.query.filter_by(student_id=student.id, subject_id=subject.id).first()
    if existing:
        flash("Student is already enrolled in this subject.", "warning")
    else:
        db.session.add(StudentSubjectEnrollment(student_id=student.id, subject_id=subject.id))
        db.session.commit()
        flash(f"Enrolled {student.full_name} in {subject.name}.", "success")

    return redirect(url_for("teacher.student_profile", student_id=student.id))


@teacher_bp.route("/subjects")
@role_required("teacher")
def subjects():
    teacher_id = session["user_id"]
    subject_list = Subject.query.filter_by(created_by=teacher_id).order_by(Subject.name).all()
    return render_template("subjects.html", subjects=subject_list)


@teacher_bp.route("/subjects/add", methods=["GET", "POST"])
@role_required("teacher")
def add_subject():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        code = request.form.get("code", "").strip().upper()
        semester = request.form.get("semester", "").strip()
        section = request.form.get("section", "").strip()
        department = request.form.get("department", "").strip()

        errors = []
        if not all([name, code, semester, section, department]):
            errors.append("All fields are required.")
        if Subject.query.filter_by(code=code).first():
            errors.append("A subject with this code already exists.")
        if semester and not semester.isdigit():
            errors.append("Semester must be a number.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("subject_form.html", form=request.form)

        subject = Subject(
            name=name,
            code=code,
            semester=int(semester),
            section=section,
            department=department,
            created_by=session["user_id"],
        )
        db.session.add(subject)
        db.session.commit()
        flash("Subject added successfully.", "success")
        return redirect(url_for("teacher.subjects"))

    return render_template("subject_form.html", form=None)
