import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.host     = os.getenv("DB_HOST")
        self.port     = os.getenv("DB_PORT")
        self.name     = os.getenv("DB_NAME")
        self.user     = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")

    def get_connection(self):
        return psycopg2.connect(
            host     = self.host,
            port     = self.port,
            dbname   = self.name,
            user     = self.user,
            password = self.password,
            cursor_factory = RealDictCursor
        )

    def create_tables(self):
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS attendance (
                        id             SERIAL PRIMARY KEY,
                        student_number VARCHAR(20) NOT NULL,
                        card_uid       VARCHAR(20) NOT NULL,
                        first_name     VARCHAR(50) NOT NULL,
                        last_name      VARCHAR(50) NOT NULL,
                        middle_name    VARCHAR(50) NULL,
                        suffix         VARCHAR(20) NULL,
                        section        VARCHAR(20) NOT NULL,
                        grade_level    VARCHAR(20) NOT NULL,
                        at_date        DATE DEFAULT CURRENT_DATE,
                        time_in        TIME DEFAULT CURRENT_TIME,
                        time_out       TIME NULL
                    );
                """)
            conn.commit()