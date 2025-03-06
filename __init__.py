import pandas as pd
import os
import json
import subprocess
import time
import sys
from dbSqlite.table_users_origin import table_users_origin
from dbSqlite.table_news_origin import table_news_origin
from dbSqlite.table_users_preprocess import table_users_preprocess
from dbSqlite.table_news_preprocess import table_news_preprocess
import preProcess.preProcessFiles as pre_process


def read_origin_files(path_users_info,path_news_info):
    df_return = []
    for path in [path_users_info, path_news_info]:
        dataframes = []
        for file in os.listdir(path):
            caminho_arquivo = os.path.join(path, file)
            if file.endswith(".csv"):
                df = pd.read_csv(caminho_arquivo)
                dataframes.append(df)
        df_return.append(pd.concat(dataframes, ignore_index=True))
    return df_return[0], df_return[1]

def send_df_in_batch_to_db(df,table, value=False):
    batch_size = 10000
    if(value): #convertendo dados de lista para string para serem armazenados no db
        cols_to_convert = ["history","weightedEngagement"]
        
        df[cols_to_convert] = df[cols_to_convert].applymap(json.dumps)

    values = df.values.tolist()
    for i in range(0, len(values), batch_size):
        batch = values[i:i+batch_size]
        table.insert_bacth_info(batch)

def send_df_col_in_batch_to_db(df,table):
    batch_size = 10000
    values = df.values.tolist()
    for i in range(0, len(values), batch_size):
        batch = values[i:i+batch_size]
        table.insert_batch_specific_column(batch)

def read_process_save(obj_pp, obj_table_users_origin, obj_table_news_origin, obj_table_users_preprocess, obj_table_news_preprocess):
    # Lê arquivos
    path_users_info = 'Files/files/treino'
    path_news_info = 'Files/itens/itens'
    df_users_info, df_news_info = read_origin_files(path_users_info, path_news_info)

    #Armazena dados originais no db
    #send_df_in_batch_to_db(df_users_info, obj_table_users_origin)
    #send_df_in_batch_to_db(df_news_info, obj_table_news_origin)
    
    # Processar e inserir dados no db
    df_users_info_preprocess = obj_pp.run_pre_process(df_users_info, True)
    send_df_in_batch_to_db(df_users_info_preprocess, obj_table_users_preprocess, True)

    
    df_news_info_preprocess = obj_pp.run_pre_process(df_news_info, False)
    send_df_in_batch_to_db(df_news_info_preprocess, obj_table_news_preprocess)
    

def train_tf_idf(obj_tf_idf,news):
    tfidf_matrix = obj_tf_idf.train_model(news["preprocesstext"])
    embedding_vectors = []
    for i in range(tfidf_matrix.shape[0]):
        embedding_vector = tfidf_matrix[i].toarray().flatten()  # Converte para vetor 1D
        embedding_vectors.append(embedding_vector)
    news["embeddings_tfidf"] = embedding_vectors
    send_df_col_in_batch_to_db(news[["page","embeddings_tfidf"]])


def train_fast_text(obj_fast_text, news):
    array = obj_fast_text.create_embeddings_parallel(news["preprocesstext"].tolist())
    news["embeddings_fasttext"] = list(array)
    send_df_col_in_batch_to_db(news[["page","embeddings_fasttext"]])
    

def run_read_process_save_train(obj_pp,
                                obj_table_users_origin,
                                obj_table_news_origin,
                                obj_table_users_preprocess,
                                obj_table_news_preprocess):
    read_process_save(obj_pp, obj_table_users_origin, obj_table_news_origin, obj_table_users_preprocess, obj_table_news_preprocess)

import requests
import time



def run_fastapi():
    subprocess.Popen([sys.executable, 'routes/routes.py']) 

def run_streamlit():
    subprocess.Popen(['streamlit', 'run', 'streamlitPages/initial_page.py'])

def run_mlflow():
    subprocess.Popen(['mlflow', 'ui']) 


def main():    
    # Iniciando DB
    db_path = 'database.db'

    obj_table_users_origin = table_users_origin(db_path)
    obj_table_news_origin = table_news_origin(db_path)
    obj_table_users_preprocess = table_users_preprocess(db_path)
    obj_table_news_preprocess = table_news_preprocess(db_path)

    #Criando Objetos
    obj_pp = pre_process.preProcessFiles()
    run_read_process_save_train(obj_pp, obj_table_users_origin, obj_table_news_origin, obj_table_users_preprocess, obj_table_news_preprocess)
    

if __name__ == '__main__':

    os.system("fuser -k 5000/tcp")
    os.system("fuser -k 8000/tcp")
    os.system("fuser -k 8501/tcp")
    #main()
    run_mlflow()
    run_fastapi()
    time.sleep(20)
    run_streamlit()
    

    print("Todos os serviços estão rodando...")
    print("Fast API em: http://127.0.0.1:8000/")
    print("Streamlit em: http://127.0.0.1:8501/")
    print("Mlflow em: http://127.0.0.1:5000/")