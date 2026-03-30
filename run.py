from app.database import Database
from app import create_app

db = Database()
db.create_tables()

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)