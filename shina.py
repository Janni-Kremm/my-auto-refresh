import time
import sys
import os
import requests
import undetected_chromedriver as uc
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
    print(">>> ЗАПУСК 'ШИНА' (STEALTH MODE + VERSION FIX)...")
    
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    # ФИКС ВЕРСИИ: Просим библиотеку использовать ту версию, которая реально стоит в системе
    # Обычно на GitHub Actions это сейчас 144 или 145. Ставим version_main=144 (самый безопасный вариант сейчас)
    try:
        driver = uc.Chrome(options=options, version_main=144)
    except Exception as e:
        print(f"Попытка с версией 144 не удалась ({e}), пробую авто-определение...")
        driver = uc.Chrome(options=options) # Пробуем без версии, если вдруг там уже обновили Chrome

    try:
        # 1. РАЗОГРЕВ
        print(f"Разогрев: {URL_WARMUP}")
        driver.get(URL_WARMUP)
        time.sleep(15) 
        
        # Проверяем защиту
        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text
            if "Verify you are human" in body_text:
                print("!!! Cloudflare detected. Жду 30 сек...")
                time.sleep(30)
        except: pass
        
        for i in range(1, 4):
            print(f"Update {i}...")
            driver.refresh()
            time.sleep(10)

        # 2. ОСНОВНОЙ ПРОЦЕСС
        print(f"Основной процесс: {URL_MAIN}")
        driver.get(URL_MAIN)
        time.sleep(10)
        
        start_time = time.time()
        
        # Печатаем, что видим
        try:
            initial_source = driver.find_element(By.TAG_NAME, "body").text
            print(f"--- ВИДИМ НА ЭКРАНЕ ---\n{initial_source[:200]}\n-----------------------")
            
            if "Verify you are human" in initial_source:
                 send_telegram("❌ БЛОКИРОВКА: Cloudflare не пускает бота (капча).")
                 # Не выходим сразу, вдруг пропустит позже, но предупреждаем
        except:
            print("Не удалось прочитать текст страницы (возможно, еще грузится)")

        while True:
            if time.time() - start_time > (MAX_WAIT_MINUTES * 60):
                try:
                    final_source = driver.find_element(By.TAG_NAME, "body").text[:200]
                except: final_source = "???"
                send_telegram(f"❌ ТАЙМ-АУТ. Экран:\n'{final_source}...'")
                sys.exit(1)

            try:
                page_text_lower = driver.find_element(By.TAG_NAME, "body").text.lower()
                
                if FINAL_TEXT in page_text_lower:
                    send_telegram("✅ УСПЕХ! Найдена надпись 'the end'.")
                    break
            except: pass
                
            time.sleep(5)

    except Exception as e:
        send_telegram(f"⚠️ СБОЙ: {e}")
        sys.exit(1)
    finally:
        try:
            driver.quit()
        except: pass

if __name__ == "__main__":
    run_shina_task()
