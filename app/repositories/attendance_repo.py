from app.database import Database
from datetime import date as date_type


ALLOWED_ORDERS = {
        "time_in_desc": "a.time_in DESC",
        "time_in_asc": "a.time_in ASC",
        "last_name_desc": "s.last_name DESC",
        "last_name_asc": "s.last_name ASC",
        "student_number_desc": "s.student_number DESC",
    }



class AttendanceRepository:

    def __init__(self, db: Database):
        self.db = db


# This is for logging time in
    def log_time_in(self, student_number: str, card_uid: str):
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO attendance (student_number, card_uid)
                    VALUES (%s, %s)
                    RETURNING id
                """, (student_number, card_uid))
                conn.commit()



#This is for logging time out
    def log_time_out(self, card_uid: str):
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                      UPDATE attendance
                      SET time_out = CURRENT_TIME
                      WHERE card_uid = %s
                      AND at_date = %s
                      """, (card_uid, date_type.today()))
                conn.commit()


#This is for checking if the person is already in
    def has_record_today(self, card_uid: str) -> bool:
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id FROM attendance
                    WHERE card_uid = %s
                    AND at_date = %s
                """, (card_uid, date_type.today()))
                return cursor.fetchone() is not None


#This is for getting the attendance list by date
    def get_attendance_date(self, target_date=None, order=None):
        if target_date is None:
            target_date = date_type.today()

        order_clause = ALLOWED_ORDERS.get(order, "a.time_in DESC")

        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        s.student_number,
                        s.first_name,
                        s.last_name,
                        s.section,
                        s.grade_level,
                        a.at_date,
                        a.time_in,
                        a.time_out
                    FROM attendance a
                    JOIN students s ON a.student_number = s.student_number
                    WHERE a.at_date::date = %s
                    ORDER BY """ + order_clause,(target_date,)
                )
                return cursor.fetchall()



# This is for searching
    def get_attendance_student(self, at_date=None, student_number=None,
                       first_name=None, last_name=None, order=None):

        if at_date is None:
            at_date = date_type.today()

        order_clause = ALLOWED_ORDERS.get(order, "a.time_in DESC")

        conditions = ["a.at_date = %s"]
        values = [at_date]

        if student_number:
            conditions.append("s.student_number = %s")
            values.append(student_number)

        if first_name:
            conditions.append("s.first_name ILIKE %s")
            values.append(f"%{first_name}%")

        if last_name:
            conditions.append("s.last_name ILIKE %s")
            values.append(f"%{last_name}%")

        query = """
            SELECT
                s.student_number,
                s.first_name,
                s.last_name,
                s.section,
                s.grade_level,
                a.at_date,
                a.time_in,
                a.time_out
            FROM attendance a
            JOIN students s ON a.student_number = s.student_number
            WHERE """ + " AND ".join(conditions) + """
            ORDER BY """ + order_clause

        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, values)
                return cursor.fetchall()

