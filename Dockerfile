# Use a imagem oficial do Python como base
FROM python:3.12.8

# Instale dependências de sistema
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Defina o diretório de trabalho dentro do container
WORKDIR /app

# Copie o arquivo de dependências para o container
COPY requirements.txt . 

# Instale as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copie o código fonte do projeto para o diretório de trabalho no container
COPY . . 

# Crie a pasta db, se necessário
RUN mkdir -p /db && touch /db/database.db

# Expõe a porta 8000 para o FastAPI
EXPOSE 8000

# Comando para rodar o servidor FastAPI usando Uvicorn
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]