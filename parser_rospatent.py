# Добавлен список всех подклассов раздела F
# Реализован цикл по подклассам

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Список подклассов раздела F
MPK_SUBCLASSES = [
    "F01",
    "F02",
    "F03",
    "F04",
    "F15",
    "F16",
    "F17",
    "F21",
    "F22",
    "F23",
    "F24",
    "F25",
    "F26",
    "F27",
    "F28",
    "F41",
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
        print(f"Поиск по запросу: {query}")
        self.driver.get("https://searchplatform.rospatent.gov.ru/patents_advanced")
        time.sleep(2)

        search_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "textarea.search_query"))
        )
        search_input.clear()
        search_input.send_keys(query)

        search_btn = self.driver.find_element(By.CSS_SELECTOR, "button.search_button")
        search_btn.click()
        
        time.sleep(3)
        
        print("Поиск выполнен")

    def collect_patents(self, subclass):
        """Сбор патентов для подкласса"""
        
        query = f"IC=({subclass})"
        self.perform_search(query)
        
        # TODO: Реализовать сбор данных
        
        print(f"Обработан подкласс {subclass}")

    def run(self):
        self.setup_driver()
        
        for subclass in MPK_SUBCLASSES:
            print(f"\nОбработка {subclass}")
        
            self.collect_patents(subclass)
            time.sleep(2)
        
        self.driver.quit()


if __name__ == "__main__":
    parser = PatentParser()
    parser.run()
