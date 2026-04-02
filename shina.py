import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


WARMUP_URL = "https://titanshina.ua/test/?tyres=1"
MAIN_URL = "https://titanshina.ua/test/"
WARMUP_REFRESH_COUNT = 5
TIMEOUT = 180


def create_driver():
    options = Options()

    # Важно для GitHub Actions / серверов
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--window-size=1920,1080")

    # User-Agent как у обычного браузера
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=options)
    return driver


def warmup(driver):
    print(f"Разогрев: {WARMUP_URL}")
    driver.get(WARMUP_URL)
    time.sleep(3)

    for i in range(WARMUP_REFRESH_COUNT):
        print(f"Warmup refresh {i + 1}")
        driver.refresh()
        time.sleep(2)


def monitor(driver):
    print(f"Переход: {MAIN_URL}")
    driver.get(MAIN_URL)

    start_time = time.time()

    while True:
        elapsed = time.time() - start_time

        if elapsed > TIMEOUT:
            print("❌ Timeout reached")
            return False

        page = driver.page_source

        print("Проверка состояния...")

        if (
            "Статус загрузки: Запрещено" in page
            and "step: 12" in page
            and "Загрузка завершена" in page
        ):
            print("\n✅ ГОТОВО!")
            print("Статус загрузки: Запрещено")
            print("step: 12")
            print("Загрузка завершена")
            return True

        time.sleep(5)


def main():
    print(">>> ЗАПУСК 'ШИНА' (FULL MODE)...")

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
