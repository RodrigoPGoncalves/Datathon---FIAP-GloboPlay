# Usar uma imagem base do Python
FROM python:3.9-slim

# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Copiar os arquivos de dependências
COPY requirements.txt .

# Instalar as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código-fonte para o container
COPY . .

# Expor as portas necessárias
# FastAPI
# Streamlit
# MLflow
EXPOSE 8000  
EXPOSE 8501  
EXPOSE 5000  

# Comando para rodar a aplicação
CMD ["python", "__init__.py"]