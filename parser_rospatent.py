# Реализован переход по страницам пагинации
# Добавлен сбор всех страниц

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

MPK_SUBCLASSES = [
    "F01", "F02", "F03", "F04",
    "F15", "F16", "F17", "F21",
    "F22", "F23", "F24", "F25",
    "F26", "F27", "F28", "F41",
    "F42",
]


class PatentParser:
    def __init__(self):
        print("Инициализация парсера")
        self.driver = None

    def setup_driver(self):
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)

        print("Драйвер запущен")

    def perform_search(self, query):
        print(f"Поиск: {query}")
        self.driver.get("https://searchplatform.rospatent.gov.ru/patents_advanced")
        time.sleep(2)

        search_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "textarea.search_query"))
        )
        search_input.clear()
        search_input.send_keys(query)

        search_btn = self.driver.find_element(By.CSS_SELECTOR, "button.search_button")
        search_btn.click()
        time.sleep(5)

    def parse_titles(self):
        titles = []
        items = self.driver.find_elements(By.CSS_SELECTOR, "ul.report_items > li")
        print(f"Найдено {len(items)} патентов")

        for item in items:
            try:
                title_elem = item.find_element(By.CSS_SELECTOR, "div.report_caption")
                title = title_elem.text.strip()
                if title:
                    if title[0].isdigit() and ". " in title:
                        title = title.split(". ", 1)[1]
                    titles.append(title)
            except Exception as e:
                print(f"Exception: {e}")
                continue

        return titles

    def go_to_next_page(self):
        """Переход на следующую страницу"""
        try:
            pagination = self.driver.find_elements(
                By.CSS_SELECTOR, "ul.pagination li a"
            )
            for link in pagination:
                if link.text.strip() in [">", "»"]:
                    link.click()
                    time.sleep(3)
                    return True
            return False
        except Exception as e:
            print(f"Exception: {e}")
            return False

    def collect_patents(self, subclass):
        query = f"IC=({subclass})"
        self.perform_search(query)
        all_titles = []
        page = 1

        while page <= 10:  # максимум 10 страниц
            print(f"Страница {page}")
            titles = self.parse_titles()
            if not titles:
                break
            all_titles.extend(titles)

            if not self.go_to_next_page():
                break
            page += 1

        print(f"Всего собрано {len(all_titles)} названий")
        return all_titles

    def run(self):
        self.setup_driver()
        
        for subclass in MPK_SUBCLASSES:
            print(f"\nОбработка {subclass}")
            titles = self.collect_patents(subclass)
            print(f"Результат: {len(titles)} патентов")
            time.sleep(2)
        
        self.driver.quit()


if __name__ == "__main__":
    parser = PatentParser()
    parser.run()
