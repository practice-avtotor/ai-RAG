import csv
import logging
import os
import time
import traceback

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Все подклассы раздела патентов про автомобили

MPK_SUBCLASSES = [
    "F01", "F02", "F03", "F04", "F15", "F16", "F17",
    "F21", "F22", "F23", "F24", "F25", "F26", "F27",
    "F28", "F41", "F42"
]


def setup_driver():
    """Запускает Chromium драйвер"""
    logger.info("Запуск Chromium драйвера...")

    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.binary_location = '/usr/bin/chromium-browser'

    service = Service('/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(10)

    logger.info("Драйвер запущен")
    return driver


def go_to_search_page(driver):
    """Принудительно переходит на страницу поиска"""
    logger.info("Переход на страницу поиска...")
    driver.get("https://searchplatform.rospatent.gov.ru/patents_advanced")

    time.sleep(2)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                "textarea.search_query")))

        logger.info("Страница поиска загружена!")
        return True

    except Exception as ex:
        logger.warning(f"Страница поиска загрузилась не полностью!"\
                       f"Подробнее: {ex}")
        return False


def perform_search(driver, query):
    """Выполняет поиск по конкретному запросу"""
    logger.info(f"Выполнение поиска по запросу: {query}")

    try:
        driver.get("https://searchplatform.rospatent.gov.ru/patents_advanced")
        time.sleep(2)

        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                "textarea.search_query")))

        search_input.clear()
        search_input.send_keys(query)
        logger.info(f"Запрос '{query}' введён")

        search_btn = None

        try:
            search_btn = driver.find_element(By.CSS_SELECTOR, "button.search_button.active.mbl_hdn")
        except Exception as ex:
            logger.info(f"Cant find search button by its class."\
                        f"More: {ex}")
            pass

        if not search_btn:
            try:
                search_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Поиск')]")
            except Exception as ex:
                logger.info(f"Cant find search button by its text \"Поиск\"."\
                            f"More: {ex}")
                pass

        # Вариант 3: по любому button с классом search_button
        if not search_btn:
            try:
                search_btn = driver.find_element(By.CSS_SELECTOR, "button.search_button")
            except Exception as ex:
                logger.info(f"Cant find any button with class \"search_button\"."\
                            f"More: {ex}")
                pass

        if not search_btn:
            logger.error("Кнопка поиска не найдена!")
            return False

        driver.execute_script("arguments[0].click();", search_btn)
        logger.info("Кнопка поиска нажата")

        time.sleep(5)

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    "ul.report_items > li")))

            items = driver.find_elements(By.CSS_SELECTOR,
                                         "ul.report_items > li")

            logger.info(f"Результаты загружены, на странице {len(items)} патентов")
            return True

        except TimeoutException:
            try:
                no_results = driver.find_element(By.XPATH, "//div[contains(text(), 'ничего не найдено') or contains(text(), 'No results')]") # noqa: F841
                logger.warning(f"Для запроса {query} ничего не найдено")
                return False

            except Exception as ex:
                logger.warning(f"Неизвестная ошибка для запроса {query}"\
                               f"More: {ex}")
                return False

    except Exception as ex:
        logger.error(f"Ошибка поиска для {query}: {ex}")
        return False


def wait_for_manual_limit(driver, wait_seconds=3):
    """
    Даёт время на ручную установку лимита (только для первого запроса)
    Дальше все сохраняется в куках и не требут переустановки
    """

    logger.info(f"Ожидание {wait_seconds} секунд для ручной установки лимита 100...")
    logger.info("Сейчас вы можете вручную выбрать 'Показать сразу: 100'")

    for i in range(wait_seconds, 0, -1):
        logger.info(f"Осталось {i} секунд...")
        time.sleep(1)

    logger.info("✅ Продолжаем парсинг...")

    try:
        items = driver.find_elements(By.CSS_SELECTOR, "ul.report_items > li")
        logger.info(f"На странице {len(items)} патентов")

    except Exception as ex:
        logger.info(f"Unbounded error: {ex}")
        pass

    return True

def parse_titles_only(driver, subclass):
    """Парсит только названия патентов с текущей страницы"""
    titles = []

    try:
        items = driver.find_elements(By.CSS_SELECTOR, "ul.report_items > li")
        logger.info(f"Найдено {len(items)} патентов на странице")

        for item in items:
            try:
                title_elem = item.find_element(By.CSS_SELECTOR, "div.report_caption")
                title = title_elem.text.strip()

                if title and title[0].isdigit() and ". " in title:
                    title = title.split(". ", 1)[1]

                if title:
                    titles.append(title)

            except Exception as e:
                logger.debug(f"Ошибка парсинга: {e}")
                continue

    except Exception as e:
        logger.error(f"Ошибка парсинга страницы: {e}")

    logger.info(f"Собрано {len(titles)} названий для {subclass}")
    return titles


def go_to_next_page(driver):
    """Универсальный переход на следующую страницу"""
    try:
        time.sleep(2)

        pagination_links = driver.find_elements(By.CSS_SELECTOR, "ul.pagination li a")

        if not pagination_links:
            logger.debug("Пагинация не найдена")
            return False

        next_btn = None

        for link in pagination_links:
            text = link.text.strip()

            if text in [">", "»", "›", "next", "след", "далее"]:
                class_name = link.get_attribute("class") or ""

                if "disabled" not in class_name:
                    next_btn = link
                    break

        if not next_btn:
            logger.info("Кнопка 'Далее' не найдена или неактивна")
            return False

        driver.execute_script("arguments[0].click();", next_btn)
        time.sleep(3)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                "ul.report_items > li")))

        return True

    except Exception as e:
        logger.debug(f"Ошибка перехода: {e}")
        return False


def save_titles_to_csv(titles, subclass, output_dir="patents_data"):
    """Сохраняет названия для конкретного подкласса в CSV"""

    if not titles:
        logger.warning(f"Нет данных для сохранения {subclass}")
        return

    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"patents_{subclass}.csv")

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["title"])

        for title in titles:
            writer.writerow([title])

    logger.info(f"Сохранено {len(titles)} названий в {filename}")

def collect_patents_for_subclass(driver, subclass, is_first=False, max_pages=10):
    """
    Собирает патенты для одного подкласса
    """

    query = f"IC=({subclass})"
    all_titles = []
    page_num = 1

    logger.info(f"Обработка подкласса {subclass}")

    if not perform_search(driver, query):
        logger.warning(f"Для {subclass} ничего не найдено или ошибка")
        return []

    if is_first:
        wait_for_manual_limit(driver, wait_seconds=5)

    while page_num <= max_pages:
        logger.info(f"  Страница {page_num} из {max_pages}")

        titles = parse_titles_only(driver, subclass)
        if not titles:
            break

        all_titles.extend(titles)
        logger.info(f"Всего для {subclass}: {len(all_titles)}")

        if len(titles) < 10:
            logger.info("На странице меньше 10 патентов - последняя")
            break

        if not go_to_next_page(driver):
            logger.info("  Достигнут конец списка")
            break

        page_num += 1

    if all_titles:
        save_titles_to_csv(all_titles, subclass)
        logger.info(f"Для {subclass} собрано {len(all_titles)} названий")

    else:
        logger.warning(f"Для {subclass} не собрано ни одного названия")

    return all_titles

def main():
    logger.info("Запуск парсера Роспатента для всех подклассов F*")

    driver = None
    all_results = {}

    try:
        driver = setup_driver()

        for i, subclass in enumerate(MPK_SUBCLASSES, 1):
            logger.info(f"#{i} из {len(MPK_SUBCLASSES)}: {subclass}")

            is_first = (i == 1)

            titles = collect_patents_for_subclass(
                driver,
                subclass,
                is_first=is_first,
                max_pages=10
            )

            all_results[subclass] = titles

            time.sleep(2)

        # ======================================================================

        logger.info("\n" + "="*60)
        logger.info("ИТОГОВЫЙ ОТЧЁТ\n")

        total = 0

        for subclass, titles in all_results.items():
            count = len(titles) if titles else 0
            logger.info(f"{subclass}: {count} названий")
            total += count

        logger.info(f"Всего собрано: {total} названий")
        logger.info("Данные сохранены в папке 'patents_data/'")

    except KeyboardInterrupt:
        logger.info("Прервано пользователем!")
        logger.info("Сохранены данные для обработанных подклассов")

    except Exception as ex:
        logger.error(f"Критическая ошибка: {ex}")
        traceback.print_exc()

    finally:
        if driver:
            driver.quit()
            logger.info("Драйвер закрыт")

    logger.info("Парсер завершил работу")

if __name__ == "__main__":
    main()
