# 👤 Face Detection-Based Attendance Management System

A comprehensive web-based attendance management system using **facial recognition** powered by OpenCV LBPH algorithm. Built with Flask, SQLAlchemy, and Bootstrap 5.

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-green.svg)](https://flask.palletsprojects.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-red.svg)](https://opencv.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Features

### 🔐 Authentication & Authorization
- **Role-based access control**: Admin, Teacher, Student
- Secure password hashing with bcrypt
- Account lockout after 5 failed login attempts (15-minute cooldown)
- Student self-registration

### 📸 Face Recognition
- **LBPH (Local Binary Pattern Histogram)** face recognizer
- Browser-based face sample capture (configurable samples: 20-100)
- One-click model training
- Real-time camera-based attendance marking
- Confidence threshold filtering

### 📊 Attendance Management
- Camera-based automatic marking (proxy-proof)
- Manual attendance entry (single/bulk)
- Attendance correction with full audit trail
- Subject-wise attendance tracking
- Date/time filtering and search

### 📈 Analytics Dashboard
- **Admin Dashboard**: Today's stats, 7-day trend, top defaulters, subject summary
- **Teacher Dashboard**: Same analytics for their classes
- **Student Dashboard**: Personal attendance rate, per-subject breakdown
- Students below 75% threshold alerts

### 📄 Export & Reports
- CSV export (all attendance records)
- PDF export with styled tables (ReportLab)
- Downloadable attendance history

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.12+**
- **MySQL 8.0+** or **MariaDB 10.4+**
- Webcam (for face capture/recognition)

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/face-detection-attendance.git
cd face-detection-attendance
```

### 2️⃣ Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables
Create a `.env` file in the project root (copy from `.env.example`):

```env
SECRET_KEY=your-secret-key-change-this-in-production
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_NAME=attendanceDB
FACE_DATA_DIR=data/faces
FACE_MODEL_DIR=data/models
ATTENDANCE_COOLDOWN_SECONDS=10
```

**Important**: Replace `your_mysql_password` with your actual MySQL password.

### 5️⃣ Create Database
```bash
# Login to MySQL
mysql -u root -p

# Create database
CREATE DATABASE attendanceDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### 6️⃣ Run Database Migrations
```bash
# Initialize migrations (if not already done)
flask db init

# Generate migration
flask db migrate -m "Initial schema"

# Apply migration
flask db upgrade
```

### 7️⃣ Seed Demo Data (Optional)
```bash
python scripts/seed_data.py
```

**Demo Accounts:**
| Role    | Email                         | Password     |
|---------|-------------------------------|--------------|
| Admin   | admin@attendance.local        | admin123     |
| Teacher | teacher@attendance.local      | teacher123   |
| Student | student@attendance.local      | student123   |

### 8️⃣ Run the Application
```bash
python app.py
```

Open your browser at **http://127.0.0.1:5000**

---

## 📁 Project Structure

```
face_detection/
├── app.py                      # Flask application factory
├── config.py                   # Configuration (DB, paths, secrets)
├── extensions.py               # SQLAlchemy, Flask-Login, Migrate singletons
├── auth_utils.py               # role_required decorator
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (DO NOT COMMIT)
├── .gitignore                  # Git ignore rules
│
├── models/                     # ORM Models
│   ├── user.py                 # User (auth, roles, lockout)
│   ├── student.py              # Student profile
│   ├── subject.py              # Subject/course
│   ├── attendance.py           # Attendance records
│   └── attendance_audit.py     # Audit log
│
├── routes/                     # Flask Blueprints (URL routes)
│   ├── auth.py                 # Login, register, logout
│   ├── main.py                 # Landing page
│   ├── dashboard.py            # Role-specific dashboards
│   ├── attendance.py           # Attendance management
│   ├── admin.py                # Admin: users & subjects CRUD
│   └── student.py              # Student profile view
│
├── services/                   # Business Logic
│   ├── face_service.py         # Face capture, train, recognition
│   ├── attendance_service.py   # Mark, bulk, correct attendance
│   └── analytics_service.py    # Dashboard stats & trends
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Base layout with navbar
│   ├── login.html              # Role-aware login page
│   ├── register.html           # Student registration
│   ├── dashboard_*.html        # Role-specific dashboards
│   ├── attendance.html         # Attendance management page
│   └── ...
│
├── static/
│   └── styles.css              # Custom CSS
│
├── data/
│   ├── faces/                  # Captured face samples (.jpg)
│   └── models/                 # Trained LBPH model files
│
├── migrations/                 # Alembic database migrations
├── scripts/
│   └── seed_data.py            # Database seeding script
│
└── tests/                      # Pytest test suite
    ├── test_auth_rbac.py
    ├── test_attendance_service.py
    └── test_analytics.py
```

---

## 🎯 Usage Flow

### For Admin:
1. **Login** at `/auth/login/admin`
2. **Manage Users**: `/admin/users` — create teacher/student accounts
3. **Manage Subjects**: `/admin/subjects` — create subjects/courses
4. **View Analytics**: `/dashboard/` — today's stats, defaulters, trends
5. **Export Data**: CSV/PDF export from dashboard

### For Teacher:
1. **Login** at `/auth/login/teacher`
2. **Capture Faces**: `/attendance/` → select student → "Capture Faces"
3. **Train Model**: After capturing all students, click "Train Face Model"
4. **Mark Attendance**: 
   - **Camera**: Click "Start Camera Marking" → webcam scans class
   - **Manual**: Select student → "Mark Attendance"
   - **Bulk**: Select multiple → "Bulk Mark"
5. **Correct Errors**: Click edit icon on any record → change status
6. **View Analytics**: Dashboard shows trends and defaulters

### For Student:
1. **Register** at `/auth/register` (self-service)
2. **Login** at `/auth/login/student`
3. **View Profile**: `/student/profile` — personal attendance rate
4. **Check Breakdown**: See per-subject attendance percentage

---

## 🛠️ Technology Stack

| Component          | Technology                                |
|--------------------|-------------------------------------------|
| **Backend**        | Flask 3.x, Python 3.12                    |
| **ORM**            | SQLAlchemy 2.0, Flask-Migrate (Alembic)   |
| **Authentication** | Flask-Login, Werkzeug (bcrypt)            |
| **Face Detection** | OpenCV 4.x (Haar Cascade + LBPH)          |
| **Database**       | MySQL 8.0 / MariaDB 10.4 (via PyMySQL)    |
| **Frontend**       | Jinja2 templates, Bootstrap 5, plain CSS  |
| **PDF Export**     | ReportLab                                 |
| **Config**         | python-dotenv                             |

---

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_auth_rbac.py -v
```

---

## 🔒 Security Features

✅ **Password Security**: bcrypt hashing with salt  
✅ **Login Protection**: Account lockout after 5 failed attempts  
✅ **RBAC**: Role-based access control on all protected routes  
✅ **CSRF Protection**: Built-in Flask session protection  
✅ **SQL Injection**: Parameterized queries via SQLAlchemy ORM  
✅ **Audit Trail**: Immutable log of all attendance corrections  

⚠️ **For Production**:
- Use HTTPS (TLS/SSL certificate)
- Set strong `SECRET_KEY` in `.env`
- Use environment-specific database credentials
- Enable Flask production mode (`FLASK_ENV=production`)
- Use a WSGI server (Gunicorn/uWSGI) instead of Flask dev server

---

## 📦 Database Schema

### Core Tables

**users** — User accounts with roles and lockout  
**students** — Student profiles linked to users  
**subjects** — Subjects/courses with code, course, section  
**attendance** — Daily attendance records (student + subject + date)  
**attendance_audit** — Immutable change log for corrections  

**Relationships:**
- `users` 1→0..1 `students` (one user can have one student profile)
- `students` 1→N `attendance` (one student has many attendance records)
- `subjects` 1→0..* `attendance` (one subject has many records, nullable)
- `attendance` 1→N `attendance_audit` (one record can have many edits)

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Ashish Nandekar**  
MCA First Year, P. R. Pote Patil College of Engineering & Management, Amravati  
📧 Email: your.email@example.com  
🔗 GitHub: [@YOUR_USERNAME](https://github.com/YOUR_USERNAME)

**Project Guide:** Prof. Sandip Jadhav

---

## 🙏 Acknowledgements

- OpenCV community for robust computer vision library
- Flask and SQLAlchemy teams for excellent web framework
- P. R. Pote Patil College for providing lab resources
- Bootstrap team for responsive UI components

---

## 📸 Screenshots

> Add screenshots of your application here once pushed to GitHub

---

**⭐ If you found this project helpful, please give it a star!**
