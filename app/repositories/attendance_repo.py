from app.database import Database
from datetime import date as date_type

ALLOWED_ORDERS = {
        "time_in_desc": "a.time_in DESC",
        "time_in_asc": "a.time_in ASC",
        "last_name_desc": "s.last_name DESC",
        "last_name_asc": "s.last_name ASC",
        "student_number_desc": "s.student_number DESC"
    }


class AttendanceRepository:

    def __init__(self, db: Database):
        self.db = db

    # ===============================================================================================================
    # ===============================================================================================================
    # ==================The following code is for setting the time in and time out ==================================


                                        # This is for logging time in


    def log_time_in(self, student_number: str, card_uid: str,
                    first_name: str, last_name: str, middle_name:str, suffix:str,
                    section: str, grade_level: str):

        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO attendance 
                        (student_number, card_uid, first_name, last_name, middle_name, suffix, section, grade_level)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (student_number, card_uid, first_name, last_name, middle_name, suffix, section, grade_level))
                conn.commit()




    # ===============================================================================================================
    # ===============================================================================================================





                                       #This is for logging time out


    def log_time_out(self, student_number: str):
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                      UPDATE attendance
                      SET time_out = CURRENT_TIME
                      WHERE student_number = %s
                      AND at_date = %s
                      """, (student_number, date_type.today()))
                conn.commit()




    # ===============================================================================================================
    # ===============================================================================================================




                            #This is for checking if the person is already in



    def has_record_today(self, student_number: str) -> bool:
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id FROM attendance
                    WHERE student_number = %s
                    AND at_date = %s
                """, (student_number, date_type.today()))
                return cursor.fetchone() is not None

    # ===============================================================================================================
    # ===============================================================================================================
    #=================== The following code is for the user to be able to view the attendance =======================



                                #This is for getting the attendance list by date



    def get_attendance_date_limit(self, at_date, order_clause = None):

        order_clause = ALLOWED_ORDERS.get(order_clause, "a.time_in DESC")

        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        s.card_uid,
                        s.student_number,
                        s.first_name,
                        s.last_name,
                        TO_CHAR(a.at_date, 'YYYY-MM-DD') AS at_date,
                        TO_CHAR(a.time_in, 'HH24:MI') AS time_in,
                        CASE 
                            WHEN a.time_out IS NULL THEN NULL
                            ELSE TO_CHAR(a.time_out, 'HH24:MI')
                        END AS time_out
                    FROM attendance a
                    JOIN students s ON a.student_number = s.student_number
                    WHERE a.at_date::date = %s
                    ORDER BY """ + order_clause + """
                    LIMIT 10
                """, (at_date,))
                return cursor.fetchall()


    def get_attendance_all(self, at_date, order_clause = None):

        order_clause = ALLOWED_ORDERS.get(order_clause, "a.time_in DESC")

        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        s.card_uid,
                        s.student_number,
                        s.first_name,
                        s.last_name,
                        TO_CHAR(a.at_date, 'YYYY-MM-DD') AS at_date,
                        TO_CHAR(a.time_in, 'HH24:MI') AS time_in,
                        CASE 
                            WHEN a.time_out IS NULL THEN NULL
                            ELSE TO_CHAR(a.time_out, 'HH24:MI')
                        END AS time_out
                    FROM attendance a
                    JOIN students s ON a.student_number = s.student_number
                    WHERE a.at_date::date = %s
                    ORDER BY """ + order_clause,(at_date,)
                )
                return cursor.fetchall()



    # ===============================================================================================================
    # ===============================================================================================================



                                                #This is for searching



    def get_attendance_student(self, at_date, student_number=None,
                               first_name=None, last_name=None, order_clause=None):

        order_clause = ALLOWED_ORDERS.get(order_clause, "a.time_in DESC")

        conditions = ["a.at_date = %s"]
        values = [at_date]


        if student_number:
            conditions.append("s.student_number = %s")
            values.append(student_number)


        elif first_name and last_name:
            conditions.append("s.first_name ILIKE %s")
            conditions.append("s.last_name ILIKE %s")
            values.append(f"{first_name}%")
            values.append(f"{last_name}%")


        elif first_name:
            conditions.append("s.first_name ILIKE %s")
            values.append(f"%{first_name}%")


        elif last_name:
            conditions.append("s.last_name ILIKE %s")
            values.append(f"%{last_name}%")

        query = """
            SELECT
                s.card_uid,
                s.student_number,
                s.first_name,
                s.last_name,
                TO_CHAR(a.at_date, 'YYYY-MM-DD') AS at_date,
                        TO_CHAR(a.time_in, 'HH24:MI') AS time_in,
                        CASE 
                            WHEN a.time_out IS NULL THEN NULL
                            ELSE TO_CHAR(a.time_out, 'HH24:MI')
                        END AS time_out 
            FROM attendance a
            JOIN students s ON a.student_number = s.student_number
            WHERE """ + " AND ".join(conditions) + """
            ORDER BY """ + order_clause

        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, values)
                return cursor.fetchall()

