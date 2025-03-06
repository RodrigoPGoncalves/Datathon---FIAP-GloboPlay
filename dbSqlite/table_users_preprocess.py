from dbSqlite.database import Database

class table_users_preprocess:
    def __init__(self, db_path):
        self.database = Database(db_path)
        self.create_preprocess_users_table()

    def create_preprocess_users_table(self):
        """Cria a tabela 'users_preprocess'"""
        query = '''
        CREATE TABLE IF NOT EXISTS users_preprocess (
            userId TEXT PRIMARY KEY,
            history TEXT,
            weightedEngagement TEXT
        );
        '''
        

        with self.database.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()

    def insert_bacth_info(self, user_data_list):
        """Insere ou atualiza dados na tabela 'users_preprocess' em lotes"""
        with self.database.connect() as conn:
            cursor = conn.cursor()
            cursor.executemany('''
                INSERT OR REPLACE INTO users_preprocess (userId, history,weightedEngagement)
                VALUES (?, ?, ?)
            ''', user_data_list)
            conn.commit()

    def insert_preprocess_user_info(self, user_data):
        """Insere ou atualiza dados na tabela 'users_preprocess'"""
        with self.database.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO users_preprocess (userId, history,weightedEngagement)
                VALUES (?, ?, ?)
            ''', user_data)
            conn.commit()

    def fetch_all_preprocessed_users(self):
        """Busca todos os registros da tabela 'users_preprocess'"""
        with self.database.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users_preprocess")
            return cursor.fetchall()

    def delete_preprocessed_user_info(self, userId):
        """Deleta um registro da tabela 'users_preprocess'"""
        with self.database.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users_preprocess WHERE userId = ?", (userId,))
            conn.commit()

    def get_random_user_id(self):
        """Retorna um userId aleatório da tabela users_preprocess"""
        with self.database.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT userId FROM users_preprocess ORDER BY RANDOM() LIMIT 1;")
            result = cursor.fetchone()
            return result[0] if result else None 
    
    def get_history_and_engagement_with_id(self, id):
        """Retorna a lista de history baseado no id enviado"""
        with self.database.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                        SELECT history, weightedEngagement FROM users_preprocess
                        WHERE userId = ?
                        """, (id,)) 
            result = cursor.fetchone()
            print("Resultado")
            print(result)
            return result if result else (None,None)