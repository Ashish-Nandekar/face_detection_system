import os
from urllib.parse import quote_plus
from dotenv import load_dotenv


load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    _db_url = os.getenv("DATABASE_URL")
    if _db_url:
        SQLALCHEMY_DATABASE_URI = _db_url
    else:
        db_user = os.getenv("DB_USER", "root")
        db_password = os.getenv("DB_PASSWORD", "root")
        db_host = os.getenv("DB_HOST", "localhost")
        db_name = os.getenv("DB_NAME", "attendanceDB")
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{db_user}:{quote_plus(db_password)}@{db_host}/{db_name}"
        )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FACE_DATA_DIR = os.getenv("FACE_DATA_DIR", "data/faces")
    FACE_MODEL_DIR = os.getenv("FACE_MODEL_DIR", "data/models")
    ATTENDANCE_COOLDOWN_SECONDS = int(os.getenv("ATTENDANCE_COOLDOWN_SECONDS", "10"))
