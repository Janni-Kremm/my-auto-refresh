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
        print(">>> ОШИБКА: Нет ключей Telegram!")
        return
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    data = {"chat_id": TG_CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except:
        pass

# НАСТРОЙКИ
TARGET_URL = "https://hlorka.ua/test/"
FINAL_TEXT = "this is end"
MAX_TIME_MINUTES = 15  # Максимальное время работы скрипта (15 минут)

def run_browser_task():
    print(">>> ЗАПУСК: Режим 'До победного'...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    start_time = time.time()
    # 15 минут в секундах
    max_duration = MAX_TIME_MINUTES * 60 

    try:
        driver.get(TARGET_URL)
        time.sleep(5) # Даем прогрузиться первый раз

        step = 0
        success = False

        while True:
            step += 1
            current_duration = time.time() - start_time
            
            # Если скрипт работает слишком долго (больше 15 мин) - останавливаем
            if current_duration > max_duration:
                print("!!! ПРЕВЫШЕНО ВРЕМЯ ОЖИДАНИЯ.")
                send_telegram(f"❌ НЕУДАЧА: Прошло {MAX_TIME_MINUTES} минут, а надпись так и не появилась.")
                break

            print(f"--- Попытка №{step} (прошло {int(current_duration)} сек) ---")

            # 1. Проверяем, вдруг надпись УЖЕ есть (до обновления)
            if FINAL_TEXT in driver.page_source:
                print("!!! НАЙДЕНО (сразу)!")
                success = True
                break

            # 2. Обновляем страницу
            try:
                print("Обновляю...")
                driver.refresh()
            except Exception as e:
                print(f"Ошибка обновления (не страшно): {e}")

            # 3. Ждем после обновления (УМНОЕ ОЖИДАНИЕ)
            # Вместо тупого time.sleep(15), мы будем проверять каждую секунду в течение 20 секунд
            # Это решит проблему "долгих редиректов" и "быстрых появлений"
            print("Жду прогрузки и ищу текст...")
            found_during_wait = False
            for _ in range(20): # Ждем до 20 секунд
                time.sleep(1)
                try:
                    if FINAL_TEXT in driver.page_source:
                        found_during_wait = True
                        break
                except:
                    pass # Если страница еще белая/пустая, игнорируем ошибку
            
            if found_during_wait:
                print("!!! НАЙДЕНО (во время ожидания)!")
                success = True
                break
            
            # Если не нашли за 20 секунд - цикл while повторится, и мы обновим снова.

        if success:
            msg = f"✅ УСПЕХ! Надпись '{FINAL_TEXT}' найдена на шаге {step}."
            print(msg)
            send_telegram(msg)
        else:
            # Если вышли из цикла по тайм-ауту
            sys.exit(1)

    except Exception as e:
        msg = f"⚠️ КРИТИЧЕСКИЙ СБОЙ: {e}"
        print(msg)
        send_telegram(msg)
        sys.exit(1)
    finally:
        driver.quit()

if __name__ == "__main__":
    run_browser_task()
