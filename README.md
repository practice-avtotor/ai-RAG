# 🔥 ai-RAG — RAG-переводчик патентов

RAG-система для перевода патентных заголовков с английского на русский и китайский.  
Использует **семантический поиск (FAISS)** по глоссарию из 3674 терминов и **LLM (Ollama + Qwen2.5)** для точного перевода.

---

## 🧠 Что внутри

| Компонент | Технологии |
|-----------|------------|
| **RAG** | FAISS + SentenceTransformers (paraphrase-multilingual-MiniLM-L12-v2) |
| **LLM** | Ollama + Qwen2.5:7b (локально, бесплатно) |
| **API** | FastAPI + Uvicorn |
| **Кэш** | LRU-кэш (1000 записей) |
| **Контейнеризация** | Docker + Docker Compose |
| **Глоссарий** | 3674 термина (китайский → русский/английский) |

---

## 📁 Структура проекта

```
ai-RAG/
├── .env                     # Настройки (создаётся локально)
├── .env.example             # Пример настроек
├── docker-compose.yml       # Docker Compose
├── Dockerfile               # Docker образ
├── requirements.txt         # Зависимости
├── prompts.yaml             # SYSTEM_PROMPT для LLM
├── README.md                # Документация
│
├── config.py                # Конфигурация (читает .env)
├── main.py                  # FastAPI сервер
├── translator.py            # Основная логика перевода
├── prompt_builder.py        # Построение промптов
├── cache_manager.py         # LRU-кэш
├── models.py                # Pydantic модели для API
│
├── rag/                     # RAG-модуль
│   ├── config.py
│   ├── models.py
│   ├── loader.py
│   ├── embedder.py
│   ├── index_builder.py
│   └── retriever.py
│
├── scripts/                 # Утилиты
│   ├── build_index.py       # Построение индекса FAISS
│   ├── test_search.py       # Тестирование поиска
│   └── init.sh              # Скрипт инициализации (модель + индекс)
│
└── data/
    └── merged_glossary.jsonl # Глоссарий
```


## 🚀 Быстрый старт (с нуля)

### 1. Клонируй репозиторий

```bash
git clone <url-репозитория>
cd ai-RAG
```

### 2. Создай `.env` из примера

```bash
cp .env.example .env
```

Отредактируй `.env` при необходимости (обычно всё работает по умолчанию).

### 3. Запусти через Docker Compose

```bash
docker compose up -d
```

При первом запуске автоматически:
- 🐳 Поднимется контейнер с Ollama
- 📥 Скачается модель `qwen2.5:7b` (4.7 ГБ, 5-10 минут)
- 📊 Построится FAISS-индекс из глоссария
- 🚀 Запустится FastAPI сервер

### 4. Проверь, что всё работает

```bash
# Health check
curl http://localhost:8000/health

# Тестовый перевод
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "HEAT EXCHANGER"}'

# Swagger UI
# Открой в браузере: http://localhost:8000/docs
```


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
  "context": "Устройство для герметизации соединений",
  "from_cache": false,
  "rag_used": true,
  "rag_examples": [...]
}
```


## 🧪 Тестирование

### Построение индекса вручную

```bash
docker exec -it patent-translator bash -c "PYTHONPATH=/app python scripts/build_index.py --force"
```

### Интерактивный тест поиска

```bash
docker exec -it patent-translator bash -c "PYTHONPATH=/app python scripts/test_search.py"
```


## 🐳 Docker

### Сборка и запуск

```bash
docker compose build
docker compose up -d
```

### Просмотр логов

```bash
# Логи всех контейнеров
docker compose logs -f

# Только переводчика
docker compose logs -f translator

# Только Ollama
docker compose logs -f ollama
```

### Остановка и очистка

```bash
# Остановка
docker compose down

# Остановка + удаление томов (включая скачанные модели)
docker compose down -v
```


## 🛠️ Используемые технологии

| Компонент | Технология | Версия |
|-----------|------------|--------|
| **Фреймворк** | FastAPI | 0.139.0 |
| **Сервер** | Uvicorn | 0.49.0 |
| **RAG** | FAISS | 1.8.0+ |
| **Эмбеддинги** | SentenceTransformers | 3.0.0+ |
| **LLM** | Ollama + Qwen2.5:7b | — |
| **Векторизация** | NumPy | 2.5.0 |
| **Контейнеризация** | Docker + Docker Compose | — |

