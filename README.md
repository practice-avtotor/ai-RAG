# ai-RAG

Репозиторий для подготовки данных и создания RAG-системы перевода автотерминов (китайский → русский) в автомобильной области.

---

## Что внутри

### 📂 data_for_RAG/

Готовые данные для RAG-системы:

- `glossary.json` — глоссарий в формате JSON (массив объектов с полями `chinese`, `russian`, `english`, `category`, `context`).
- `glossary.jsonl` — тот же глоссарий в формате JSON Lines.
- `unprocessed_terms.jsonl` — новые термины без перевода, ожидающие ручной обработки.

### 📂 terms_processing_scripts/

Скрипты для обработки терминов:

- `extract_terms.py` — извлекает уникальные термины из Excel/CSV-файлов (автоматически определяет нужный столбец) и сохраняет новые термины в `unprocessed_terms.xlsx`.
- `find_unprocessed_terms.py` — сравнивает `glossary.json` с исходными Excel-файлами и добавляет отсутствующие термины в `unprocessed_terms.jsonl`.

### ⚙️ Конфигурация

- `.gitignore` — исключает из репозитория:
  - директорию `BOMs/`;
  - исходные Excel-файлы (`*.xlsx`);
  - временные файлы и артефакты обработки.

- `requirements.txt` — список зависимостей:
  - `pandas`
  - `openpyxl`
  - `chardet`

---

## Быстрый старт

### Клонирование репозитория

```bash
git clone git@github.com:practice-avtotor/ai-RAG.git
cd ai-RAG
```

### Установка зависимостей

```bash
pip install -r requirements.txt
```

---

## Структура проекта

```text
ai-RAG/
├── data_for_RAG/
│   ├── glossary.json
│   ├── glossary.jsonl
│   └── unprocessed_terms.jsonl
│
├── terms_processing_scripts/
│   ├── extract_terms.py
│   └── find_unprocessed_terms.py
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Формат записи терминов

Пример записи в `glossary.json`:

```json
{
  "chinese": "发动机",
  "russian": "двигатель",
  "english": "engine",
  "category": "powertrain",
  "context": "Основной силовой агрегат автомобиля"
}
```