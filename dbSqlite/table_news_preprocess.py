from dbSqlite.database import Database
import pandas as pd

class table_news_preprocess:
    def __init__(self, db_path):
        self.database = Database(db_path)
        self.create_preprocess_news_table()

    def create_preprocess_news_table(self):
        """Cria a tabela 'preprocess_news'"""
        query = '''
        CREATE TABLE IF NOT EXISTS news_preprocess (
            page TEXT PRIMARY KEY,
            url TEXT,
            title TEXT,
            caption TEXT,
            preprocesstext TEXT
        );
        '''
        with self.database.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()

    def insert_bacth_info(self, user_data_list):
        """Insere ou atualiza dados na tabela 'news_preprocess' em lotes"""
        with self.database.connect() as conn:
            cursor = conn.cursor()
            cursor.executemany('''
                INSERT OR REPLACE INTO news_preprocess (page, url, title, 
                caption, preprocesstext)
                VALUES (?, ?, ?, ?, ?)
            ''', user_data_list)
            conn.commit()

    def insert_batch_specific_column(self, column_name, column_data):
        """Insere ou atualiza uma coluna específica na tabela 'news_preprocess' em lotes"""
        with self.database.connect() as conn:
            cursor = conn.cursor()
            cursor.executemany(f'''
                        INSERT OR REPLACE INTO news_preprocess (id, {column_name})
                        VALUES (?, ?)
                    ''', column_data)
            conn.commit()

    def insert_preprocess_news_info(self, news_data):
        """Insere ou atualiza dados na tabela 'news_preprocess'"""
        with self.database.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''lite.
                INSERT OR REPLACE INTO news_preprocess (page, url, title, 
                caption, preprocesstext)
                VALUES (?, ?, ?, ?, ?)
            ''', news_data)
            conn.commit()

    def fetch_all_preprocessed_news(self):
        """Busca todos os registros da tabela 'news_preprocess'"""
        with self.database.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM news_preprocess")
            return cursor.fetchall()

    def delete_preprocessed_news_info(self, page):
        """Deleta um registro da tabela 'news_preprocess'"""
        with self.database.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM news_preprocess WHERE page = ?", (page,))
            conn.commit()

    def get_news_links_with_id(self,id_list):
        """Retorna o link da noticia dado o id"""
        with self.database.connect() as conn:
            cursor = conn.cursor()
            results = []
            for i in range(0, len(id_list), 20):
                batch = id_list[i:i + 20]
                query = f"""
                    SELECT url FROM news_preprocess
                    WHERE page IN ({','.join(['?'] * len(batch))})
                """
                cursor.execute(query, batch)
                results.extend(cursor.fetchmany(20))

        return [row[0] for row in results]
    
    def get_column(self, col):
        with self.database.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT {col} FROM news_preprocess") 
            result = cursor.fetchone()
            return result[0] if result else ""
        
    def embedding_tf_idf_return_news_read(self, id_list):
        """Retorna o embbeding da lista de ids de noticias"""
        with self.database.connect() as conn:
            cursor = conn.cursor()
            results = []

            for i in range(0, len(id_list), 20):
                batch = id_list[i:i + 20]
                query = f"""
                    SELECT preprocesstext FROM news_preprocess
                    WHERE page IN ({','.join(['?'] * len(batch))})
                """
                cursor.execute(query, batch)
                results.extend(cursor.fetchmany(20))

        return [row[0] for row in results]
    
    def embedding_tf_idf_return_news_unread(self, id_list):
        """Retorna o embbeding do que NAO está na lista de ids de noticias"""
        with self.database.connect() as conn:
            cursor = conn.cursor()
            results = []
            query = f"""
                SELECT preprocesstext, url FROM news_preprocess
                WHERE page NOT IN ({','.join(['?'] * len(id_list))})
            """
            cursor.execute(query, id_list)
            results = cursor.fetchall()

        df = pd.DataFrame(results, columns=['preprocesstext', 'url'])

        return df
    
    def df_all_notices(self):
        """Retorna o embbeding do que NAO está na lista de ids de noticias"""
        with self.database.connect() as conn:
            cursor = conn.cursor()
            results = []
            query = f"""
                SELECT preprocesstext, url FROM news_preprocess
            """
            cursor.execute(query)
            results = cursor.fetchall()

        df = pd.DataFrame(results, columns=['preprocesstext', 'url'])

        return df
    