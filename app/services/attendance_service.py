from app.repositories.attendance_repo import AttendanceRepository
from app.repositories.students_repo import StudentRepository
from datetime import date as date_type


class AttendanceService:

    def __init__(self, students: StudentRepository, attendance: AttendanceRepository):
        self.students = students
        self.attendance = attendance


    # ===============================================================================================================
    # ===============================================================================================================



    def serialize_attendance(self, attendance_list):
        for record in attendance_list:
            if record.get("time_in"):
                record["time_in"] = str(record["time_in"])
            if record.get("time_out"):
                record["time_out"] = str(record["time_out"])
        return attendance_list



    # ===============================================================================================================
    # ===============================================================================================================

                             #This is for setting the attendance if only one RFID SCANNER


    def set_attendance(self, card_uid: str):
        student_info = self.students.get_by_card_uid(card_uid)

        if student_info is None:
            return "not registered"

        logged_in_student = self.attendance.has_record_today(card_uid)

        if not logged_in_student:
            self.attendance.log_time_in(
                student_number=student_info["student_number"],
                card_uid=card_uid,
                first_name=student_info["first_name"],
                last_name=student_info["last_name"],
                middle_name=student_info["middle_name"],
                suffix=student_info["suffix"],
                section=student_info["section"],
                grade_level=student_info["grade_level"]
            )
            return "successful time-in"

        self.attendance.log_time_out(card_uid)
        return "successful time-out"



    # ===============================================================================================================
    # ===============================================================================================================

                                        # Service for getting the daily attendance


    def get_daily_attendance(self, at_date=None, order_clause=None):
        if at_date is None:
            at_date = date_type.today()

        attendance_list = self.attendance.get_attendance_date(at_date, order_clause)

        if not attendance_list:
            return "no records"

        return self.serialize_attendance(attendance_list)



    # ===============================================================================================================
    # ===============================================================================================================

                                                # Service for searching



    def search_attendance(self, at_date=None, student_number=None,
                          first_name=None, last_name=None, order_clause=None):
        if at_date is None:
            at_date = date_type.today()

        result = self.attendance.get_attendance_student(
            at_date=at_date,
            student_number=student_number,
            first_name=first_name,
            last_name=last_name,
            order_clause=order_clause
        )

        if not result:
            return "no records"

        return self.serialize_attendance(result)




    #===============================================================================================================
    #===============================================================================================================


                    #Service for manual attendance - student number, first name, last name, card uid


    def get_student_list(self, first_name=None, last_name=None, student_number=None):

        student = self.students.search_by_student_info(first_name,last_name, student_number)

        if not student:
            return "not enrolled"

        return student


