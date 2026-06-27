# patents_parser_v10.py
# Улучшена логика пагинации
# Добавлена проверка наличия кнопки "Далее"

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import csv
import os
import time
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

MPK_SUBCLASSES = [
    "F01", "F02", "F03", "F04", "F15", "F16", "F17", 
    "F21", "F22", "F23", "F24", "F25", "F26", "F27", 
    "F28", "F41", "F42"
]

class PatentParser:
    def __init__(self):
        self.driver = None
        self.output_dir = "patents_data"
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info("Парсер инициализирован")
    
    def setup_driver(self):
        logger.info("Запуск Chromium драйвера...")
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_page_load_timeout(30)
        self.driver.implicitly_wait(10)
        logger.info("Драйвер запущен")
    
    def perform_search(self, query):
        logger.info(f"Поиск по запросу: {query}")
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
        logger.info("Поиск выполнен")
    
    def parse_titles(self):
        titles = []
        items = self.driver.find_elements(By.CSS_SELECTOR, "ul.report_items > li")
        logger.info(f"Найдено {len(items)} патентов")
        
        for item in items:
            try:
                title_elem = item.find_element(By.CSS_SELECTOR, "div.report_caption")
                title = title_elem.text.strip()
                if title:
                    if title[0].isdigit() and ". " in title:
                        title = title.split(". ", 1)[1]
                    titles.append(title)
            except Exception as ex:
                logger.debug(f"Ошибка парсинга названия: {ex}")
                continue
        return titles
    
    def go_to_next_page(self):
        """Переход на следующую страницу с проверкой"""
        try:
            pagination_links = self.driver.find_elements(By.CSS_SELECTOR, "ul.pagination li a")
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
            
            self.driver.execute_script("arguments[0].click();", next_btn)
            time.sleep(3)
            logger.info("Переход на следующую страницу")
            return True
        except Exception as e:
            logger.debug(f"Ошибка перехода: {e}")
            return False
    
    def save_to_csv(self, titles, subclass):
        filename = os.path.join(self.output_dir, f"patents_{subclass}.csv")
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["title"])
            for title in titles:
                writer.writerow([title])
        logger.info(f"Сохранено {len(titles)} записей в {filename}")
    
    def collect_patents(self, subclass):
        query = f"IC=({subclass})"
        self.perform_search(query)
        all_titles = []
        page = 1
        
        while page <= 10:
            logger.info(f"Страница {page}")
            titles = self.parse_titles()
            if not titles:
                break
            
            if len(titles) < 10:
                logger.info("На странице меньше 10 патентов - последняя")
                all_titles.extend(titles)
                break
            
            all_titles.extend(titles)
            
            if not self.go_to_next_page():
                break
            page += 1
        
        self.save_to_csv(all_titles, subclass)
        return all_titles
    
    def run(self):
        self.setup_driver()
        try:
            for subclass in MPK_SUBCLASSES:
                logger.info(f"\nОбработка подкласса {subclass}")
                titles = self.collect_patents(subclass)
                logger.info(f"Результат: {len(titles)} патентов")
                time.sleep(2)
        except Exception as e:
            logger.error(f"Критическая ошибка: {e}")
        finally:
            self.driver.quit()
            logger.info("Драйвер закрыт")

if __name__ == "__main__":
    parser = PatentParser()
    parser.run()
