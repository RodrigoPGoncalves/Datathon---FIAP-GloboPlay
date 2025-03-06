# Projeto de Recomendação de Notícias

Este projeto é uma aplicação que utiliza técnicas de machine learning (TF-IDF e FastText) para recomendar notícias personalizadas com base no histórico de engajamento dos usuários. A aplicação é composta por:

- **FastAPI**: Para fornecer endpoints de API.
- **Streamlit**: Para criar uma interface web interativa.
- **MLflow**: Para monitorar experimentos de machine learning.
- **SQLite**: Para armazenar dados de usuários e notícias.

## Funcionalidades

1. **Recomendação de Notícias**:
   - Utiliza o modelo TF-IDF para gerar recomendações personalizadas.
   - Considera o histórico de notícias lidas e o engajamento do usuário (cliques, tempo na página, scroll, etc.).

2. **Interface Web**:
   - Interface interativa criada com Streamlit para visualizar notícias recomendadas e histórico de leitura.

3. **Monitoramento**:
   - Uso do MLflow para monitorar e comparar os resultados dos modelos de machine learning.

4. **Banco de Dados**:
   - Armazenamento de dados de usuários e notícias em um banco SQLite.

# Estrutura do Projeto
```
├── routes/ # Endpoints da API (FastAPI)
│ └── routes.py
├── streamlitPages/ # Páginas da interface web (Streamlit)
│ └── initial_page.py
├── dbSqlite/ # Código para interação com o banco SQLite
├── preProcess/ # Código para pré-processamento de dados
├── tfIDF/ # Implementação do modelo TF-IDF
├── fastText/ # Implementação do modelo FastText
├── requirements.txt # Dependências do projeto
├── Dockerfile # Configuração do Docker
└── README.md # Este arquivo
```

## Pré-requisitos

- Python 3.10 ou superior.
- Docker (opcional, para rodar em containers).

## Como Executar

### 1. Configuração do Ambiente

Clone o repositório:
```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```

Crie um ambiente virtual (opcional, mas recomendado):
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

Instale as dependências:
```bash
pip install -r requirements.txt
```
Acesse as interfaces:

### 2. Executando Localmente
Digite no terminal (dentro da pasta):
```bash
python __init__.py
```

OU

Inicie o FastAPI:

```bash
uvicorn routes.routes:app --host 0.0.0.0 --port 8000
```

Inicie o Streamlit:
```bash
streamlit run streamlitPages/initial_page.py
```
Inicie o MLflow:
```bash
mlflow ui
```

Acesse as interfaces:

FastAPI: http://localhost:8000

Streamlit: http://localhost:8501

MLflow: http://localhost:5000

### 3. Executando com Docker
Construa a imagem Docker:

```bash
docker build -t minha-aplicacao .
```
Rode o container:
```bash
docker run -p 8000:8000 -p 8501:8501 -p 5000:5000 minha-aplicacao
```

FastAPI: http://localhost:8000

Streamlit: http://localhost:8501

MLflow: http://localhost:5000

## Endpoints da API (FastAPI)
GET /: Mensagem de boas-vindas.

GET /random_user_id: Retorna um ID de usuário aleatório.

GET /history: Retorna o histórico de notícias lidas por um usuário.

GET /train_tfidf: Treina o modelo TF-IDF.

GET /tfidfrecomendation: Retorna recomendações de notícias usando TF-IDF.

## Contribuição
Faça um fork do projeto.

Crie uma branch para sua feature (git checkout -b feature/nova-feature).

Commit suas mudanças (git commit -m 'Adicionando nova feature').

Push para a branch (git push origin feature/nova-feature).

Abra um Pull Request.

## Licença
Este projeto está licenciado sob a MIT License. Veja o arquivo LICENSE para mais detalhes.
