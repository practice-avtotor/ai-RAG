FROM python:3.12-slim

WORKDIR /app

# Установка системных зависимостей для faiss и sentence-transformers
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    cmake \
    build-essential \
    curl \
    nano \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости и устанавливаем
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

# Создаём папку для данных
RUN mkdir -p data

# Копируем скрипт инициализации
COPY scripts/init.sh /app/scripts/init.sh
RUN chmod +x /app/scripts/init.sh

EXPOSE 8000

# Запускаем скрипт инициализации, затем uvicorn
CMD ["/app/scripts/init.sh"]
