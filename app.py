import os

from flask import Flask, redirect, render_template, session, url_for
from flask_wtf import CSRFProtect

from config import Config
from models import db

csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(os.path.join(app.root_path, "instance"), exist_ok=True)

    db.init_app(app)
    csrf.init_app(app)

    from routes.auth import auth_bp
    from routes.teacher import teacher_bp
    from routes.student import student_bp
    from routes.attendance import attendance_bp
    from routes.curriculum import curriculum_bp
    from routes.activities import activities_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(curriculum_bp)
    app.register_blueprint(activities_bp)

    @app.route("/")
    def index():
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        if session.get("role") == "teacher":
            return redirect(url_for("teacher.dashboard"))
        return redirect(url_for("student.dashboard"))

    @app.errorhandler(403)
    def forbidden(_e):
        return render_template("error.html", code=403, message="You are not authorized to view this page."), 403

    @app.errorhandler(404)
    def not_found(_e):
        return render_template("error.html", code=404, message="Page not found."), 404

    return app


app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
