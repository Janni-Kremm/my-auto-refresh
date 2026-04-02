import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# -----------------------------
# НАСТРОЙКИ
# -----------------------------
WARMUP_URL = "https://titanshina.ua/test/?tyres=1"
MAIN_URL = "https://titanshina.ua/test/"

WARMUP_REFRESH_COUNT = 5
STEP_TARGET = 12


# -----------------------------
# ДРАЙВЕР
# -----------------------------
def create_driver():
    options = Options()

    # ВАЖНО: имитация реального браузера
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")

    # User-Agent (как у обычного Chrome)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=options)

    # Убираем признаки автоматизации
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    return driver


# -----------------------------
# WARMUP
# -----------------------------
def warmup(driver):
    print(f"Разогрев: {WARMUP_URL}")
    driver.get(WARMUP_URL)

    time.sleep(3)

    for i in range(WARMUP_REFRESH_COUNT):
        print(f"Warmup refresh {i + 1}")
        driver.refresh()
        time.sleep(2)


# -----------------------------
# ОСНОВНОЙ МОНИТОРИНГ
# -----------------------------
def monitor(driver):
    print(f"Переход: {MAIN_URL}")
    driver.get(MAIN_URL)

    time.sleep(5)

    step = 0
    timeout = 180  # максимум ожидания (сек)

    start_time = time.time()

    while True:
        elapsed = time.time() - start_time

        if elapsed > timeout:
            print("Timeout reached")
            break

        page_text = driver.page_source

        # Проверяем шаг
        if "step: 12" in page_text:
            step = 12

        print("Текущий статус проверяется...")

        if (
            "Статус загрузки: Запрещено" in page_text
            and "step: 12" in page_text
            and "Загрузка завершена" in page_text
        ):
            print("\n✅ ГОТОВО!")
            print("Статус загрузки: Запрещено")
            print("step: 12")
            print("Загрузка завершена")
            return True

        time.sleep(5)

    return False


# -----------------------------
# MAIN
# -----------------------------
def main():
    print(">>> ЗАПУСК 'ШИНА' (STABLE MODE)...")

    driver = create_driver()

    try:
        warmup(driver)
        success = monitor(driver)

        if not success:
            print("❌ Не удалось дождаться результата")
            exit(1)

    except Exception as e:
        print("Ошибка:", str(e))
        exit(1)

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
