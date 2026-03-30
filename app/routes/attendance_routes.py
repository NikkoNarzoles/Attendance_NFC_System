from flask import Blueprint, request, jsonify
from app.services.attendance_service import AttendanceService
from flask import render_template

attendance_bp = Blueprint("attendance", __name__)

def create_attendance_routes(service: AttendanceService):

    # ===============================================================================================================
    # ===============================================================================================================



    @attendance_bp.route("/", methods=["GET"])
    def index():
        return render_template("dashboard.html")



    # ===============================================================================================================
    # ===============================================================================================================

    @attendance_bp.route("/tap/log-in", methods=["POST"])
    def tap_log_in():
        data = request.get_json()
        student_number = data["student_number"]
        result = service.set_logged_in(student_number)
        return jsonify({"message": result})


    @attendance_bp.route("/tap/log-out", methods=["POST"])
    def tap_log_out():
        data = request.get_json()
        student_number = data["student_number"]
        result = service.set_logged_out(student_number)
        return jsonify({"message": result})


    @attendance_bp.route("/manual-log", methods=["POST"])
    def tap():
        data = request.get_json()
        student_number = data["student_number"]
        result = service.set_attendance(student_number)
        return jsonify({"message": result})

    # ===============================================================================================================
    # ===============================================================================================================




    @attendance_bp.route("/attendance", methods=["GET"])
    def get_attendance():
        at_date = request.args.get("at_date")
        order_clause = request.args.get("order_clause")
        result = service.get_daily_attendance(at_date, order_clause)
        if isinstance(result, str):
            return jsonify({"message": result})
        return jsonify(result)

    # ===============================================================================================================
    # ===============================================================================================================




    @attendance_bp.route("/attendance/search", methods=["GET"])
    def search_attendance():
        at_date = request.args.get("at_date")
        order_clause = request.args.get("order_clause")
        student_number = request.args.get("student_number")
        first_name = request.args.get("first_name")
        last_name = request.args.get("last_name")

        result = service.search_attendance(
            at_date=at_date,
            student_number=student_number,
            first_name=first_name,
            last_name=last_name,
            order_clause=order_clause
        )
        if isinstance(result, str):
            return jsonify({"message": result})
        return jsonify(result)


    # ===============================================================================================================
    # ===============================================================================================================




    @attendance_bp.route("/attendance/student_list", methods=["GET"])
    def search_student_in_list():
        first_name = request.args.get("first_name")
        last_name = request.args.get("last_name")
        student_number = request.args.get("student_number")

        result = service.get_student_list(first_name, last_name, student_number)

        if isinstance(result, str):
            return jsonify({"message": result})

        return jsonify(result)






    return attendance_bp