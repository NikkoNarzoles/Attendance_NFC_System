from flask import Flask
from app.database import Database
from app.repositories.students_repo import StudentRepository
from app.repositories.attendance_repo import AttendanceRepository
from app.services.attendance_service import AttendanceService
from app.routes.attendance_routes import create_attendance_routes


def create_app():
    app = Flask(__name__)

# Set up the database
    db = Database()
    db.create_tables()

# Create repositories
    student_repo = StudentRepository(db)
    attendance_repo = AttendanceRepository(db)

# Create services and inject repositories
    attendance_service = AttendanceService(student_repo, attendance_repo)

# Register routes and inject services
    app.register_blueprint(create_attendance_routes(attendance_service))

    return app