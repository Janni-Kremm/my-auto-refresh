import time
import sys
import os
import requests
import re # Библиотека для поиска текста "step: 5" и т.д.
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# --- НАСТРОЙКИ ---
URL_WARMUP = "https://titanshina.ua/test/?tyres=1" # Ссылка для разогрева
URL_MAIN = "https://titanshina.ua/test/"           # Основная ссылка
FINAL_TEXT = "the end"                            # Финальная надпись (проверьте точность!)
MAX_WAIT_MINUTES = 10                              # Сколько ждать основного процесса

# Получаем ключи (те же самые, что и раньше)
TG_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TG_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram(message):
    if not TG_TOKEN or not TG_CHAT_ID:
        print(">>> ОШИБКА: Нет ключей Telegram!")
        return
    # Добавляем пометку "Шина" в начало сообщения
    full_message = f"🚗 [Шина]: {message}"
    try:
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                      data={"chat_id": TG_CHAT_ID, "text": full_message})
    except: pass

def run_shina_task():
    print(">>> ЗАПУСК 'ШИНА'...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        # ЧАСТЬ 1: РАЗОГРЕВ (3 обновления первой ссылки)
        print(f"1. Разогрев: {URL_WARMUP}")
        driver.get(URL_WARMUP)
        time.sleep(3)
        
        for i in range(1, 4): # 3 раза
            print(f"   Обновление {i}/3...")
            driver.refresh()
            time.sleep(3)

        # ЧАСТЬ 2: ОСНОВНОЙ ПРОЦЕСС
        print(f"2. Основной процесс: {URL_MAIN}")
        driver.get(URL_MAIN)
        
        # Теперь мы должны следить за надписями на экране
        start_time = time.time()
        last_step_seen = "Начало"
        
        while True:
            # 1. Проверяем время (чтобы не висеть вечно)
            if time.time() - start_time > (MAX_WAIT_MINUTES * 60):
                error_msg = f"❌ ОШИБКА: Тайм-аут! Застряли на шаге '{last_step_seen}'."
                print(error_msg)
                send_telegram(error_msg)
                sys.exit(1)

            # 2. Читаем страницу
            page_text = driver.find_element("tag name", "body").text.lower() # Весь текст маленькими буквами
            
            # 3. Ищем ошибку (если на странице появилось слово error или fail)
            # Если у них ошибки пишутся специфически (например "Error 500"), можно уточнить
            if "error" in page_text or "fatal" in page_text:
                error_msg = f"❌ ОШИБКА на странице! Последний шаг: '{last_step_seen}'. Текст: {page_text[:100]}..."
                print(error_msg)
                send_telegram(error_msg)
                sys.exit(1)

            # 4. Проверяем ФИНАЛ
            if FINAL_TEXT in page_text:
                success_msg = "✅ УСПЕХ! Процесс завершен (the end)."
                print(success_msg)
                send_telegram(success_msg)
                break

            # 5. Пытаемся понять, какой сейчас шаг (ищем текст типа "step: 5")
            # Это чисто для логов, чтобы вы знали, где мы
            try:
                # Ищем слово step: и цифры после него
                found_step = re.search(r"step:\s*(\d+)", page_text) 
                if found_step:
                    current_step = f"Step {found_step.group(1)}"
                    if current_step != last_step_seen:
                        print(f"   >> Сейчас идет: {current_step}")
                        last_step_seen = current_step
            except: pass

            # Ждем секунду перед следующей проверкой
            time.sleep(2)

    except Exception as e:
        msg = f"⚠️ СБОЙ СКРИПТА: {e}"
        print(msg)
        send_telegram(msg)
        sys.exit(1)
    finally:
        driver.quit()

if __name__ == "__main__":
    run_shina_task()
