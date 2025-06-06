# Используем официальный образ Python 3.13
FROM python:3.13-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Обновляем системные требования
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей в контейнер
# Устанавливаем все зависимости из requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . .

# Make init_db.sh executable
# Create a non-root user
RUN chmod +x init_db.sh
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Add app directory to Python path
ENV PYTHONPATH=/app

# Запускаем бота
CMD ["python3", "main.py"]
