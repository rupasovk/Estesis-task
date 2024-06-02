# Образ Python
FROM python:3.10-slim

# Проверяем версию Python
RUN python --version

# Устанавливаем рабочую директорию
RUN mkdir /estesis_app
WORKDIR /estesis_app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN python -m pip install --progress-bar off --upgrade pip
RUN python -m pip install --progress-bar off -r requirements.txt

# Копируем все файлы проекта
COPY . .

# Применям миграции
RUN alembic upgrade head

# Запускаем FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]