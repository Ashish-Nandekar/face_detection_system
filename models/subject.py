from extensions import db


class Subject(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(30), unique=True, nullable=False, index=True)
    course = db.Column(db.String(120), nullable=True)
    section = db.Column(db.String(50), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    attendances = db.relationship("Attendance", back_populates="subject")
