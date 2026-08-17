from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from auth_utils import role_required
from extensions import db
from models import Student, User
from models.subject import Subject

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/users")
@login_required
@role_required("admin")
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin_users.html", users=all_users)


@admin_bp.route("/users/create", methods=["POST"])
@login_required
@role_required("admin")
def create_user():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    role = request.form.get("role", "student")
    password = request.form.get("password", "")
    roll_no = request.form.get("roll_no", "").strip()
    course = request.form.get("course", "").strip()
    section = request.form.get("section", "").strip()

    if not all([name, email, role, password]):
        flash("Name, email, role, and password are required.", "warning")
        return redirect(url_for("admin.users"))

    if role not in {"student", "teacher", "admin"}:
        flash("Invalid role.", "warning")
        return redirect(url_for("admin.users"))

    if User.query.filter_by(email=email).first():
        flash("Email already registered.", "danger")
        return redirect(url_for("admin.users"))

    user = User(name=name, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    if role == "student":
        if not roll_no:
            flash("Roll number required for student.", "warning")
            db.session.rollback()
            return redirect(url_for("admin.users"))
        if Student.query.filter_by(roll_no=roll_no).first():
            flash("Roll number already exists.", "danger")
            db.session.rollback()
            return redirect(url_for("admin.users"))
        db.session.add(Student(
            user_id=user.id,
            roll_no=roll_no,
            name=name,
            course=course or None,
            section=section or None,
        ))

    db.session.commit()
    flash(f"User '{name}' created successfully.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@login_required
@role_required("admin")
def toggle_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("admin.users"))
    user.is_active_user = not user.is_active_user
    db.session.commit()
    state = "activated" if user.is_active_user else "deactivated"
    flash(f"User '{user.name}' {state}.", "info")
    return redirect(url_for("admin.users"))


@admin_bp.route("/subjects")
@login_required
@role_required("admin")
def subjects():
    all_subjects = Subject.query.order_by(Subject.name.asc()).all()
    return render_template("admin_subjects.html", subjects=all_subjects)


@admin_bp.route("/subjects/create", methods=["POST"])
@login_required
@role_required("admin")
def create_subject():
    name = request.form.get("name", "").strip()
    code = request.form.get("code", "").strip().upper()
    course = request.form.get("course", "").strip()
    section = request.form.get("section", "").strip()

    if not name or not code:
        flash("Subject name and code are required.", "warning")
        return redirect(url_for("admin.subjects"))

    if Subject.query.filter_by(code=code).first():
        flash(f"Subject code '{code}' already exists.", "danger")
        return redirect(url_for("admin.subjects"))

    from flask_login import current_user
    db.session.add(Subject(
        name=name,
        code=code,
        course=course or None,
        section=section or None,
        created_by=current_user.id,
    ))
    db.session.commit()
    flash(f"Subject '{name}' created.", "success")
    return redirect(url_for("admin.subjects"))


@admin_bp.route("/subjects/<int:subject_id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def delete_subject(subject_id):
    subj = db.session.get(Subject, subject_id)
    if not subj:
        flash("Subject not found.", "danger")
        return redirect(url_for("admin.subjects"))
    db.session.delete(subj)
    db.session.commit()
    flash(f"Subject '{subj.name}' deleted.", "info")
    return redirect(url_for("admin.subjects"))
