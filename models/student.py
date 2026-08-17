from extensions import db


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=True)
    roll_no = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    course = db.Column(db.String(120), nullable=True)
    section = db.Column(db.String(50), nullable=True)
    face_label_id = db.Column(db.Integer, unique=True, nullable=True)

    user = db.relationship("User", back_populates="student_profile")
    attendances = db.relationship("Attendance", back_populates="student", cascade="all, delete-orphan")
