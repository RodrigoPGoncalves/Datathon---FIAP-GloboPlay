import streamlit as st
import pandas as pd
import requests
import time

API_URL = "http://127.0.0.1:8000/"

def grafico_predict(json_value):
    df_cmin3_test_model = pd.DataFrame(json_value['df_cmin3_test_model'])
    df_cmin3_test_model['Date'] = pd.to_datetime(df_cmin3_test_model['Date'])

    date_predict = pd.to_datetime(json_value['date_predict'])

    # Criando o gráfico interativo
    fig = go.Figure()

    # Adicionando os dados históricos
    fig.add_trace(go.Scatter(
        x=df_cmin3_test_model['Date'],
        y=df_cmin3_test_model['close_cmin3'],
        mode='lines+markers',
        name='Dados Históricos',
        line=dict(color='blue')
    ))

    # Adicionando previsões
    fig.add_trace(go.Scatter(
        x=date_predict,
        y=json_value['predict_sample_lstm'],
        mode='lines+markers',
        name='Previsão LSTM',
        line=dict(color='orange')
    ))

    fig.add_trace(go.Scatter(
        x=date_predict,
        y=json_value['predict_lstm_bidirecional'],
        mode='lines+markers',
        name='Previsão LSTM Bidirecional',
        line=dict(color='red')
    ))

    fig.add_trace(go.Scatter(
        x=date_predict,
        y=json_value['predict_lstm_attention'],
        mode='lines+markers',
        name='Previsão LSTM + Attention',
        line=dict(color='gray')
    ))

    fig.add_trace(go.Scatter(
        x=date_predict,
        y=json_value['predict_lstm_cnn'],
        mode='lines+markers',
        name='Previsão LSTM + CNN',
        line=dict(color='green')
    ))

    fig.add_trace(go.Scatter(
        x=date_predict,
        y=json_value['predict_lstm_bi_atten_cnn'],
        mode='lines+markers',
        name='Previsão LSTM Bi-Attention + CNN',
        line=dict(color='pink')
    ))

    # Customizando o layout
    fig.update_layout(
        title='Previsões de Preço de Fechamento',
        xaxis_title='Datas',
        yaxis_title='Preço de Fechamento',
        legend_title='Modelos',
        template='plotly_white'
    )

    # Exibindo o gráfico no Streamlit
    st.plotly_chart(fig)

def app():
    st.header("""Trabalho Fase 5 - FIAP + GLOBO""")
    st.write("""
                O intuito deste trabalho é realizar recomendações de noticias baseado nos dados fornecidos pela globo.
            """)
    st.write("""Neste Trabalho foi considerado dois tipos de usuários, aqueles cujo o user_id é sábido e aqueles que são considerados como
              cold-start (primeira vez que entam no site ou acima de trinta dias dias e portanto perderam o hash).
             """)
    st.write("""O modelo escolhido para ser utilizados foi o TF-IDF, escolhi esse modelo pela facilidade de se trabalahr, alem de sua agilidade 
             na construção e interferencia do modelo. Em muitos locais de pesquisa, apesar da alta recomendação de modelos pré treinados, muitos 
             informam que mesmo antiga tal métrica funciona muito bem, comparado aos modelos mais modernos, des de que continue sendo treinada com
             dados novos sempre que necessário. Para acompanhar a interferencia foi utilizado o mlflow que se encontra no endereço http://127.0.0.1:5000/
             """)
    st.write("""A priori foi realizado todo o pré processamento dos dados. Para os dados de usuários, foi utilizado uma verificação de tamanho das listas contidas
              em algumas das colunas já que devem possuir o mesmo tamanho, também foram retirardas duplicatas e campos nulos, como de costume, alem de retiradas notícias da coluna history
             de forma a excluir aquelas que não eram consideradas uteis, da seguinte forma:
            """)
    st.markdown("""
                - scrollPercentageHistory < 10%
                - timeOnPageHistory < 10s
                - timeOnPageHistory > 1000s
                - numberOfClicksHistory > 200
                """)
    st.write("""Para as escolhas de valores acima, foi levado uma analise do conjunto de dados iniciais alem das imagens mostradas abaixo
            """)
    
    if 'show_image' not in st.session_state:
        st.session_state.show_image = False

    if st.button("Mostrar/Ocultar Imagens"):
        st.session_state.show_image = not st.session_state.show_image

    if st.session_state.show_image:
        st.image("./figures/boxplot_metrica_usuario.png", caption="BoxPlot Métricas do usuário")
        st.image("./figures/relation_time_and_clicks.png", caption="Relação TimeInPage e Clicks")
        st.image("./figures/relation_time_and_scroll.png", caption="Relação TimeInPage e Scroll")
    
    st.write("""Para garantir melhores dados também utilizei de técnicas de pesos baseada no histórico de noticias do usuário, portanto as informações de
              quantidade de clicks, scrool tempo na pagina foram utilizadas de forma a melhorar a resposta do modelo, além de também considerar
              em prevalecer recomendações de noticias mais novas sempre que possível.Os pesos considerados para os calculos pode ser vistos abaixo:
              abaixo:
            """)
    st.markdown("""
                - timeOnPageHistory: 0.3
                - scrollPercentageHistory: 0.3
                - numberOfClicksHistory: 0.2
                - pageVisitsCountHistory: 0.2
                """)
    st.write("""Aproveitando ainda mais a técnica acima, também considerei um valor minimo do somatório desses pesos, portanto, noticias com engajamento 
             abaixo de 0.1 foram retiradas no pré processamento
            """)
    
    #st.subheader("LEMBRETE: APESAR DO BOTÃO DE RECARREGAR DADOS ESTAR ABAIXO, NÃO RECOMENDO, POIS O PRÉ PROCESSAMENTO DOS DADOS ESTÁ BEM PESADO.")

        
    if st.button("Treinar TF-IDF"):
        with st.spinner("Carregando, aguarde..."):
            try:
                response = requests.get(
                    API_URL + "train_tfidf",
                    timeout=60 
                )
                if response.status_code == 200:
                    st.success("TF-IDF Treinado com sucesso")
                else:
                    error_message = response.json().get("message", "Erro desconhecido ao processar a requisição.")
                    st.error(f"Erro na API: {error_message}")
            except requests.exceptions.RequestException as e:
                st.error(f"Erro ao conectar com a API: {str(e)}")


    tab1, tab2= st.tabs(["ID encontrado", "Cold-Start"])
    with tab1:
        if "id_usuario" not in st.session_state:
            st.session_state.id_usuario = None 

        if st.session_state.id_usuario is None:
            with st.spinner("Carregando ID..."):
                try:
                    response = requests.get(API_URL + "random_user_id", timeout=10)
                    if response.status_code == 200:
                        st.session_state.id_usuario = response.json().get("userId")
                    else:
                        error_message = response.json().get("message", "Erro desconhecido ao processar a requisição.")
                        st.error(f"Erro na API: {error_message}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Erro ao conectar com a API: {str(e)}")

        st.header("Seu ID: ")
        st.write(st.session_state.get("id_usuario", ""))

        if "noticias_lidas" not in st.session_state:
            st.session_state.noticias_lidas = []

        # Armazena as notícias lidas no session_state
        if not st.session_state.noticias_lidas:
            with st.spinner("Carregando Notícias..."):
                try:
                    response = requests.get(f"{API_URL}history?userID={st.session_state.id_usuario}", timeout=10)
                    if response.status_code == 200:
                        st.session_state.noticias_lidas = response.json().get("newsLink")
                    else:
                        error_message = response.json().get("message", "Erro desconhecido ao processar a requisição.")
                        st.error(f"Erro na API: {error_message}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Erro ao conectar com a API: {str(e)}")

        st.header("Links com as suas notícias já lidas: ")
        
        noticias_lidas = st.session_state.noticias_lidas
        items_per_page = 5  # Número de notícias por página
        page_number = st.number_input("Página", min_value=1, max_value=(len(noticias_lidas) // items_per_page) + 1, value=1)

        if noticias_lidas:
            start = (page_number - 1) * items_per_page
            end = start + items_per_page
            for link in noticias_lidas[start:end]:
                st.markdown(f"- [{link}]({link})")
        else:
            st.write("Nenhum link encontrado.")

        # Seção de recomendação
        st.header("Notícias recomendadas:")

        if "noticias_recomendadas_tfidf" not in st.session_state:
            st.session_state.noticias_recomendadas_tfidf = []

        if "noticias_recomendadas_fastText" not in st.session_state:
            st.session_state.noticias_recomendadas_fastText = []

        # Função genérica para recomendar notícias
        def recomendar_noticias(metodo):
            if len(st.session_state.noticias_lidas) == 0:
                st.error("É necessário ter um histórico maior que zero para recomendação")
                return

            with st.spinner(f"Carregando recomendações usando {metodo}..."):
                try:
                    response = requests.get(
                        API_URL + f"{metodo}recomendation",  # Endpoint da API
                        timeout=30
                    )
                    if response.status_code == 200:
                        if metodo == "tfidf":
                            st.session_state.noticias_recomendadas_tfidf = response.json().get("newsLink", [])
                        elif metodo == "fastText":
                            st.session_state.noticias_recomendadas_fastText = response.json().get("newsLink", [])
                        st.success("Recomendações carregadas com sucesso!")
                    else:
                        error_message = response.json().get("message", "Erro desconhecido ao processar a requisição.")
                        st.error(f"Erro na API: {error_message}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Erro ao conectar com a API: {str(e)}")

        # Botões para recomendar notícias

        if st.button("Recomendar TF-IDF"):
            recomendar_noticias("tfidf")


        # Exibir notícias recomendadas em colunas
        if st.session_state.noticias_recomendadas_tfidf or st.session_state.noticias_recomendadas_fastText:
                if st.session_state.noticias_recomendadas_tfidf:
                    st.markdown("**Recomendações TF-IDF**")
                    for link in st.session_state.noticias_recomendadas_tfidf:
                        st.markdown(f"- [{link}]({link})")
                else:
                    st.info("Nenhuma notícia recomendada por TF-IDF ainda.")
        else:
            st.info("Use o botão acima para gerar recomendações.")

    with tab2:
        st.header("Cold Start")
        
        
    

if __name__ == "__main__":
    app()