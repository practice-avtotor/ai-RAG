# Реализован ввод запроса и нажатие кнопки поиска
# Добавлены базовые селекторы

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


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
        """Выполнение поиска"""
        
        print(f"Поиск по запросу: {query}")
        
        self.driver.get("https://searchplatform.rospatent.gov.ru/patents_advanced")
        time.sleep(2)

        # Находим поле ввода
        search_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "textarea.search_query"))
        )
        search_input.send_keys(query)

        # Нажимаем кнопку поиска
        search_btn = self.driver.find_element(By.CSS_SELECTOR, "button.search_button")
        search_btn.click()
        
        print("Поиск выполнен")
        
        time.sleep(3)

    def run(self):
        self.setup_driver()
        self.perform_search("IC=(F01)")
        
        time.sleep(5)
        
        self.driver.quit()


if __name__ == "__main__":
    parser = PatentParser()
    parser.run()
