import json
import pandas as pd
from pathlib import Path
from typing import Set, List, Dict

SCRIPT_DIR = Path(__file__).parent.absolute()

DATA_DIR = SCRIPT_DIR.parent

GLOSSARY_PATH = DATA_DIR / "glossary.json"
INPUT_FILE = DATA_DIR / "Automotive_Glossary_CN-RU.xlsx"
OUTPUT_JSONL = DATA_DIR / "unprocessed_terms.jsonl"


def load_glossary_chinese(glossary_path: str) -> Set[str]:
    """Загружает все китайские термины из glossary"""
    with open(glossary_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    chinese_terms = {item['chinese'].strip() for item in data 
                    if isinstance(item, dict) and 'chinese' in item}
    print(f"Загружено {len(chinese_terms)} терминов из glossary.json")
    return chinese_terms


def load_existing_unprocessed(jsonl_path: str) -> Set[str]:
    """Загружает уже добавленные китайские термины из jsonl"""
    existing = set()
    path = Path(jsonl_path)
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        item = json.loads(line)
                        if 'chinese' in item:
                            existing.add(item['chinese'].strip())
                    except:
                        continue
    return existing


def main():
    glossary = load_glossary_chinese(GLOSSARY_PATH)
    existing_unprocessed = load_existing_unprocessed(OUTPUT_JSONL)
    
    df = pd.read_excel(INPUT_FILE, sheet_name=0, header=None)
    chinese_terms = [str(x).strip() for x in df.iloc[:, 0].dropna() if str(x).strip()]

    new_entries: List[Dict] = []
    skipped = 0

    print(f"Всего терминов в Excel: {len(chinese_terms)}")
    print(f"Уже есть в glossary:     {len(glossary)}")
    print(f"Уже в unprocessed.jsonl: {len(existing_unprocessed)}\n")

    for i, term in enumerate(chinese_terms):
        if not term or term in glossary or term in existing_unprocessed:
            skipped += 1
            continue

        print(f"[{i+1}/{len(chinese_terms)}] Найден новый: {term}")
        
        entry = {
            "chinese": term,
            "russian": "",           
            "english": "",         
            "category": "general",
            "context": f"{term} — это автомобильный термин. Автомобильная деталь или материал, используемый при производстве, сборке или ремонте транспортного средства.",
        }
        
        new_entries.append(entry)

    if new_entries:
        with open(OUTPUT_JSONL, 'a', encoding='utf-8') as f:
            for entry in new_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        pd.DataFrame(new_entries).to_excel(DATA_DIR / "unprocessed_terms_new.xlsx", index=False)
        
        print(f"\nУспешно добавлено {len(new_entries)} новых терминов!")
    else:
        print("\nНовых терминов для добавления не найдено.")

    print(f"   Пропущено (уже существуют): {skipped}")
    print(f"   Файл обновлён: {OUTPUT_JSONL}")


if __name__ == "__main__":
    main()