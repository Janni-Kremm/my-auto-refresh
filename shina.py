import time
import sys
import os
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


# --- НАСТРОЙКИ ---
URL_WARMUP = "https://titanshina.ua/test/?tyres=1"
URL_MAIN = "https://titanshina.ua/test/"
FINAL_TEXT = "the end"
MAX_WAIT_MINUTES = 15

TG_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TG_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def send_telegram(message):
    if not TG_TOKEN:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            data={"chat_id": TG_CHAT_ID, "text": f"🚗 [Шина]: {message}"}
        )
    except:
        pass


def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    return driver


def run_shina_task():
    print(">>> ЗАПУСК 'ШИНА' (STABLE SELENIUM MODE)...")

    driver = None

    # --- RETRY ---
    for attempt in range(3):
        try:
            driver = create_driver()
            break
        except Exception as e:
            print(f"Ошибка запуска драйвера (попытка {attempt+1}): {e}")
            time.sleep(5)

    if not driver:
        send_telegram("❌ Не удалось запустить браузер")
        sys.exit(1)

    try:
        # 1. РАЗОГРЕВ
        print(f"Разогрев: {URL_WARMUP}")
        driver.get(URL_WARMUP)
        time.sleep(15)

        # Проверка Cloudflare
        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text
            if "Verify you are human" in body_text:
                print("!!! Cloudflare detected. Жду...")
                time.sleep(30)
        except:
            pass

        # Refresh
        for i in range(3):
            print(f"Refresh {i+1}")
            driver.refresh()
            time.sleep(10)

        # 2. ОСНОВНОЙ ПРОЦЕСС
        print(f"Основной процесс: {URL_MAIN}")
        driver.get(URL_MAIN)
        time.sleep(10)

        start_time = time.time()

        # Лог страницы
        try:
            initial_source = driver.find_element(By.TAG_NAME, "body").text
            print(f"--- ВИДИМ ---\n{initial_source[:200]}\n-------------")

            if "Verify you are human" in initial_source:
                send_telegram("❌ Cloudflare блокирует доступ")
        except:
            print("Не удалось прочитать страницу")

        # Ожидание
        while True:
            if time.time() - start_time > MAX_WAIT_MINUTES * 60:
                try:
                    final_source = driver.find_element(By.TAG_NAME, "body").text[:200]
                except:
                    final_source = "???"

                send_telegram(f"❌ TIMEOUT: {final_source}")
                sys.exit(1)

            try:
                page_text = driver.find_element(By.TAG_NAME, "body").text.lower()

                if FINAL_TEXT in page_text:
                    send_telegram("✅ SUCCESS: найден 'the end'")
                    break
            except:
                pass

            time.sleep(5)

    except Exception as e:
        send_telegram(f"⚠️ ERROR: {e}")
        sys.exit(1)

    finally:
        try:
            driver.quit()
        except:
            pass


if __name__ == "__main__":
    run_shina_task()
