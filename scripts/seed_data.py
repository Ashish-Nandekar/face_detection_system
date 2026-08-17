import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from models import Student, User
from models.subject import Subject


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        # --- Users ---
        admin = User.query.filter_by(email="admin@attendance.local").first()
        if not admin:
            admin = User(name="Admin", email="admin@attendance.local", role="admin")
            admin.set_password("admin123")
            db.session.add(admin)

        teacher = User.query.filter_by(email="teacher@attendance.local").first()
        if not teacher:
            teacher = User(name="Teacher", email="teacher@attendance.local", role="teacher")
            teacher.set_password("teacher123")
            db.session.add(teacher)

        student_user = User.query.filter_by(email="student@attendance.local").first()
        if not student_user:
            student_user = User(name="Student One", email="student@attendance.local", role="student")
            student_user.set_password("student123")
            db.session.add(student_user)
            db.session.flush()
            db.session.add(Student(
                user_id=student_user.id,
                roll_no="S001",
                name="Student One",
                course="BSc CS",
                section="A",
                face_label_id=1,
            ))

        db.session.flush()

        # --- Subjects ---
        subjects_data = [
            ("Mathematics", "MATH101", "BSc CS", "A"),
            ("Physics", "PHY101", "BSc CS", "A"),
            ("Computer Science", "CS101", "BSc CS", "A"),
        ]
        for name, code, course, section in subjects_data:
            if not Subject.query.filter_by(code=code).first():
                db.session.add(Subject(name=name, code=code, course=course, section=section))

        db.session.commit()
        print("Seed complete.")
        print("  Admin:   admin@attendance.local / admin123")
        print("  Teacher: teacher@attendance.local / teacher123")
        print("  Student: student@attendance.local / student123")


if __name__ == "__main__":
    seed()
