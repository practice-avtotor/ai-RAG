import json
from pathlib import Path
from typing import List, Dict, Set


def load_jsonl(file_path: Path) -> List[Dict]:
    """Загружает JSONL файл."""
    entries = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                entries.append(data)
            except json.JSONDecodeError as e:
                print(f"Ошибка в строке {i} файла {file_path}: {e}")
    return entries


def load_json(file_path: Path) -> List[Dict]:
    """Загружает обычный JSON массив."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        if isinstance(data, list):
            return data
        else:
            print(f"Ошибка: {file_path} должен содержать массив объектов.")
            return []


def save_jsonl(entries: List[Dict], file_path: Path):
    """Сохраняет в JSONL формат."""
    with open(file_path, 'w', encoding='utf-8') as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')


def save_json(entries: List[Dict], file_path: Path):
    """Сохраняет в JSON формат (красивый)."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


def main():
    SCRIPT_DIR = Path(__file__).parent.absolute()
    DATA_DIR = SCRIPT_DIR.parent

    input_files = [
        Path(DATA_DIR / "glossary_rospatent(qwen2.5-7b).json"),
        Path(DATA_DIR / "glossary.jsonl"),
    ]

    output_json = Path(DATA_DIR / "merged_glossary.json")
    output_jsonl = Path(DATA_DIR / "merged_glossary.jsonl")

    all_entries: List[Dict] = []
    seen_chinese: Set[str] = set()
    duplicates = 0

    print("Начинаем объединение файлов...\n")

    for file_path in input_files:
        if not file_path.exists():
            print(f"Файл не найден: {file_path}")
            continue

        print(f"Обрабатывается: {file_path.name}")

        if file_path.suffix.lower() == '.jsonl':
            entries = load_jsonl(file_path)
        elif file_path.suffix.lower() == '.json':
            entries = load_json(file_path)
        else:
            print(f"Неподдерживаемый формат: {file_path}")
            continue

        for entry in entries:
            chinese = entry.get("chinese", "").strip()
            if not chinese:
                continue

            if chinese in seen_chinese:
                duplicates += 1
                print(f"Дубликат найден: {chinese}")
                continue

            seen_chinese.add(chinese)
            all_entries.append(entry)

    all_entries.sort(key=lambda x: x.get("chinese", ""))

    print(f"\nГотово!")
    print(f"Всего уникальных записей: {len(all_entries)}")
    print(f"Найдено дубликатов: {duplicates}")

    save_json(all_entries, output_json)
    save_jsonl(all_entries, output_jsonl)

    print(f"\nФайлы сохранены:")
    print(f"   - {output_json}")
    print(f"   - {output_jsonl}")


if __name__ == "__main__":
    main()