# patents_parser_v2.py
# Добавлена инициализация Selenium WebDriver

# TODO: Настроить пути к браузеру

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

class PatentParser:
    def __init__(self):
        print("Инициализация парсера")
        self.driver = None
    
    def setup_driver(self):
        """Инициализация Chrome драйвера"""

        options = Options()
        options.add_argument('--no-sandbox')
        self.driver = webdriver.Chrome(options=options)

        print("Драйвер запущен")
    
    def run(self):
        self.setup_driver()
        print("Запуск парсера")

        # TODO: Реализовать парсинг

        time.sleep(2)
        self.driver.quit()

if __name__ == "__main__":
    parser = PatentParser()
    parser.run()
