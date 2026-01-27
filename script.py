import time
import sys
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Получаем ключи
TG_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TG_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram(message):
    if not TG_TOKEN or not TG_CHAT_ID:
        print(">>> ОШИБКА: Нет ключей Telegram (проверьте Secrets)!")
        return
    
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    data = {
        "chat_id": TG_CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print(">>> Telegram: Сообщение отправлено!")
        else:
            print(f">>> Telegram ОШИБКА: {response.text}")
    except Exception as e:
        print(f">>> Telegram СБОЙ: {e}")

TARGET_URL = "https://hlorka.ua/test/"
TOTAL_STEPS = 9
FINAL_TEXT = "this is end"

def run_browser_task():
    print(">>> ЗАПУСК СКРИПТА (ВЕРСИЯ С ТЕЛЕГРАМОМ)...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        driver.get(TARGET_URL)
        time.sleep(5)

        found = False
        for i in range(1, TOTAL_STEPS + 1):
            print(f"--- Шаг {i} ---")
            
            if i == 8:
                print("8-й шаг (ожидание)...")
                driver.refresh()
                # Ждем
                for _ in range(10): 
                    time.sleep(3)
                    if FINAL_TEXT in driver.page_source:
                        found = True
                        break
                if found: break
            else:
                driver.refresh()
                time.sleep(5)
                if FINAL_TEXT in driver.page_source:
                    found = True
                    break
        
        if not found:
            time.sleep(3)
            if FINAL_TEXT in driver.page_source:
                found = True

        if found:
            print("УСПЕХ.")
            send_telegram(f"✅ УСПЕХ! Скрипт нашел надпись '{FINAL_TEXT}'.")
        else:
            print("ОШИБКА.")
            send_telegram(f"❌ ОШИБКА! Надпись '{FINAL_TEXT}' НЕ найдена.")
            sys.exit(1)

    except Exception as e:
        msg = f"⚠️ Скрипт сломался: {e}"
        print(msg)
        send_telegram(msg)
        sys.exit(1)
    finally:
        driver.quit()

if __name__ == "__main__":
    run_browser_task()
