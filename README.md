```markdown
# ai-RAG

–епозиторий дл€ подготовки данных и создани€ RAG-системы перевода автотерминов (китайский ? русский) в автомобильной области.

---

## „то внутри

- **data_for_RAG/** Ц готовые данные:
  - `glossary.json` Ц глоссарий (массив объектов с пол€ми: chinese, russian, english, category, context).
  - `glossary.jsonl` Ц тот же глоссарий в формате JSON Lines.
  - `unprocessed_terms.jsonl` Ц новые термины без перевода (ждут ручного заполнени€).

- **terms_processing_scripts/** Ц скрипты:
  - `extract_terms.py` Ц извлекает уникальные термины из Excel/CSV (автоопределение столбца), сохран€ет новые в `unprocessed_terms.xlsx`.
  - `find_unprocessed_terms.py` Ц сравнивает `glossary.json` с исходным Excel, добавл€ет недостающие термины в `unprocessed_terms.jsonl`.

- **.gitignore** Ц исключены: `BOMs/`, `*.xlsx` (исходные файлы), временные файлы.

- **requirements.txt** Ц зависимости: `pandas`, `openpyxl`, `chardet`.

---

## Ѕыстрый старт

```bash
git clone git@github.com:practice-avtotor/ai-RAG.git
cd ai-RAG
pip install -r requirements.txt
```

### »звлечь новые термины
ѕоместите Excel/CSV с терминами в корневую папку, запустите:
```bash
python terms_processing_scripts/extract_terms.py
```