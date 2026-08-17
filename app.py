import os
from flask import Flask

from config import Config
from extensions import db, login_manager, migrate
from models import User
from routes.attendance import attendance_bp
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.main import main_bp
from routes.admin import admin_bp
from routes.student import student_bp


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    os.makedirs(app.config["FACE_DATA_DIR"], exist_ok=True)
    os.makedirs(app.config["FACE_MODEL_DIR"], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(attendance_bp, url_prefix="/attendance")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(student_bp, url_prefix="/student")

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
