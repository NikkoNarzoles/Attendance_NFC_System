from app.database import Database

class StudentRepository:

    def __init__(self, db: Database):
        self.db = db

#This is for getting the student by uid
    def get_by_card_uid(self, card_uid: str):
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                               SELECT * FROM students
                                WHERE card_uid = %s """, (card_uid,))
                return cursor.fetchone()



# This is for getting the student by student_number
    def get_by_student_number(self, student_number: str):
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                               SELECT * FROM students
                                WHERE student_number = %s """, (student_number,))
                return cursor.fetchone()



#This is for getting the student by student info
    def search_by_student_info(self, first_name=None, last_name=None, student_number=None):
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:

                conditions = []
                values = []

                if student_number:
                    conditions.append("student_number ILIKE %s")
                    values.append(f"%{student_number}%")

                elif first_name and last_name:
                    conditions.append("first_name ILIKE %s")
                    conditions.append("last_name ILIKE %s")
                    values.append(f"{first_name}%")
                    values.append(f"{last_name}%")

                    where_clause = " AND ".join(conditions)

                elif first_name:
                    conditions.append("first_name ILIKE %s")
                    values.append(f"%{first_name}%")

                    where_clause = " OR ".join(conditions)

                elif last_name:
                    conditions.append("last_name ILIKE %s")
                    values.append(f"%{last_name}%")

                    where_clause = " OR ".join(conditions)

                else:
                    where_clause = "TRUE"

                if 'where_clause' not in locals():
                    where_clause = " OR ".join(conditions)

                cursor.execute(f"""
                    SELECT * FROM students
                    WHERE {where_clause} 
                    LIMIT 14""", values)

                return cursor.fetchall()