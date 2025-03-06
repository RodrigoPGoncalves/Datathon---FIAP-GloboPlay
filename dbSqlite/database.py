import sqlite3
import os

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.create_database()

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row #NEcessário para acessar o db através de nome
        return conn

    def create_database(self):
        if not os.path.exists(self.db_path):
            with self.connect() as conn:
                cursor = conn.cursor()
                conn.commit()