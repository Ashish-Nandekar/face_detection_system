from datetime import date, datetime, time

from extensions import db


class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False, index=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=True, index=True)
    date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    time = db.Column(db.Time, nullable=False, default=lambda: datetime.now().time())
    status = db.Column(db.String(20), nullable=False, default="Present")
    source = db.Column(db.String(20), nullable=False, default="camera")
    recorded_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    student = db.relationship("Student", back_populates="attendances")
    subject = db.relationship("Subject", back_populates="attendances")
    recorder = db.relationship("User", foreign_keys=[recorded_by])

    __table_args__ = (
        db.UniqueConstraint("student_id", "date", "subject_id", name="uq_student_daily_subject_attendance"),
    )
