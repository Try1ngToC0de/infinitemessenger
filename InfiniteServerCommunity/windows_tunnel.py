import subprocess
import time
import re
import requests
import sys
import logging
from jsonbox import JB_API, JB_URL

# ====== НАСТРОЙКА ЛОГИРОВАНИЯ ======
logger = logging.getLogger('tunnel')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

file_handler = logging.FileHandler('tunnel.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# ====== ОСНОВНОЙ КОД ======
def update_jsonbox(url):
    try:
        logger.info(f"Отправка адреса в JsonBox: {url}")
        r = requests.post(JB_URL, json={
            "api_key": JB_API,
            "data": {"server_url": url}
        })
        if r.status_code == 200:
            logger.info(f"✅ Адрес обновлён: {url}")
            return True
        else:
            logger.error(f"❌ Ошибка JsonBox: {r.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Ошибка сети: {e}")
        return False

def get_cloudpub_url_from_output(text):
    # Ищем адрес, который выдаёт CloudPub
    match = re.search(r'https://([a-zA-Z0-9-]+)\.cloudpub\.ru', text)
    if match:
        return f"https://{match.group(1)}.cloudpub.ru"
    return None

def run_tunnel():
    logger.info("🚀 Сервис туннелирования (CloudPub) запущен")
    
    # Путь к clo.exe (он в той же папке)
    clo_path = "./clo.exe"
    
    while True:
        logger.info("Запускаю туннель через CloudPub...")
        
        # Команда для публикации локального порта 7089
        cmd = [clo_path, "publish", "http", "7089"]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        cloudpub_url = None
        
        if process.stdout is None:
            logger.error("❌ Не удалось получить вывод процесса")
            time.sleep(10)
            continue
        
        for line in process.stdout:
            logger.info(line.strip())
            
            if not cloudpub_url:
                url = get_cloudpub_url_from_output(line)
                if url:
                    cloudpub_url = url
                    if update_jsonbox(cloudpub_url):
                        logger.info("✅ Адрес успешно отправлен в JsonBox!")
        
        logger.warning("❌ Туннель упал. Перезапуск через 10 секунд...")
        time.sleep(10)

if __name__ == "__main__":
    try:
        run_tunnel()
    except KeyboardInterrupt:
        logger.info("👋 Завершение работы по запросу пользователя")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"💥 Критическая ошибка: {e}")
        sys.exit(1)
