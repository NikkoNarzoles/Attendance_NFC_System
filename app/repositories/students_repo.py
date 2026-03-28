import psycopg2
from app.database import Database

class StudentRepository:

    def __init__(self, db: Database):
        self.db = db


    def get_by_card_uid(self, card_uid: str):
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                               SELECT * FROM students
                                WHERE card_uid = %s """, (card_uid,))
                return cursor.fetchone()



