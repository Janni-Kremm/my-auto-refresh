import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


WARMUP_URL = "https://titanshina.ua/test/?tyres=1"
MAIN_URL = "https://titanshina.ua/test/"
WARMUP_REFRESH_COUNT = 5
TIMEOUT = 180


def create_driver():
    options = Options()

    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--window-size=1920,1080")

    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    return webdriver.Chrome(options=options)


def warmup(driver):
    print(f"Разогрев: {WARMUP_URL}")
    driver.get(WARMUP_URL)
    time.sleep(3)

    for i in range(WARMUP_REFRESH_COUNT):
        print(f"Warmup refresh {i + 1}")
        driver.refresh()
        time.sleep(2)


def debug_page(driver):
    """Функция диагностики состояния страницы"""
    print("\n--- DEBUG PAGE ---")

    title = driver.title
    print("TITLE:", title)

    html = driver.page_source

    print("\n--- HTML SNIPPET ---")
    print(html[:1000])  # первые 1000 символов

    print("\n--- CHECKS ---")

    print("Contains 'Статус загрузки: Запрещено':",
          "Статус загрузки: Запрещено" in html)

    print("Contains 'step: 12':",
          "step: 12" in html)

    print("Contains 'Загрузка завершена':",
          "Загрузка завершена" in html)

    # Попробуем вытащить step грубо
    step = None
    if "step:" in html:
        try:
            step = html.split("step:")[1].split("<")[0].strip()
        except:
            pass

    print("Detected STEP:", step)

    print("--- END DEBUG ---\n")


def monitor(driver):
    print(f"Переход: {MAIN_URL}")
    driver.get(MAIN_URL)

    start_time = time.time()

    while True:
        elapsed = time.time() - start_time

        if elapsed > TIMEOUT:
            print("❌ Timeout reached")
            return False

        debug_page(driver)

        html = driver.page_source

        if (
            "Статус загрузки: Запрещено" in html
            and "step: 12" in html
            and "Загрузка завершена" in html
        ):
            print("\n✅ ГОТОВО!")
            return True

        time.sleep(5)


def main():
    print(">>> ЗАПУСК 'ШИНА' (FULL MODE WITH DEBUG)...")

    driver = create_driver()

    try:
        warmup(driver)
        success = monitor(driver)

        if not success:
            exit(1)

    except Exception as e:
        print("❌ Ошибка:", str(e))
        exit(1)

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
