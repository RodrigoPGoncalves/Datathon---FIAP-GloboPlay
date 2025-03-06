import time
import pickle
import mlflow
import numpy as np
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("News Recommendation")

class TfIDF:
    def __init__(self, obj_news_table):

        self.model_path = "./models/tfidf_model.pkl"
        self.obj_news_table = obj_news_table
        self.loaded_vectorizer = None

    def load_model(self):
        try:
            with open(self.model_path, "rb") as f:
                self.loaded_vectorizer = pickle.load(f)
                return True,""
        except:
            return False,"Necessário treinar modelo"

    def train_model(self):
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            vectorizer = TfidfVectorizer(stop_words="english", max_features=300)
            df_all_news = self.obj_news_table.df_all_notices()
            tfidf_matrix = vectorizer.fit_transform(df_all_news["preprocesstext"])
            with open(self.model_path, "wb") as f:
                self.loaded_vectorizer = vectorizer
                pickle.dump(vectorizer, f)
            return True,"Treinado com sucesso"
        except Exception as  e:
            return False,"Falha ao treinar: " + str(e)

    def recommend(self, history, engagement_list):
        """Recomenda notícias com base nas que o usuário já viu"""
        with mlflow.start_run(run_name="TFIDF_Recommender"):
            start_time = time.time()

            if(self.loaded_vectorizer == None):
                value, message = self.load_model()
                if(not value):
                    return message,[]                
                
            
            news_read = self.obj_news_table.embedding_tf_idf_return_news_read(history)
            news_unread = self.obj_news_table.embedding_tf_idf_return_news_unread(history)

            tfidf_matrix_read = self.loaded_vectorizer.transform(news_read)
            tfidf_matrix_not_read = self.loaded_vectorizer.transform(news_unread["preprocesstext"])

            user_profile = np.zeros(tfidf_matrix_read.shape[1])
            for idx, engagement in zip(range(tfidf_matrix_read.shape[0]), eval(engagement_list)):
                user_profile += tfidf_matrix_read[idx].toarray().flatten() * engagement
            
            user_profile /= np.linalg.norm(user_profile)

            similarity = cosine_similarity(tfidf_matrix_not_read, user_profile.reshape(1, -1))
            similarity_mean = similarity.mean(axis=1)

            news_unread['similarity_mean'] = similarity_mean
            recomendation = news_unread.sort_values(by='similarity_mean', ascending=False).head(5)
            recomendation_list = recomendation["url"].tolist()
            elapsed_time = time.time() - start_time

            # Logar métricas no MLflow
            mlflow.log_metric("tempo_recomendacao", elapsed_time)
            mlflow.log_metric("similaridade_media", recomendation['similarity_mean'].head(5).mean())
            mlflow.log_param("modelo", "TF-IDF")

            return "ok", recomendation_list
