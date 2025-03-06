from fastapi import FastAPI,HTTPException, APIRouter
from typing import List
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel
import sys
import os   
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import dbSqlite.table_users_preprocess as table_users_preprocess
import dbSqlite.table_news_preprocess as table_news_preprocess
from typing import Optional
import json
import tfIDF.tfidf as tf_idf
import ast

app = FastAPI()

class LastValuesManager:
    def __init__(self):
        self.lastHistory = []
        self.engagement_list = []

    def set_last_history(self, history):
        self.lastHistory = history

    def get_last_history(self):
        return self.lastHistory
    
    def set_last_engagement_list(self, engagement_list):
        self.engagement_list = engagement_list

    def get_last_engagement_list(self):
        return self.engagement_list
    

db_path = 'database.db'
user_table = table_users_preprocess.table_users_preprocess(db_path)
news_table = table_news_preprocess.table_news_preprocess(db_path)

obj_tf_idf = tf_idf.TfIDF(news_table)

last_values_manager = LastValuesManager()



@app.get("/")
async def root():
    return {"message":"Bem vindo a API de previsão da ação CMIN3."}

@app.get("/random_user_id")
async def random_user_id():
    userID = user_table.get_random_user_id()
    if(userID != None):
        return JSONResponse(
                status_code=200,  
                content={"userId": userID}
            )
    else:
        return JSONResponse(
                status_code=500,  
                content={"message": "Falha ao requisitar um user ID"}
            )


@app.get("/history")
async def history(userID: Optional[str] = None):
    if(userID != None):
        history, engagement_list = user_table.get_history_and_engagement_with_id(userID)
        if(history != [] and engagement_list != []):

            history = history.strip("[]")
            history_corrigidos = ast.literal_eval(history)
            history_corrigidos = [id.strip() for id in eval(history_corrigidos)]

            engagement_list = engagement_list.strip("[]")
            engagement_list = ast.literal_eval(engagement_list)

            last_values_manager.set_last_history(history_corrigidos)
            last_values_manager.set_last_engagement_list(engagement_list)
            
            newsLinks = news_table.get_news_links_with_id(history_corrigidos)
            print(newsLinks)
            return JSONResponse(
                    status_code=200,  
                    content={"newsLink": newsLinks}
                )
        else:
            last_values_manager.set_last_history([])
            last_values_manager.set_last_engagement_list([])
            return JSONResponse(
                status_code=422,  
                content={"message": "Falha ao requisitar o history"}
            )
    else:
        return JSONResponse(
                    status_code=422,  
                    content={"message": "User ID vazio"}
                )    

@app.get("/train_tfidf")
async def tfidfrecomendation():
    values, message_return = obj_tf_idf.train_model()
    if(values):
        return JSONResponse(
                status_code=200,  
                content={"newsLink": values}
            )
    else:
        return JSONResponse(
                status_code=500,  
                content={"message": message_return}
            )


@app.get("/tfidfrecomendation")
async def tfidfrecomendation():
    hist_noticias = last_values_manager.get_last_history()
    engagement_list = last_values_manager.get_last_engagement_list()
    if(hist_noticias != [] and engagement_list != []):
        message, values = obj_tf_idf.recommend(hist_noticias, engagement_list)
        if(values != []):
            return JSONResponse(
                    status_code=200,  
                    content={"newsLink": values}
                )
        else:
            return JSONResponse(
                    status_code=500,  
                    content={"message": f"Falha ao requisitar a recomendação: {message}"}
                )
    else:
        return JSONResponse(
                    status_code=422,  
                    content={"message":"History vazio, atualizar pagina"}
                )    



if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
