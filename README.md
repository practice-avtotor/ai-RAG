# ai-RAG

Репозиторий для **RAG-системы перевода автомобильных терминов** (китайский упрощённый → русский).

---

# О проекте

Данный репозиторий содержит RAG-модуль, предназначенный для поиска автомобильных терминов.

Модуль полностью независим от LLM и может использоваться как отдельная библиотека.

## Основные возможности

- Быстрый семантический поиск (FAISS + SentenceTransformers)
- Поддержка фильтрации по `min_similarity`
- Логирование и обработка ошибок
- Оптимизировано для CPU-инференса
- Простая интеграция с любой LLM

---

# Структура проекта

```text
ai-RAG/
│
├── data/
│   ├── glossary.jsonl          # Основной глоссарий
│   ├── faiss.index             # FAISS индекс
│   ├── metadata.pkl            # Метаданные терминов
│   └── embeddings.npy          # Эмбеддинги (для отладки)
│
├── rag/                        # Основной пакет
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   ├── loader.py
│   ├── embedder.py
│   ├── index_builder.py
│   └── retriever.py
│
├── scripts/
│   ├── build_index.py          # Построение индекса
│   └── test_search.py          # Интерактивное тестирование
│   └── merge_csv_files.py      # Сливает результаты парсинга в один csv файл
│   └── ollama_translation.py   # Переводит каждую строчку csv файла в jsonl
│   └── parser_rospatent.py     # Парсит страницу роспатента по нескольким поисковым запросам
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Быстрый старт

## 1. Клонирование репозитория

```bash
git clone <repository-url>
cd ai-RAG
```

## 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

## 3. Построение индекса

### Windows (PowerShell)

```powershell
$env:PYTHONPATH="."
python -m scripts.build_index --force
```

### Linux / macOS

```bash
PYTHONPATH=. python -m scripts.build_index --force
```

---

# Тестирование поиска

### Windows

```powershell
$env:PYTHONPATH="."
python -m scripts.test_search
```

### Linux / macOS

```bash
PYTHONPATH=. python -m scripts.test_search
```

---

# Использование в коде

```python
from rag import Retriever

retriever = Retriever()

terms = retriever.retrieve(
    "检查DOT4制动液液位",
    top_k=5,
    min_similarity=0.75,
)

for term in terms:
    print(
        f"{term.entry.chinese} → "
        f"{term.entry.russian} "
        f"(score: {term.similarity:.4f})"
    )
```

---

# Формат глоссария

Файл `glossary.jsonl` содержит один JSON-объект в каждой строке.

```json
{
  "chinese": "DOT4制动液",
  "russian": "Тормозная жидкость DOT4",
  "english": "DOT4 Brake Fluid",
  "category": "brakes",
  "context": "Используется в тормозной системе"
}
```

---

# Как работает система

```text
Запрос пользователя
        │
        ▼
SentenceTransformer
        │
        ▼
Вектор запроса
        │
        ▼
FAISS Index
        │
        ▼
Top-K наиболее похожих терминов
        │
        ▼
Фильтрация по min_similarity
        │
        ▼
Готовый список терминов
        │
        ▼
Передача в LLM
```

---

# Используемые технологии

- Python 3.11+
- FAISS
- SentenceTransformers
- NumPy
- Pydantic
- Logging
