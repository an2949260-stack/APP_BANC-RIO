# Dockerfile Frontend (Streamlit)
FROM python:3.11-slim

WORKDIR /app

# Instalação de dependências
COPY frontend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Cópia da aplicação
COPY frontend/ .

# Configuração do Streamlit
RUN mkdir -p ~/.streamlit && \
    echo "[server]" > ~/.streamlit/config.toml && \
    echo "headless = true" >> ~/.streamlit/config.toml && \
    echo "port = 8501" >> ~/.streamlit/config.toml

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
