# ai-RAG

–епозиторий дл€ подготовки данных и создани€ RAG-системы перевода автотерминов (китайский ? русский) в автомобильной области.

---

## „то внутри

### ?? data_for_RAG/

√отовые данные дл€ RAG-системы:

- `glossary.json` Ч глоссарий в формате JSON (массив объектов с пол€ми `chinese`, `russian`, `english`, `category`, `context`).
- `glossary.jsonl` Ч тот же глоссарий в формате JSON Lines.
- `unprocessed_terms.jsonl` Ч новые термины без перевода, ожидающие ручной обработки.

### ?? terms_processing_scripts/

—крипты дл€ обработки терминов:

- `extract_terms.py` Ч извлекает уникальные термины из Excel/CSV-файлов (автоматически определ€ет нужный столбец) и сохран€ет новые термины в `unprocessed_terms.xlsx`.
- `find_unprocessed_terms.py` Ч сравнивает `glossary.json` с исходными Excel-файлами и добавл€ет отсутствующие термины в `unprocessed_terms.jsonl`.

### ??  онфигураци€

- `.gitignore` Ч исключает из репозитори€:
  - директорию `BOMs/`;
  - исходные Excel-файлы (`*.xlsx`);
  - временные файлы и артефакты обработки.

- `requirements.txt` Ч список зависимостей:
  - `pandas`
  - `openpyxl`
  - `chardet`

---

## Ѕыстрый старт

###  лонирование репозитори€

```bash
git clone git@github.com:practice-avtotor/ai-RAG.git
cd ai-RAG
```

### ”становка зависимостей

```bash
pip install -r requirements.txt
```

---

## —труктура проекта

```text
ai-RAG/
??? data_for_RAG/
?   ??? glossary.json
?   ??? glossary.jsonl
?   ??? unprocessed_terms.jsonl
?
??? terms_processing_scripts/
?   ??? extract_terms.py
?   ??? find_unprocessed_terms.py
?
??? .gitignore
??? requirements.txt
??? README.md
```

---

## ‘ормат записи терминов

ѕример записи в `glossary.json`:

```json
{
  "chinese": "???",
  "russian": "двигатель",
  "english": "engine",
  "category": "powertrain",
  "context": "ќсновной силовой агрегат автомобил€"
}
```