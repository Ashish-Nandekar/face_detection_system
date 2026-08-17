import csv
from io import BytesIO, StringIO

import cv2
from flask import Blueprint, Response, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from auth_utils import role_required
from extensions import db
from models import Attendance, Student
from models.subject import Subject
from services.attendance_service import AttendanceService
from services.face_service import FaceService

attendance_bp = Blueprint("attendance", __name__)
attendance_service = AttendanceService()
face_service = FaceService()


@attendance_bp.route("/")
@login_required
@role_required("admin", "teacher")
def list_attendance():
    students = Student.query.order_by(Student.name.asc()).all()
    subjects = Subject.query.order_by(Subject.name.asc()).all()

    # --- Filters ---
    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")
    student_id = request.args.get("student_id", "")
    section = request.args.get("section", "")
    status = request.args.get("status", "")
    subject_id = request.args.get("subject_id", "")

    query = Attendance.query.join(Student, Student.id == Attendance.student_id)

    if date_from:
        query = query.filter(Attendance.date >= date_from)
    if date_to:
        query = query.filter(Attendance.date <= date_to)
    if student_id and student_id.isdigit():
        query = query.filter(Attendance.student_id == int(student_id))
    if section:
        query = query.filter(Student.section == section)
    if status:
        query = query.filter(Attendance.status == status)
    if subject_id and subject_id.isdigit():
        query = query.filter(Attendance.subject_id == int(subject_id))

    records = query.order_by(Attendance.date.desc(), Attendance.time.desc()).limit(300).all()

    # Unique sections for filter dropdown
    sections = [s[0] for s in db.session.query(Student.section).distinct() if s[0]]

    filters = dict(
        date_from=date_from, date_to=date_to,
        student_id=student_id, section=section,
        status=status, subject_id=subject_id,
    )

    return render_template(
        "attendance.html",
        records=records,
        students=students,
        subjects=subjects,
        sections=sections,
        filters=filters,
    )


@attendance_bp.route("/capture", methods=["POST"])
@login_required
@role_required("admin", "teacher")
def capture_faces():
    student_id_raw = request.form.get("student_id", "").strip()
    samples_raw = request.form.get("num_samples", "20").strip()
    if not student_id_raw.isdigit():
        flash("Please select a valid student.", "warning")
        return redirect(url_for("attendance.list_attendance"))
    student = db.session.get(Student, int(student_id_raw))
    if not student:
        flash("Student not found.", "danger")
        return redirect(url_for("attendance.list_attendance"))
    try:
        num_samples = max(5, min(int(samples_raw), 100))
    except ValueError:
        num_samples = 20
    captured = face_service.capture_faces(student.name, num_samples=num_samples)
    flash(f"Captured {captured} face samples for {student.name}.", "success")
    return redirect(url_for("attendance.list_attendance"))


@attendance_bp.route("/train", methods=["POST"])
@login_required
@role_required("admin", "teacher")
def train_model():
    total_images, known_faces = face_service.train_model()
    if total_images == 0:
        flash("No face samples found. Capture faces first.", "warning")
    else:
        flash(f"Model trained with {total_images} images for {len(known_faces)} students.", "success")
    return redirect(url_for("attendance.list_attendance"))


@attendance_bp.route("/mark", methods=["POST"])
@login_required
@role_required("admin", "teacher")
def mark_attendance():
    student_id_raw = request.form.get("student_id", "").strip()
    subject_id_raw = request.form.get("subject_id", "").strip()
    if not student_id_raw.isdigit():
        flash("Please select a valid student.", "warning")
        return redirect(url_for("attendance.list_attendance"))
    student_id = int(student_id_raw)
    subject_id = int(subject_id_raw) if subject_id_raw.isdigit() else None
    student = db.session.get(Student, student_id)
    if not student:
        flash("Student not found.", "danger")
        return redirect(url_for("attendance.list_attendance"))
    _, created = attendance_service.mark_attendance(
        student_id, current_user.id, source="manual", subject_id=subject_id
    )
    flash("Attendance marked." if created else "Already marked for today.", "info")
    return redirect(url_for("attendance.list_attendance"))


@attendance_bp.route("/bulk", methods=["POST"])
@login_required
@role_required("admin", "teacher")
def bulk_mark():
    student_ids_raw = request.form.getlist("student_ids")
    status = request.form.get("status", "Present")
    subject_id_raw = request.form.get("subject_id", "").strip()

    if status not in {"Present", "Absent", "Late"}:
        flash("Invalid status.", "warning")
        return redirect(url_for("attendance.list_attendance"))

    student_ids = [int(sid) for sid in student_ids_raw if sid.isdigit()]
    if not student_ids:
        flash("No students selected.", "warning")
        return redirect(url_for("attendance.list_attendance"))

    subject_id = int(subject_id_raw) if subject_id_raw.isdigit() else None
    newly, already = attendance_service.bulk_mark(
        student_ids=student_ids,
        recorded_by=current_user.id,
        status=status,
        subject_id=subject_id,
    )
    flash(f"Bulk mark done — {newly} newly marked, {already} already marked.", "success")
    return redirect(url_for("attendance.list_attendance"))


@attendance_bp.route("/correct/<int:attendance_id>", methods=["POST"])
@login_required
@role_required("admin", "teacher")
def correct_attendance(attendance_id):
    status = request.form.get("status", "Present")
    if status not in {"Present", "Absent", "Late"}:
        flash("Invalid attendance status.", "warning")
        return redirect(url_for("attendance.list_attendance"))
    record = attendance_service.correct_attendance(attendance_id, status, changed_by=current_user.id)
    flash("Attendance corrected." if record else "Record not found.", "info")
    return redirect(url_for("attendance.list_attendance"))


@attendance_bp.route("/camera/mark", methods=["POST"])
@login_required
@role_required("admin", "teacher")
def camera_mark():
    try:
        known_faces = face_service.load_model()
    except Exception:
        flash("Model not available. Train face model first.", "danger")
        return redirect(url_for("attendance.list_attendance"))

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        flash("Could not open camera.", "danger")
        return redirect(url_for("attendance.list_attendance"))

    subject_id_raw = request.form.get("subject_id", "").strip()
    subject_id = int(subject_id_raw) if subject_id_raw.isdigit() else None

    marked_names = set()
    frame_count = 0
    try:
        while frame_count < 400:
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_service.face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                face_img = cv2.resize(gray[y: y + h, x: x + w], (200, 200))
                person_id, confidence = face_service.recognizer.predict(face_img)
                recognized = confidence < 100
                if recognized:
                    name = known_faces.get(person_id, "Unknown")
                    color = (0, 255, 0)
                    if name and name not in marked_names:
                        _, created, _ = attendance_service.mark_by_name(
                            name, current_user.id, source="camera", subject_id=subject_id
                        )
                        status_text = "Marked" if created else "Already Marked"
                        if created:
                            marked_names.add(name)
                    else:
                        status_text = "Already Marked"
                else:
                    name = "Unknown"
                    color = (0, 0, 255)
                    status_text = "Not Recognized"
                label = f"{name} | {status_text}"
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(frame, label, (x, max(y - 10, 20)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            cv2.putText(frame, "Attendance Marking - Press Q or ESC to close",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
            cv2.imshow("Face Attendance Marking", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q") or key == 27:
                break
            frame_count += 1
    finally:
        cap.release()
        cv2.destroyAllWindows()
    flash(f"Camera scan done. Marked: {len(marked_names)}", "info")
    return redirect(url_for("attendance.list_attendance"))
