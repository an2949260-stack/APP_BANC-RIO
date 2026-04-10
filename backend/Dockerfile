# Stage 1: Base
FROM python:3.11-slim as base

WORKDIR /app

# Instalação de dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Cópia de requirements
COPY backend/requirements.txt .

# Instalação de dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production
FROM base as production

# Cópia da aplicação
COPY backend/app app/
COPY backend/main.py main.py

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


# Stage 3: Development
FROM base as development

# Instalação de ferramentas de desenvolvimento
RUN pip install --no-cache-dir \
    pytest==7.4.3 \
    pytest-asyncio==0.21.1 \
    pytest-cov==4.1.0 \
    black==23.11.0 \
    flake8==6.1.0

# Cópia completa do backend
COPY backend/ .

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
