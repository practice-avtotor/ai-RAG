import pandas as pd
import re
from pathlib import Path
from typing import List, Set
import chardet

class AutomotiveTermExtractor:
    """Экстрактор автомобильных терминов с автоматическим определением столбца"""

    def __init__(self, existing_terms_file: str = "unified_terms.xlsx"):
        self.existing_terms_file = existing_terms_file
        self.existing_terms = self._load_existing_terms()

        # Паттерны для определения автомобильных терминов
        self.automotive_patterns = [
            r'总成', r'螺栓', r'螺母', r'螺钉', r'垫圈', r'卡扣',
            r'支架', r'护板', r'线束', r'传感器', r'控制器', r'模块',
            r'发动机', r'变速箱', r'制动', r'转向', r'悬挂', r'座椅',
            r'保险杠', r'后视镜', r'车门', r'车窗', r'玻璃', r'灯具',
            r'空调', r'仪表', r'安全气囊', r'安全带'
        ]

        # Паттерн для китайских иероглифов
        self.chinese_pattern = re.compile(r'[\u4e00-\u9fff]')

    def _load_terms_from_file(self, file_path: str) -> Set[str]:
        """Загружает термины из файла, предполагая, что они в первом столбце"""
        path = Path(file_path)
        if not path.exists():
            return set()

        try:
            df = pd.read_excel(path)
            if df.empty:
                return set()
            terms = set(df.iloc[:, 0].dropna().astype(str).str.strip())
            return terms
        except Exception as e:
            print(f"Ошибка при загрузке файла {path}: {e}")
            return set()

    def _load_existing_terms(self) -> Set[str]:
        """Загружает существующие термины из файла"""
        terms = self._load_terms_from_file(self.existing_terms_file)
        if terms:
            print(f"Загружено {len(terms)} существующих терминов из {self.existing_terms_file}")
        else:
            print(f"Файл {self.existing_terms_file} не найден или пуст. Создаем новый список терминов.")
        return terms

    def _detect_encoding(self, file_path: str) -> str:
        """Определяет кодировку файла"""
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read(10000))
        return result['encoding'] or 'utf-8'

    def _is_automotive_term(self, text: str) -> bool:
        """Проверяет, является ли текст автомобильным термином"""
        if not text or pd.isna(text):
            return False

        text = str(text).strip()

        # Длина термина (обычно термины короткие)
        if len(text) < 2 or len(text) > 100:
            return False

        # Должен содержать китайские иероглифы
        if not self.chinese_pattern.search(text):
            return False

        # Проверяем наличие автомобильных паттернов
        for pattern in self.automotive_patterns:
            if re.search(pattern, text):
                return True

        # Если нет явных паттернов, проверяем структуру
        # Термины обычно не содержат длинных предложений
        if len(text.split()) > 10:  # Слишком много слов
            return False

        return True

    def _find_terms_column(self, df: pd.DataFrame) -> int:
        """Находит столбец с терминами в DataFrame"""
        column_scores = []

        for col_idx in range(len(df.columns)):
            column = df.iloc[:, col_idx]

            # Пропускаем пустые столбцы
            if column.dropna().empty:
                column_scores.append((col_idx, 0))
                continue

            # Анализируем первые 100 непустых значений
            sample = column.dropna().head(100).astype(str)

            score = 0

            # Проверяем процент автомобильных терминов
            automotive_count = sum(1 for val in sample if self._is_automotive_term(val))
            automotive_ratio = automotive_count / len(sample) if len(sample) > 0 else 0

            score += automotive_ratio * 50  # До 50 баллов за процент терминов

            # Проверяем среднюю длину (термины обычно средней длины)
            avg_length = sample.str.len().mean()
            if 5 <= avg_length <= 50:
                score += 20

            # Проверяем разнообразие (термины не должны повторяться слишком часто)
            unique_ratio = sample.nunique() / len(sample) if len(sample) > 0 else 0
            score += unique_ratio * 30  # До 30 баллов за разнообразие

            column_scores.append((col_idx, score))

        # Возвращаем столбец с максимальным score
        best_column = max(column_scores, key=lambda x: x[1])

        if best_column[1] < 20:  # Минимальный порог
            print(f"Не удалось найти столбец с терминами (максимальный score: {best_column[1]:.2f})")
            return -1

        print(f"Найден столбец с терминами: колонка {best_column[0]} (score: {best_column[1]:.2f})")
        return best_column[0]

    def extract_terms_from_file(self, file_path: str) -> List[str]:
        """Извлекает уникальные термины из файла"""
        file_path = Path(file_path)

        if not file_path.exists():
            print(f"Файл не найден: {file_path}")
            return []

        print(f"\nОбработка файла: {file_path.name}")

        try:
            # Определяем формат файла
            suffix = file_path.suffix.lower()

            if suffix in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            elif suffix == '.csv':
                encoding = self._detect_encoding(str(file_path))
                df = None
                for sep in [',', ';', '\t', '|']:
                    try:
                        candidate = pd.read_csv(file_path, encoding=encoding, sep=sep)
                        if not candidate.empty and len(candidate.columns) >= 1:
                            df = candidate
                            if len(candidate.columns) > 1:
                                break
                    except Exception:
                        continue
                if df is None:
                    print("Не удалось прочитать CSV-файл с известными разделителями")
                    return []
            else:
                print(f"Неподдерживаемый формат: {suffix}")
                return []

            print(f"Размер файла: {len(df)} строк, {len(df.columns)} столбцов")

            # Находим столбец с терминами
            terms_column = self._find_terms_column(df)

            if terms_column == -1:
                print("Не удалось определить столбец с терминами")
                return []

            # Извлекаем термины
            terms = []
            for value in df.iloc[:, terms_column]:
                if self._is_automotive_term(value):
                    term = str(value).strip()
                    if term and term not in self.existing_terms:
                        terms.append(term)

            # Удаляем дубликаты внутри файла
            unique_terms = list(dict.fromkeys(terms))

            print(f"Найдено {len(unique_terms)} новых уникальных терминов")

            return unique_terms

        except Exception as e:
            print(f"Ошибка при обработке файла: {e}")
            return []

    def add_terms_to_file(self, new_terms: List[str], output_file: str = None):
        """Добавляет новые термины в файл"""
        if not new_terms:
            print("\nНет новых терминов для добавления")
            return

        output_file = output_file or self.existing_terms_file

        # Объединяем существующие и новые термины и удаляем дубликаты
        all_terms = list(dict.fromkeys(sorted(set(self.existing_terms).union(new_terms))))

        # Создаем DataFrame
        df = pd.DataFrame({
            'Китайский термин': all_terms,
            'Количество': [len(all_terms)] * len(all_terms)
        })

        # Сохраняем в файл
        df.to_excel(output_file, index=False)

        print(f"\nДобавлено {len(all_terms) - len(self.existing_terms)} новых терминов")
        print(f"Всего терминов в файле: {len(all_terms)}")
        print(f"Файл сохранен: {output_file}")

        # Обновляем список существующих терминов
        self.existing_terms = set(all_terms)

    def write_untranslated_terms(self, translated_terms_file: str = "translated_terms.xlsx", output_file: str = "untranslated_terms.xlsx"):
        """Записывает термины из unified_terms, которых нет в translated_terms"""
        translated_terms = self._load_terms_from_file(translated_terms_file)
        untranslated_terms = sorted(self.existing_terms.difference(translated_terms))

        if not untranslated_terms:
            print(f"Нет непререведенных терминов для записи в {output_file}")
            return

        df = pd.DataFrame({'Китайский термин': untranslated_terms})
        df.to_excel(output_file, index=False)

        print(f"\nЗаписано {len(untranslated_terms)} непререведенных терминов в {output_file}")

    def process_directory(self, directory_path: str, output_file: str = None):
        """Обрабатывает все файлы в директории"""
        directory = Path(directory_path)

        if not directory.exists():
            print(f"Директория не найдена: {directory_path}")
            return

        print(f"\n{'='*60}")
        print(f"ОБРАБОТКА ДИРЕКТОРИИ: {directory}")
        print(f"{'='*60}")

        all_new_terms = []
        supported_extensions = ['.xlsx', '.xls', '.csv']

        for file_path in directory.rglob('*'):
            if file_path.suffix.lower() in supported_extensions:
                new_terms = self.extract_terms_from_file(str(file_path))
                all_new_terms.extend(new_terms)

                # Обновляем список существующих терминов после каждого файла
                self.existing_terms.update(new_terms)

        unique_new_terms = list(dict.fromkeys(all_new_terms))

        # Добавляем все новые термины в файл
        if unique_new_terms:
            self.add_terms_to_file(unique_new_terms, output_file)
        else:
            print("\nНовые термины не найдены")


def main():
    """Основная функция"""
    print("="*60)
    print("ЭКСТРАКТОР АВТОМОБИЛЬНЫХ ТЕРМИНОВ v2.0")
    print("Автоматическое определение столбца с терминами")
    print("="*60)

    # Инициализируем экстрактор
    extractor = AutomotiveTermExtractor("unprocessed_terms.xlsx")

    # Запрашиваем путь
    print("\nВвeдитe путь к файлу или директории:")
    print("(оставьте пустым для текущей директории)")
    input_path = input("> ").strip()

    if not input_path:
        input_path = "."

    input_path = Path(input_path)

    # Обрабатываем
    if input_path.is_file():
        new_terms = extractor.extract_terms_from_file(str(input_path))
        if new_terms:
            extractor.add_terms_to_file(new_terms)
    elif input_path.is_dir():
        extractor.process_directory(str(input_path))
    else:
        print(f"Путь не найден: {input_path}")

    extractor.write_untranslated_terms()

    print("\n" + "="*60)
    print("ГОТОВО!")
    print("="*60)


if __name__ == "__main__":
    main()
