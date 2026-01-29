import time
import sys
import os
import requests
import undetected_chromedriver as uc # Специальная библиотека для обхода
from selenium.webdriver.common.by import By

# --- НАСТРОЙКИ ---
URL_WARMUP = "https://titanshina.ua/test/?tyres=1"
URL_MAIN = "https://titanshina.ua/test/"
FINAL_TEXT = "the end" 
MAX_WAIT_MINUTES = 15

TG_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TG_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram(message):
    if not TG_TOKEN: return
    try:
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                      data={"chat_id": TG_CHAT_ID, "text": f"🚗 [Шина]: {message}"})
    except: pass

def run_shina_task():
    print(">>> ЗАПУСК 'ШИНА' (STEALTH MODE)...")
    
    # Настройки для маскировки
    options = uc.ChromeOptions()
    options.add_argument("--headless") # Без монитора
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    # Запускаем "невидимый" драйвер
    # version_main=144 заставит его скачать драйвер именно под 144-й Хром
    driver = uc.Chrome(options=options, version_main=144)


    try:
        # 1. РАЗОГРЕВ
        print(f"Разогрев: {URL_WARMUP}")
        driver.get(URL_WARMUP)
        time.sleep(10) # Ждем чуть дольше, чтобы Cloudflare пропустил
        
        # Проверяем, прошли ли мы защиту
        body_text = driver.find_element(By.TAG_NAME, "body").text
        if "Verify you are human" in body_text:
            print("!!! CLOUDFLARE НЕ ПУСКАЕТ. Попытка подождать 20 сек...")
            time.sleep(20)
        
        for i in range(1, 4):
            print(f"Update {i}...")
            driver.refresh()
            time.sleep(8) # Паузы побольше, чтобы не злить защиту

        # 2. ОСНОВНОЙ ПРОЦЕСС
        print(f"Основной процесс: {URL_MAIN}")
        driver.get(URL_MAIN)
        time.sleep(10)
        
        start_time = time.time()
        
        # Печатаем проверку
        initial_source = driver.find_element(By.TAG_NAME, "body").text
        print(f"--- ВИДИМ НА ЭКРАНЕ ---\n{initial_source[:200]}\n-----------------------")
        
        if "Verify you are human" in initial_source:
             send_telegram("❌ БЛОКИРОВКА: Cloudflare не пускает бота (капча).")
             sys.exit(1)

        while True:
            if time.time() - start_time > (MAX_WAIT_MINUTES * 60):
                final_source = driver.find_element(By.TAG_NAME, "body").text[:200]
                send_telegram(f"❌ ТАЙМ-АУТ. Экран:\n'{final_source}...'")
                sys.exit(1)

            page_text_lower = driver.find_element(By.TAG_NAME, "body").text.lower()
            
            if FINAL_TEXT in page_text_lower:
                send_telegram("✅ УСПЕХ! Найдена надпись 'the end'.")
                break
                
            time.sleep(5)

    except Exception as e:
        send_telegram(f"⚠️ СБОЙ: {e}")
        sys.exit(1)
    finally:
        driver.quit()

if __name__ == "__main__":
    run_shina_task()
