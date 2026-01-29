import time
import sys
import os
import requests
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# --- НАСТРОЙКИ ---
URL_WARMUP = "https://titanshina.ua/test/?tyres=1"
URL_MAIN = "https://titanshina.ua/test/"
FINAL_TEXT = "the end"  # Убедитесь, что там именно так (маленькими буквами)!
MAX_WAIT_MINUTES = 15   # Дадим чуть больше времени

TG_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TG_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram(message):
    if not TG_TOKEN: return
    try:
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                      data={"chat_id": TG_CHAT_ID, "text": f"🚗 [Шина]: {message}"})
    except: pass

def run_shina_task():
    print(">>> ЗАПУСК 'ШИНА' v2 (DEBUG)...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Добавляем размер окна, вдруг элементы скрыты на маленьком экране
    chrome_options.add_argument("--window-size=1920,1080") 
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        # 1. РАЗОГРЕВ
        print(f"Разогрев: {URL_WARMUP}")
        driver.get(URL_WARMUP)
        time.sleep(5)
        for i in range(1, 4):
            print(f"Update {i}...")
            driver.refresh()
            time.sleep(5)

        # 2. ОСНОВНОЙ ПРОЦЕСС
        print(f"Основной процесс: {URL_MAIN}")
        driver.get(URL_MAIN)
        time.sleep(5) # Ждем начальной прогрузки
        
        start_time = time.time()
        
        # Печатаем первые 500 символов страницы в лог, чтобы понять, что там
        initial_source = driver.find_element("tag name", "body").text
        print(f"--- НАЧАЛО СТРАНИЦЫ (DEBUG) ---\n{initial_source[:300]}\n-------------------------------")

        while True:
            # Тайм-аут
            if time.time() - start_time > (MAX_WAIT_MINUTES * 60):
                # При тайм-ауте пришлем вам текст страницы, чтобы понять причину
                final_source = driver.find_element("tag name", "body").text[:200]
                send_telegram(f"❌ ТАЙМ-АУТ! (15 мин). Скрипт видит на экране вот это:\n'{final_source}...'")
                sys.exit(1)

            # Читаем текст
            page_text_raw = driver.find_element("tag name", "body").text
            page_text_lower = page_text_raw.lower()
            
            # Проверка ФИНАЛА
            if FINAL_TEXT in page_text_lower:
                send_telegram("✅ УСПЕХ! Найдена надпись 'the end'.")
                break
                
            # Проверка ОШИБОК (fatal error и т.д.)
            if "fatal error" in page_text_lower or "exception" in page_text_lower:
                send_telegram(f"❌ КРИТИЧЕСКАЯ ОШИБКА НА САЙТЕ:\n{page_text_raw[:150]}")
                sys.exit(1)

            # Логирование шагов (просто в консоль GitHub, чтобы не спамить в телегу)
            # Ищем любые цифры рядом со словами step/шаг
            if "step" in page_text_lower or "шаг" in page_text_lower:
                print("Вижу слово 'step' или 'шаг'...")
            
            time.sleep(5)

    except Exception as e:
        send_telegram(f"⚠️ СБОЙ КОДА: {e}")
        sys.exit(1)
    finally:
        driver.quit()

if __name__ == "__main__":
    run_shina_task()
