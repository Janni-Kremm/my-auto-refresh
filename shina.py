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

    # небольшой антидетект-минимум
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    )

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    return driver


def run_shina_task():
    print(">>> ЗАПУСК 'ШИНА' (STEP MONITOR MODE)...")

    driver = None

    # --- запуск драйвера ---
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
        # --- 1. РАЗОГРЕВ ---
        print(f"Разогрев: {URL_WARMUP}")
        driver.get(URL_WARMUP)
        time.sleep(5)

        # несколько обновлений
        for i in range(3):
            print(f"Warmup refresh {i+1}")
            driver.refresh()
            time.sleep(5)

        # --- 2. ОСНОВНОЙ URL ---
        print(f"Переход: {URL_MAIN}")
        driver.get(URL_MAIN)

        start_time = time.time()

        last_step = None

        while True:
            if time.time() - start_time > MAX_WAIT_MINUTES * 60:
                send_telegram("❌ TIMEOUT: не дошли до step 12")
                sys.exit(1)

            try:
                body_text = driver.find_element(By.TAG_NAME, "body").text.lower()

                # ищем step
                if "step:" in body_text:
                    for line in body_text.split("\n"):
                        if "step:" in line:
                            last_step = line.strip()
                            print(f"Текущий прогресс: {last_step}")

                # проверка финала
                if "step: 12" in body_text and "загрузка завершена" in body_text:
                    send_telegram(f"✅ ГОТОВО:\n{last_step}\nЗагрузка завершена")
                    break

            except Exception as e:
                print(f"Ошибка чтения страницы: {e}")

            time.sleep(3)

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
