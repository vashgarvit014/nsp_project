from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        if session.get("role") == "teacher":
            return redirect(url_for("teacher.dashboard"))
        return redirect(url_for("student.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user is None or not user.check_password(password):
            flash("Invalid email or password.", "danger")
            return render_template("login.html")

        session.clear()
        session["user_id"] = user.id
        session["role"] = user.role
        session["name"] = user.name

        flash(f"Welcome back, {user.name}!", "success")
        if user.role == "teacher":
            return redirect(url_for("teacher.dashboard"))
        return redirect(url_for("student.dashboard"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
