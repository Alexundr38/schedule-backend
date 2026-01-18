FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей для psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование всего проекта
COPY . .

# Создание директории для alembic версий
RUN mkdir -p alembic/versions

WORKDIR /app/backend

# Открытие порта
EXPOSE 8000

# Команда запуска (миграции будут в docker-compose)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]