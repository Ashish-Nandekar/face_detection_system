# Face Detection-Based Attendance Management System

A web-based attendance management system that uses **face recognition** to automatically mark student attendance.

## 🚀 Features

* 🔐 User authentication with Admin, Teacher, and Student roles
* 📸 Face detection and recognition using OpenCV LBPH
* 📋 Automatic and manual attendance marking
* 📊 Attendance dashboard and analytics
* 📄 CSV and PDF attendance reports
* 🔒 Password hashing and role-based access control
* 🗄️ MySQL database integration

## 🛠️ Tech Stack

* **Python 3.12**
* **Flask**
* **OpenCV**
* **SQLAlchemy**
* **MySQL**
* **Bootstrap 5**
* **Jinja2**
* **ReportLab**

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/face-detection-attendance.git
cd face-detection-attendance
```

### 2. Create virtual environment

```bash
python -m venv venv
```

**Windows:**

```bash
venv\Scripts\activate
```

**Linux/Mac:**

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure `.env`

Create a `.env` file:

```env
SECRET_KEY=your-secret-key
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_NAME=attendanceDB
```

### 5. Create database

Open MySQL and run:

```sql
CREATE DATABASE attendanceDB;
```

### 6. Run the application

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```



## 👨‍💻 Author

**Ashish Nandekar**

MCA Student
P. R. Pote Patil College of Engineering & Management, Amravati

## 📌 Note

This project was developed as an academic project to demonstrate **Python, Flask, OpenCV, database management, and web application development**.

⭐ If you find this project useful, consider giving it a star!
