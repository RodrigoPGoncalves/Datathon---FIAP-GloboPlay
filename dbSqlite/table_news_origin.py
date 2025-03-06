from dbSqlite.database import Database

class table_news_origin:
    def __init__(self, db_path):
        self.database = Database(db_path)
        self.create_news_info_table()

    def create_news_info_table(self):
        """Cria a tabela 'news_origin'"""
        query = '''
        CREATE TABLE IF NOT EXISTS news_origin (
            page TEXT PRIMARY KEY,
            url TEXT,
            issued TEXT,
            modified TEXT,
            title TEXT,
            body TEXT,
            caption TEXT
        );
        '''
        with self.database.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()

    def insert_bacth_info(self, user_data_list):
        """Insere ou atualiza dados na tabela 'news_origin' em lotes"""
        with self.database.connect() as conn:
            cursor = conn.cursor()
            cursor.executemany('''
                INSERT OR REPLACE INTO news_origin (page, url, issued, modified, title, 
                body, caption)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', user_data_list)
            conn.commit()

    def insert_news_info(self, news_data):
        """Insere ou atualiza dados na tabela 'news_origin'"""
        with self.database.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO news_origin (page, url, issued, modified, title, body, caption)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', news_data)
            conn.commit()

    def fetch_all_news(self):
        """Busca todos os registros da tabela 'news_origin'"""
        with self.database.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM news_origin")
            return cursor.fetchall()

    def delete_news_info(self, page):
        """Deleta um registro da tabela 'news_origin'"""
        with self.database.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM news_origin WHERE page = ?", (page,))
            conn.commit()

    