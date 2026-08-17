from datetime import datetime, timedelta

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from extensions import db
from models import Student, User

auth_bp = Blueprint("auth", __name__)

VALID_ROLES = {"student", "teacher", "admin"}


@auth_bp.route("/login", methods=["GET", "POST"])
@auth_bp.route("/login/<role>", methods=["GET", "POST"])
def login(role="student"):
    if role not in VALID_ROLES:
        role = "student"
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.home"))

    prefill_email = ""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        prefill_email = email

        if not email or not password:
            flash("Email and password are required.", "warning")
            return render_template("login.html", role=role, prefill_email=prefill_email)

        user = User.query.filter_by(email=email).first()

        if user and user.locked_until and user.locked_until > datetime.utcnow():
            flash("Account temporarily locked. Try again later.", "danger")
            return render_template("login.html", role=role, prefill_email=prefill_email)

        if user and user.check_password(password) and user.is_active_user:
            if user.role != role:
                flash(f"This account is not registered as {role}. Please select the correct role.", "warning")
                return render_template("login.html", role=user.role, prefill_email=prefill_email)
            user.failed_login_attempts = 0
            user.locked_until = None
            db.session.commit()
            login_user(user)
            return redirect(url_for("dashboard.home"))

        if user:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=15)
                user.failed_login_attempts = 0
            db.session.commit()
        flash("Invalid email or password.", "danger")

    return render_template("login.html", role=role, prefill_email=prefill_email)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.home"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        roll_no = request.form.get("roll_no", "").strip()
        course = request.form.get("course", "").strip()
        section = request.form.get("section", "").strip()

        if not all([name, email, password, confirm_password, roll_no]):
            flash("Name, email, roll no, and password fields are required.", "warning")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "warning")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "warning")
            return render_template("register.html")

        if User.query.filter_by(email=email).first():
            flash("Email is already registered.", "danger")
            return render_template("register.html")

        if Student.query.filter_by(roll_no=roll_no).first():
            flash("Roll number already exists.", "danger")
            return render_template("register.html")

        user = User(name=name, email=email, role="student")
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        student = Student(
            user_id=user.id,
            roll_no=roll_no,
            name=name,
            course=course or None,
            section=section or None,
        )
        db.session.add(student)
        db.session.commit()

        flash("Registration successful. Please login.", "success")
        return redirect(url_for("auth.login", role="student"))

    return render_template("register.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))
