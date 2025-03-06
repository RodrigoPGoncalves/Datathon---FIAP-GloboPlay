from dbSqlite.database import Database

class table_users_origin:
    def __init__(self, db_path):
        self.database = Database(db_path)
        self.create_users_info_table()

    def create_users_info_table(self):
        """Cria a tabela 'users_origin'"""
        query = '''
        CREATE TABLE IF NOT EXISTS users_origin (
            userId TEXT PRIMARY KEY,
            userType TEXT,
            historySize INTEGER,
            history TEXT,
            timestampHistory TEXT,
            numberOfClicksHistory TEXT,
            timeOnPageHistory TEXT,
            scrollPercentageHistory TEXT,
            pageVisitsCountHistory TEXT,
            timestampHistory_new TEXT
        );
        '''
        with self.database.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()

    def insert_bacth_info(self, user_data_list):
        """Insere ou atualiza dados na tabela 'users_origin' em lotes"""
        with self.database.connect() as conn:
            cursor = conn.cursor()
            cursor.executemany('''
                INSERT OR REPLACE INTO users_origin (userId, userType, historySize, history, timestampHistory, 
                numberOfClicksHistory, timeOnPageHistory, scrollPercentageHistory, pageVisitsCountHistory, timestampHistory_new)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', user_data_list)
            conn.commit()

    def insert_user_info(self, user_data):
        """Insere ou atualiza dados na tabela 'users_origin'"""
        with self.database.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO users_origin (userId, userType, historySize, history, timestampHistory, 
                numberOfClicksHistory, timeOnPageHistory, scrollPercentageHistory, pageVisitsCountHistory, timestampHistory_new)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', user_data)
            conn.commit()

    def fetch_all_users(self):
        """Busca todos os registros da tabela 'users_origin'"""
        with self.database.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users_origin")
            return cursor.fetchall()

    def delete_user_info(self, userId):
        """Deleta um registro da tabela 'users_origin'"""
        with self.database.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users_origin WHERE userId = ?", (userId,))
            conn.commit()

    