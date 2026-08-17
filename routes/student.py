from flask import Blueprint, abort, render_template
from flask_login import current_user, login_required

from models import Attendance, Student
from services.analytics_service import AnalyticsService

student_bp = Blueprint("student", __name__)
analytics_service = AnalyticsService()


@student_bp.route("/profile")
@login_required
def my_profile():
    """Student views their own profile."""
    if current_user.role != "student" or not current_user.student_profile:
        abort(403)
    return _render_profile(current_user.student_profile)


@student_bp.route("/profile/<int:student_id>")
@login_required
def view_profile(student_id):
    """Admin/teacher views any student profile."""
    if current_user.role not in ("admin", "teacher"):
        abort(403)
    s = Student.query.get_or_404(student_id)
    return _render_profile(s)


def _render_profile(student):
    total = Attendance.query.filter_by(student_id=student.id).count()
    present = Attendance.query.filter_by(student_id=student.id, status="Present").count()
    rate = round((present / total) * 100, 2) if total else 0.0

    recent = (
        Attendance.query.filter_by(student_id=student.id)
        .order_by(Attendance.date.desc(), Attendance.time.desc())
        .limit(30)
        .all()
    )
    subject_breakdown = analytics_service.student_subject_breakdown(student.id)

    return render_template(
        "student_profile.html",
        student=student,
        rate=rate,
        total=total,
        present=present,
        recent=recent,
        subject_breakdown=subject_breakdown,
    )
