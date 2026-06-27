# Добавлена возможность ручной установки лимита на первой странице
# Улучшен механизм ожидания

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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
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
    
    def wait_for_manual_limit(self, wait_seconds=5):
        """Ожидание для ручной установки лимита"""
        logger.info(f"Ожидание {wait_seconds} секунд для ручной установки лимита...")
        logger.info("Вы можете вручную выбрать 'Показать сразу: 100'")
        time.sleep(wait_seconds)
        logger.info("Продолжаем парсинг...")
    
    def perform_search(self, query, is_first=False):
        logger.info(f"Поиск по запросу: {query}")
        self.driver.get("https://searchplatform.rospatent.gov.ru/patents_advanced")
        time.sleep(2)
        
        search_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "textarea.search_query"))
        )
        search_input.clear()
        search_input.send_keys(query)
        
        search_btn = self.driver.find_element(By.CSS_SELECTOR, "button.search_button")
        self.driver.execute_script("arguments[0].click();", search_btn)
        time.sleep(3)
        
        # Ожидание для установки лимита (только для первого запроса)
        if is_first:
            self.wait_for_manual_limit(5)
        
        # Проверка результатов
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ul.report_items > li"))
            )
            return True
        except TimeoutException:
            try:
                no_results = self.driver.find_element(By.XPATH, "//div[contains(text(), 'ничего не найдено')]")
                logger.warning("Ничего не найдено")
                return False
            except:
                return False
    
    def parse_titles(self):
        titles = []
        try:
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
                except:
                    continue
        except Exception as e:
            logger.error(f"Ошибка парсинга: {e}")
        return titles
    
    def go_to_next_page(self):
        try:
            pagination_links = self.driver.find_elements(By.CSS_SELECTOR, "ul.pagination li a")
            for link in pagination_links:
                text = link.text.strip()
                if text in [">", "»"]:
                    class_name = link.get_attribute("class") or ""
                    if "disabled" not in class_name:
                        link.click()
                        time.sleep(3)
                        return True
            return False
        except:
            return False
    
    def save_to_csv(self, titles, subclass):
        if not titles:
            logger.warning(f"Нет данных для сохранения {subclass}")
            return
        
        filename = os.path.join(self.output_dir, f"patents_{subclass}.csv")
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["title"])
            for title in titles:
                writer.writerow([title])
        logger.info(f"Сохранено {len(titles)} записей в {filename}")
    
    def collect_patents(self, subclass, is_first=False):
        query = f"IC=({subclass})"
        if not self.perform_search(query, is_first):
            return []
        
        all_titles = []
        page = 1
        
        while page <= 10:
            logger.info(f"Страница {page}")
            titles = self.parse_titles()
            if not titles:
                break
            
            all_titles.extend(titles)
            
            if len(titles) < 10:
                logger.info("На странице меньше 10 патентов - последняя")
                break
            
            if not self.go_to_next_page():
                break
            page += 1
        
        self.save_to_csv(all_titles, subclass)
        return all_titles
    
    def run(self):
        self.setup_driver()
        try:
            for i, subclass in enumerate(MPK_SUBCLASSES, 1):
                logger.info(f"\n{i} из {len(MPK_SUBCLASSES)}: {subclass}")
                is_first = (i == 1)
                titles = self.collect_patents(subclass, is_first)
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
