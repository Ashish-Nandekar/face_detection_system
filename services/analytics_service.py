from datetime import date, timedelta

from sqlalchemy import func

from models import Attendance, Student
from models.subject import Subject


class AnalyticsService:
    def total_students(self) -> int:
        return Student.query.count()

    def today_present_count(self) -> int:
        return Attendance.query.filter_by(date=date.today(), status="Present").count()

    def attendance_rate_today(self) -> float:
        total = self.total_students()
        if total == 0:
            return 0.0
        return round((self.today_present_count() / total) * 100, 2)

    def daily_trend(self, days: int = 7):
        start_date = date.today() - timedelta(days=days - 1)
        rows = (
            Attendance.query.with_entities(Attendance.date, func.count(Attendance.id))
            .filter(Attendance.date >= start_date, Attendance.status == "Present")
            .group_by(Attendance.date)
            .order_by(Attendance.date.asc())
            .all()
        )
        return [{"date": str(row[0]), "present_count": int(row[1])} for row in rows]

    def top_defaulters(self, limit: int = 10):
        rows = (
            Student.query.with_entities(
                Student.id, Student.name, func.count(Attendance.id).label("present_days")
            )
            .outerjoin(
                Attendance,
                (Attendance.student_id == Student.id) & (Attendance.status == "Present"),
            )
            .group_by(Student.id, Student.name)
            .order_by(func.count(Attendance.id).asc())
            .limit(limit)
            .all()
        )
        return [
            {"student_id": row.id, "name": row.name, "present_days": int(row.present_days or 0)}
            for row in rows
        ]

    def student_attendance_rate(self, student_id: int) -> float:
        total = Attendance.query.filter_by(student_id=student_id).count()
        if total == 0:
            return 0.0
        present = Attendance.query.filter_by(student_id=student_id, status="Present").count()
        return round((present / total) * 100, 2)

    def students_below_threshold(self, threshold: int = 75):
        all_students = Student.query.all()
        result = []
        for s in all_students:
            rate = self.student_attendance_rate(s.id)
            result.append({
                "student_id": s.id,
                "name": s.name,
                "roll_no": s.roll_no,
                "rate": rate,
                "low": rate < threshold,
            })
        return [r for r in result if r["low"]]

    def subject_attendance_summary(self):
        rows = (
            Subject.query.with_entities(
                Subject.id,
                Subject.name,
                Subject.code,
                func.count(Attendance.id).label("present_count"),
            )
            .outerjoin(
                Attendance,
                (Attendance.subject_id == Subject.id) & (Attendance.status == "Present"),
            )
            .group_by(Subject.id, Subject.name, Subject.code)
            .all()
        )
        return [
            {"subject_id": r.id, "name": r.name, "code": r.code, "present_count": int(r.present_count or 0)}
            for r in rows
        ]

    def student_subject_breakdown(self, student_id: int):
        subjects = Subject.query.all()
        result = []
        for subj in subjects:
            total = Attendance.query.filter_by(student_id=student_id, subject_id=subj.id).count()
            present = Attendance.query.filter_by(
                student_id=student_id, subject_id=subj.id, status="Present"
            ).count()
            rate = round((present / total) * 100, 2) if total else 0.0
            result.append({
                "subject": subj.name,
                "code": subj.code,
                "present": present,
                "total": total,
                "rate": rate,
            })
        return result
