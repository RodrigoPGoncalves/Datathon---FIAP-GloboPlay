import pandas as pd
import re
import spacy
import os
import string
import nltk
from nltk.corpus import stopwords
from multiprocessing import Pool
from datetime import datetime
import math

class preProcessFiles():

    def __init__(self):
        self.list_columns_with_same_size = ['history', 'timestampHistory', 'numberOfClicksHistory', 
                                'timeOnPageHistory', 'scrollPercentageHistory', 'pageVisitsCountHistory']
        
        self.scroll_threshold=10 #Em %
        self.min_time_threshold=10000 #Em ms
        self.max_time_threshold=1000000 #Em ms
        self.max_click_in_page_threshold = 200 #Numero de cliques
        self.min_value_weighted_engagement = 0.1
        self.pesos = {
            'timeOnPageHistory': 0.3,
            'scrollPercentageHistory': 0.3,
            'numberOfClicksHistory': 0.2,
            'pageVisitsCountHistory': 0.2
        }
        
        self.nlp = spacy.load("pt_core_news_md", disable=["ner", "parser"])
        nltk.download("stopwords", download_dir="./models")
        self.stopwords_pt = set(stopwords.words('portuguese'))
        
            


    def run_pre_process(self, df, value):
        if(value):
            new_df = self.process_users(df)
        else:
            new_df = self.process_news(df)

        return new_df

    def process_users(self, df):
        df = self.clear_dataframes(df)
        df = self.ajusting_types(df, True)
        df = df[df.apply(self.length_users_columns_validate, axis=1)]
        df["weightedEngagement"] = df.apply(self.calc_weighted_engagement,axis=1)
        df = df.apply(self.clean_users_variables_data, axis=1)
        df = df.drop(columns=["timestampHistory" ,
                                "numberOfClicksHistory" ,
                                "timeOnPageHistory" ,
                                "scrollPercentageHistory" ,
                                "pageVisitsCountHistory" ,
                                "userType" ,
                                "historySize"])
        df = df.dropna()
        
        return df
    
    def process_news(self, df):
        df = df.drop(columns=['issued', 'modified','body'])
        df = self.clear_dataframes(df)
        df = self.ajusting_types(df, False)
        text_data = (df["title"] + " " + df["caption"]).tolist()
        df["processed_text"] = self.process_in_parallel(text_data)
        return df

    def clear_dataframes(self, df:pd.DataFrame):
        df = df.dropna()
        df = df.drop_duplicates()
        if("timestampHistory_new" in df.columns):
            df = df.drop(columns=["timestampHistory_new"])
        return df
    
    def convert_to_list(self,value, dtype):
        if pd.isna(value) or value == '':
            return []
        return list(map(dtype, value.split(',')))

    def ajusting_types(self,df:pd.DataFrame, value):
        if(value):
            df['userId'] = df['userId'].astype('string')
            df['userType'] = df['userType'].astype('category')
            df['historySize'] = df['historySize'].astype('Int64')
            df['history'] = df['history'].apply(lambda x: self.convert_to_list(x, str))      
            df['timestampHistory'] = df['timestampHistory'].apply(lambda x: self.convert_to_list(x, int))
            df['numberOfClicksHistory'] = df['numberOfClicksHistory'].apply(lambda x: self.convert_to_list(x, int))
            df['timeOnPageHistory'] = df['timeOnPageHistory'].apply(lambda x: self.convert_to_list(x, int))
            df['scrollPercentageHistory'] = df['scrollPercentageHistory'].apply(lambda x: self.convert_to_list(x, float))
            df['pageVisitsCountHistory'] = df['pageVisitsCountHistory'].apply(lambda x: self.convert_to_list(x, int))
        else:
            df['page'] = df['page'].astype('string')  
            df['url'] = df['url'].astype('string') 
            df['title'] = df['title'].astype('string')  
            df['caption'] = df['caption'].astype('string')  
            
        return df
    
    def length_users_columns_validate(self,row):
        history_size = row['historySize']
        return all(len(row[col]) == history_size for col in self.list_columns_with_same_size)

    def ms_to_hours(self, milliseconds):
        return milliseconds / (1000 * 60 * 60)

    def calc_decay(self,tempo_em_horas):
        return max(math.exp(-0.01 * tempo_em_horas), 0.00001)

    def calc_weighted_engagement(self,row):
        weighted_engagements = []
        
        for i in range(len(row['timeOnPageHistory'])):
            engagement_score = (
                row['timeOnPageHistory'][i] * self.pesos['timeOnPageHistory'] +
                row['scrollPercentageHistory'][i] * self.pesos['scrollPercentageHistory'] +
                row['numberOfClicksHistory'][i] * self.pesos['numberOfClicksHistory'] +
                row['pageVisitsCountHistory'][i] * self.pesos['pageVisitsCountHistory']
            )
            
            tempo_em_horas = self.ms_to_hours(row['timestampHistory'][i])
            decay = self.calc_decay(tempo_em_horas)
            weighted_engagement = engagement_score * decay
            weighted_engagements.append(round(weighted_engagement, 3))
        
        return weighted_engagements

    def clean_users_variables_data(self, row):
        #Excluindo timeOnPageHistory < 10s
        #Excluindo timeOnPageHistory > 1000s (Pois o usuário pode ter deixado aberto e esquecido)
        #Excluindo Baixa acertividade na noticia baseado no interesse do srool
        delete_index = [i for i, (scrollInPage, timeInPage, clickInPage, weigthInPage) in enumerate(zip(row['scrollPercentageHistory'], row['timeOnPageHistory'], row['numberOfClicksHistory'], row['weightedEngagement'] ))
                        if  (scrollInPage < self.scroll_threshold) or 
                            (scrollInPage >= self.scroll_threshold and timeInPage < self.min_time_threshold) or
                            (timeInPage > self.max_time_threshold) or
                            (clickInPage > self.max_click_in_page_threshold) or
                            (weigthInPage < self.min_value_weighted_engagement)]
        if len(delete_index) > 0:

            if len(delete_index) == len(row['timeOnPageHistory']):
                return pd.Series()

            for col in self.list_columns_with_same_size:
                row[col] = [line for i, line in enumerate(row[col]) if i not in delete_index]

            row['historySize'] = int(row['historySize'] - len(delete_index))

        return row
    

    def remove_accent(self,text):
        return re.sub(r"[áàãâäéèêëíìîïóòôõöúùûüç]", 
                    lambda m: "aaaaaeeeeiiiiooooouuuuc"["áàãâäéèêëíìîïóòôõöúùûüç".index(m.group())], 
                    text)

    def remove_emojis(self, text):
        emoji_pattern = re.compile("[\U00010000-\U0010ffff]", flags=re.UNICODE)
        return emoji_pattern.sub(r"", text)

    def remove_line_breaks(self, text):
        return re.sub(r"[\n\t\r]+", " ", text).strip()
    
    def preprocess_text(self, text):
        if pd.isna(text) or not isinstance(text, str):  
            return text

        text = self.remove_accent(text.lower())
        #text = self.remove_emojis(text)  # Remove emojis
        #text = self.remove_line_breaks(text)  # Remove \n, \t, etc.
        text = re.sub(r"\d+º?", "", text)  # Remove números com ou sem o símbolo de grau

        # Tokenização + remoção de stopwords e pontuação
        doc = self.nlp(text)
        tokens = [token.text for token in doc if token.text not in self.stopwords_pt and token.text not in string.punctuation]

        return " ".join(tokens)
    
    def process_in_parallel(self, data, num_workers=None):
        if num_workers is None:
            num_workers = max(1, os.cpu_count() - 1)  # Usa todas as CPUs menos 1

        with Pool(num_workers) as pool:
            processed_texts = pool.map(self.preprocess_text, data)

        return processed_texts
    