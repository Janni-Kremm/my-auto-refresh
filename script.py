import time
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

TARGET_URL = "https://hlorka.ua/test/"
TOTAL_STEPS = 9
FINAL_TEXT = "this is end"

def run_browser_task():
    print(">>> ЗАПУСК GITHUB ACTION...")
    
    # Настройки для работы без монитора (headless)
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        print(f"Открываю: {TARGET_URL}")
        driver.get(TARGET_URL)
        time.sleep(5)

        found = False
        for i in range(1, TOTAL_STEPS + 1):
            print(f"--- Шаг {i} ---")
            
            if i == 8:
                print("!!! 8-й шаг. Жду 30 сек...")
                driver.refresh()
                # Проверяем текст во время ожидания
                for _ in range(10):
                    time.sleep(3)
                    if FINAL_TEXT in driver.page_source:
                        print("НАЙДЕНО (досрочно)!")
                        found = True
                        break
                if found: break
            else:
                driver.refresh()
                time.sleep(5)
                if FINAL_TEXT in driver.page_source:
                    print(f"НАЙДЕНО (на шаге {i})!")
                    found = True
                    break
        
        # Финальная проверка
        if not found:
            time.sleep(3)
            if FINAL_TEXT in driver.page_source:
                found = True

        if found:
            print(f">>> УСПЕХ: '{FINAL_TEXT}' найден.")
        else:
            print(f">>> ОШИБКА: '{FINAL_TEXT}' НЕ найдена!")
            # Эта команда заставит GitHub пометить выполнение красным крестиком (ошибка)
            sys.exit(1) 

    except Exception as e:
        print(f"КРИТИЧЕСКАЯ ОШИБКА: {e}")
        sys.exit(1)
    finally:
        driver.quit()

if __name__ == "__main__":
    run_browser_task()
