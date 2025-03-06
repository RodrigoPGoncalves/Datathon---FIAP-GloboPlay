import time
import mlflow
import fasttext
import fasttext.util
import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os
import concurrent.futures

#mlflow.set_tracking_uri("http://localhost:5000")
#mlflow.set_experiment("News Recommendation")

class FastText:
    def __init__(self, obj_news_table):
        self.model = None
        self.obj_news_table = obj_news_table
        #1 Acesso ao users_preProcess db para pegar o history do id do usuário que entrou
        #2 Acesso ao news_preProcess para pegar através dos ids do history qual o texto (preprocesstext) de que será usado para a similaridade
        #3 Carregar os embedding já ajustados armazenados no db de embeding (tfidf, fasttext, bert)
        #Fazer similaridade 2 e 3
        #retirar os ids que ele já leu
        #apresentar dados



    def load_fasttext_model(self):
        if self.model is None:
            path = "./models/cc.pt.300.bin"
            if os.path.exists(path):
                self.model = fasttext.load_model(path)
            else:
                fasttext.util.download_model('pt', if_exists='ignore')
        return self.model

    def get_model(self):
        return self.load_fasttext_model()

    def create_embedding_chunk(self, chunk):
        cleaned_chunk = [news.replace('\n', ' ') for news in chunk]  # Remove as quebras de linha
        return [self.model.get_sentence_vector(news) for news in cleaned_chunk]

    def create_embeddings_parallel(self, noticias: list):
        chunk_size = max(1, len(noticias) // 4)  
        chunks = [noticias[i:i + chunk_size] for i in range(0, len(noticias), chunk_size)]
        
        embeddings = []
        
        # Usando múltiplos processos para gerar os embeddings
        with concurrent.futures.ProcessPoolExecutor() as executor:
            results = executor.map(self.create_embedding_chunk, chunks)
        
        # Juntando todos os resultados
        for result in results:
            embeddings.extend(result)
        
        return np.array(embeddings)

    def recommend(self, user_id):
        with mlflow.start_run(run_name="FastText_Recommender"):
            start_time = time.time()
            self.model = self.get_model()
            
            history_user = self.take_history_acess_user()

            user_embeddings = np.array([self.model.get_sentence_vector(n) for n in history_user])
            similaridades = cosine_similarity(user_embeddings, self.embeddings)

            # Pegar as top 3 recomendações para cada notícia do usuário
            recommended_news = []
            for user_sim in similaridades:
                top_indices = user_sim.argsort()[-3:][::-1]
                recommended_news.append([(self.noticias[i], user_sim[i]) for i in top_indices])

            elapsed_time = time.time() - start_time
            mlflow.log_metric("tempo_recomendacao", elapsed_time)
            mlflow.log_param("modelo", "FastText")

        return recommended_news