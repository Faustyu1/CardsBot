# Используем официальный образ Python 3.12
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . .

# Создаём виртуальное окружение
RUN python3 -m venv venv

# Активируем виртуальное окружение и запускаем приложение
CMD ["sh", "-c", "source venv/bin/activate && python3 main.py"]
