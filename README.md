# ai-RAG — RAG-переводчик патентов

Репозиторий содержит **RAG-систему перевода автомобильных/патентных терминов** (китайский упрощённый → русский/английский) с возможностью интеграции с LLM через FastAPI и Docker.

---

## 🧠 Что внутри

- **RAG-модуль** — семантический поиск по глоссарию (FAISS + SentenceTransformers)
- **FastAPI сервер** — REST API для перевода патентов
- **Ollama** — локальный запуск LLM (qwen2.5:7b)
- **Docker** — полная контейнеризация
- **Кэширование** — LRU-кэш для быстрых повторных запросов
- **Гибкая конфигурация** — через `.env` файл (* В разработке)

---

## 📁 Структура проекта

```
ai-RAG/
│
├── data/                          # Данные
│   ├── merged_glossary.jsonl      # Основной глоссарий (3674 термина)
│   ├── glossary.jsonl             # Второй глоссарий
│
├── rag/                           # RAG-модуль
│   ├── __init__.py
│   ├── config.py                  # Конфиг RAG
│   ├── models.py                  # Модели данных
│   ├── loader.py                  # Загрузка глоссария
│   ├── embedder.py                # Эмбеддинги
│   ├── index_builder.py           # Построение индекса FAISS
│   └── retriever.py               # Поиск по индексу
│
├── scripts/                       # Утилиты
│   ├── build_index.py             # Построение индекса
│   ├── test_search.py             # Тестирование поиска
│   ├── merge_csv_files.py         # Слияние CSV
│   ├── ollama_translation.py      # Генерация глоссария через Ollama
│   └── parser_rospatent.py        # Парсинг патентов
│
├── data/terms_processing_scripts/ # Скрипты обработки терминов
│   ├── extract_terms.py
│   ├── find_unprocessed_terms.py
│   └── merge_glossary_json.py
│
├── main.py                        # FastAPI сервер (точка входа)
├── translator.py                  # Основная логика перевода
├── prompt_builder.py              # Построение промптов
├── cache_manager.py               # LRU-кэш
├── config.py                      # Глобальная конфигурация
├── models.py                      # Pydantic-модели для API
├── docker-compose.yml             # Docker Compose
├── Dockerfile                     # Docker образ
├── requirements.txt               # Зависимости
├── .env.example                   # Пример переменных окружения * (В разработке)
├── .gitignore
└── README.md
```

---

## 🚀 Быстрый старт

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd ai-RAG
```

---

### 2. Настройка переменных окружения

Создай `.env` файл из примера:

```bash
cp .env.example .env
```

Отредактируй `.env` под свои нужды:

```bash
# Ollama
OLLAMA_BASE_URL=http://ollama:11434/v1
LLM_MODEL=qwen2.5:7b

# API
API_HOST=0.0.0.0
API_PORT=8000

# RAG
RAG_TOP_K=5
RAG_MIN_SIMILARITY=0.75

# Кэш
CACHE_SIZE=1000

# Пути
GLOSSARY_PATH=data/merged_glossary.jsonl
```

---

### 3. Запуск через Docker Compose

```bash
# Сборка и запуск
docker compose up -d

# Проверка статуса
docker compose ps

# Логи
docker compose logs -f translator
```

---

### 4. Проверка работы

```bash
# Health check
curl http://localhost:8000/health

# Перевод одного патента
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "HEAT EXCHANGER"}'

# Пакетный перевод
curl -X POST "http://localhost:8000/translate_batch?top_k=3" \
  -H "Content-Type: application/json" \
  -d '["HEAT EXCHANGER", "COOLING SYSTEM", "PUMP"]'

# Swagger UI
open http://localhost:8000/docs
```

---

### 5. Локальный запуск (без Docker)

```bash
# Установка зависимостей
pip install -r requirements.txt

# Построение индекса FAISS
PYTHONPATH=. python scripts/build_index.py

# Запуск сервера
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 📡 API Endpoints

| Метод | URL | Описание |
|-------|-----|----------|
| `GET` | `/` | Информация о сервисе |
| `GET` | `/health` | Проверка здоровья |
| `GET` | `/stats` | Статистика кэша и RAG |
| `POST` | `/translate` | Перевод одного патента |
| `POST` | `/translate_batch` | Перевод нескольких патентов |
| `POST` | `/cache/clear` | Очистка кэша |
| `GET` | `/docs` | Swagger документация |
| `GET` | `/redoc` | ReDoc документация |

---

### Пример запроса на перевод

```json
{
  "text": "SEAL FOR AN EXCHANGER OF HEAT",
  "top_k": 5,
  "use_rag": true
}
```

### Пример ответа

```json
{
  "original": "SEAL FOR AN EXCHANGER OF HEAT",
  "russian": "Уплотнение теплообменника",
  "chinese": "热交换器密封装置",
  "english": "Seal for a Heat Exchanger",
  "category": "heat exchangers",
  "context": "Устройство для герметизации соединений в теплообменном аппарате.",
  "from_cache": false,
  "rag_used": true,
  "rag_examples": [...]
}
```

---

## 🧠 Как работает система

```
1. Запрос пользователя (патентный заголовок)
        │
        ▼
2. Проверка кэша (LRU)
        │
        ▼
3. Поиск в RAG (FAISS)
   - Эмбеддинг запроса через SentenceTransformer
   - Поиск в FAISS индексе
   - Фильтрация по min_similarity
   - Возврат топ-K примеров
        │
        ▼
4. Формирование промпта с примерами
        │
        ▼
5. Запрос к LLM (Ollama)
        │
        ▼
6. Парсинг JSON-ответа
        │
        ▼
7. Сохранение в кэш
        │
        ▼
8. Возврат перевода
```

---

## 🛠️ Используемые технологии

### Backend
- **FastAPI** — веб-фреймворк
- **Uvicorn** — ASGI сервер
- **Pydantic** — валидация данных

### RAG
- **FAISS** — векторный поиск
- **SentenceTransformers** — эмбеддинги
- **NumPy** — работа с векторами

### LLM
- **Ollama** — локальный запуск LLM
- **Qwen2.5:7b** — модель перевода
- **OpenAI SDK** — клиент для Ollama

### Контейнеризация
- **Docker** — контейнеризация
- **Docker Compose** — оркестрация

---

## 🔧 Переменные окружения (`.env`)

| Переменная | Описание | Значение по умолчанию |
|------------|----------|-----------------------|
| `OLLAMA_BASE_URL` | URL для подключения к Ollama | `http://ollama:11434/v1` |
| `LLM_MODEL` | Название модели для перевода | `qwen2.5:7b` |
| `API_HOST` | Хост для FastAPI | `0.0.0.0` |
| `API_PORT` | Порт для FastAPI | `8000` |
| `RAG_TOP_K` | Количество примеров из RAG | `5` |
| `RAG_MIN_SIMILARITY` | Минимальное сходство для RAG | `0.75` |
| `CACHE_SIZE` | Размер LRU-кэша | `1000` |
| `LOG_LEVEL` | Уровень логирования | `INFO` |
| `GLOSSARY_PATH` | Путь к глоссарию | `data/merged_glossary.jsonl` |

---

## 📦 Формат глоссария

Файл `merged_glossary.jsonl` содержит один JSON-объект в каждой строке:

```json
{
  "chinese": "DOT4制动液",
  "russian": "Тормозная жидкость DOT4",
  "english": "DOT4 Brake Fluid",
  "category": "brakes",
  "context": "Используется в тормозной системе автомобиля"
}
```

---

## 🧪 Тестирование

### Интерактивное тестирование RAG

```bash
# Запуск интерактивного теста
PYTHONPATH=. python scripts/test_search.py
```

### Тестирование через Swagger UI

```bash
# Открыть в браузере
http://localhost:8000/docs
```

### Тестирование через curl

```bash
# Перевод с RAG
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "THERMAL ENERGY STORAGE SYSTEM"}'

# Перевод без RAG
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "THERMAL ENERGY STORAGE SYSTEM", "use_rag": false}'
```


### 📁 `.env.example` — создай этот файл

```bash
# Ollama
OLLAMA_BASE_URL=http://ollama:11434/v1
LLM_MODEL=qwen2.5:7b

# API
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# RAG
RAG_TOP_K=5
RAG_MIN_SIMILARITY=0.75

# Кэш
CACHE_SIZE=1000

# Пути
GLOSSARY_PATH=data/merged_glossary.jsonl
```

---

## 🚀 Деплой на сервер

```bash
# 1. Копируем проект на сервер
scp -r ./patent-translator user@server:/opt/

# 2. Заходим на сервер
ssh user@server

# 3. Переходим в папку
cd /opt/patent-translator

# 4. Запускаем
docker compose up -d

# 5. Проверяем
curl http://localhost:8000/health
```
