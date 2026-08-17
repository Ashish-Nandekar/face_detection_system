import csv
from datetime import datetime
from io import BytesIO, StringIO

from flask import Blueprint, Response, jsonify, render_template
from flask_login import current_user, login_required

from auth_utils import role_required
from models import Attendance, Student
from services.analytics_service import AnalyticsService

dashboard_bp = Blueprint("dashboard", __name__)
analytics_service = AnalyticsService()


@dashboard_bp.route("/")
@login_required
def home():
    if current_user.role == "student":
        if not current_user.student_profile:
            return render_template(
                "dashboard_student.html", recent=[], attendance_rate=0.0,
                subject_breakdown=[]
            )
        student_id = current_user.student_profile.id
        recent = (
            Attendance.query.filter_by(student_id=student_id)
            .order_by(Attendance.date.desc(), Attendance.time.desc())
            .limit(30)
            .all()
        )
        total_days = Attendance.query.filter_by(student_id=student_id).count()
        present_days = Attendance.query.filter_by(student_id=student_id, status="Present").count()
        attendance_rate = round((present_days / total_days) * 100, 2) if total_days else 0.0
        subject_breakdown = analytics_service.student_subject_breakdown(student_id)
        return render_template(
            "dashboard_student.html",
            recent=recent,
            attendance_rate=attendance_rate,
            subject_breakdown=subject_breakdown,
        )

    low_attendance = analytics_service.students_below_threshold(75)
    subject_summary = analytics_service.subject_attendance_summary()
    context = {
        "now_hour": datetime.now().hour,
        "today_present": analytics_service.today_present_count(),
        "total_students": analytics_service.total_students(),
        "today_rate": analytics_service.attendance_rate_today(),
        "trend": analytics_service.daily_trend(7),
        "defaulters": analytics_service.top_defaulters(8),
        "low_attendance": low_attendance,
        "subject_summary": subject_summary,
    }
    if current_user.role == "admin":
        return render_template("dashboard_admin.html", **context)
    return render_template("dashboard_teacher.html", **context)


@dashboard_bp.route("/analytics")
@login_required
@role_required("admin", "teacher")
def analytics_api():
    payload = {
        "today_present": analytics_service.today_present_count(),
        "total_students": analytics_service.total_students(),
        "attendance_rate_today": analytics_service.attendance_rate_today(),
        "daily_trend": analytics_service.daily_trend(14),
        "top_defaulters": analytics_service.top_defaulters(10),
    }
    return jsonify(payload)


@dashboard_bp.route("/export.csv")
@login_required
@role_required("admin", "teacher")
def export_csv():
    str_output = StringIO()
    writer = csv.writer(str_output)
    writer.writerow(["student", "roll_no", "subject", "date", "time", "status", "source"])
    rows = (
        Attendance.query.join(Student, Student.id == Attendance.student_id)
        .with_entities(
            Student.name, Student.roll_no,
            Attendance.subject_id,
            Attendance.date, Attendance.time,
            Attendance.status, Attendance.source,
        )
        .order_by(Attendance.date.desc(), Attendance.time.desc())
        .all()
    )
    for row in rows:
        writer.writerow([row[0], row[1], row[2] or "—", row[3], row[4], row[5], row[6]])
    byte_output = BytesIO()
    byte_output.write(str_output.getvalue().encode("utf-8-sig"))
    byte_output.seek(0)
    return Response(
        byte_output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=attendance_export.csv"},
    )


@dashboard_bp.route("/export.pdf")
@login_required
@role_required("admin", "teacher")
def export_pdf():
    from io import BytesIO
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    rows = (
        Attendance.query.join(Student, Student.id == Attendance.student_id)
        .with_entities(
            Student.name, Student.roll_no,
            Attendance.date, Attendance.time,
            Attendance.status, Attendance.source,
        )
        .order_by(Attendance.date.desc())
        .all()
    )

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), leftMargin=1*cm, rightMargin=1*cm,
                             topMargin=1.5*cm, bottomMargin=1*cm)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph("Attendance Report", styles["Title"]))
    elements.append(Spacer(1, 0.4*cm))

    data = [["Student", "Roll No", "Date", "Time", "Status", "Source"]]
    for r in rows:
        data.append([r[0], r[1], str(r[2]), str(r[3]), r[4], r[5]])

    t = Table(data, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f6fb")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e5e7eb")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(t)
    doc.build(elements)
    buf.seek(0)
    return Response(
        buf.read(),
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment; filename=attendance_report.pdf"},
    )
