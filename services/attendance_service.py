from datetime import date, datetime
from typing import List, Optional

from sqlalchemy.exc import IntegrityError

from extensions import db
from models import Attendance, AttendanceAudit, Student


class AttendanceService:
    def mark_attendance(
        self,
        student_id: int,
        recorded_by: Optional[int],
        source: str = "manual",
        status: str = "Present",
        attendance_date: Optional[date] = None,
        subject_id: Optional[int] = None,
    ):
        day = attendance_date or date.today()
        existing = Attendance.query.filter_by(
            student_id=student_id, date=day, subject_id=subject_id
        ).first()
        if existing:
            return existing, False

        record = Attendance(
            student_id=student_id,
            date=day,
            time=datetime.now().time().replace(microsecond=0),
            status=status,
            source=source,
            recorded_by=recorded_by,
            subject_id=subject_id,
        )
        db.session.add(record)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            existing = Attendance.query.filter_by(
                student_id=student_id, date=day, subject_id=subject_id
            ).first()
            return existing, False
        db.session.add(
            AttendanceAudit(
                attendance_id=record.id,
                action="created",
                new_status=record.status,
                changed_by=recorded_by,
            )
        )
        db.session.commit()
        return record, True

    def mark_by_name(
        self,
        student_name: str,
        recorded_by: Optional[int],
        source: str = "camera",
        subject_id: Optional[int] = None,
    ):
        student = Student.query.filter_by(name=student_name).first()
        if not student:
            return None, False, f"Student '{student_name}' not found."
        record, created = self.mark_attendance(
            student.id, recorded_by, source=source, subject_id=subject_id
        )
        return record, created, None

    def bulk_mark(
        self,
        student_ids: List[int],
        recorded_by: Optional[int],
        status: str = "Present",
        subject_id: Optional[int] = None,
        source: str = "manual",
    ):
        newly_marked = 0
        already_marked = 0
        for sid in student_ids:
            _, created = self.mark_attendance(
                student_id=sid,
                recorded_by=recorded_by,
                source=source,
                status=status,
                subject_id=subject_id,
            )
            if created:
                newly_marked += 1
            else:
                already_marked += 1
        return newly_marked, already_marked

    def correct_attendance(self, attendance_id: int, status: str, changed_by: Optional[int] = None):
        record = db.session.get(Attendance, attendance_id)
        if not record:
            return None
        old_status = record.status
        record.status = status
        db.session.add(
            AttendanceAudit(
                attendance_id=record.id,
                action="corrected",
                old_status=old_status,
                new_status=status,
                changed_by=changed_by,
            )
        )
        db.session.commit()
        return record
