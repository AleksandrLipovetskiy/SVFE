import subprocess
import logging
from datetime import datetime

# Определяем цветовые коды
GREEN = '\033[0;32m'
RED = '\033[0;31m'
NC = '\033[0m'  # Без цвета

# Файл для логирования
LOG_FILE = "check_log.log"

# Явный путь к файлу с IP-адресами
CONFIG_FILE = "/path/to/your/ip_addres.conf"  # Замените на ваш путь

# Настройка логирования
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(message)s')

# Функция для проверки доступности IP
def check_ip(ip):
    try:
        output = subprocess.check_output(['ping', '-c', '3', ip], stderr=subprocess.STDOUT)
        message = f"{GREEN}{datetime.now()}: {ip} OK - доступен{NC}"
        print(message)
        logging.info(message)
        return True
    except subprocess.CalledProcessError:
        message = f"{RED}{datetime.now()}: {ip} недоступен{NC}"
        print(message)
        logging.info(message)
        return False

# Функция для проверки доступности порта с таймаутом, используя bash
def check_port(ip_port):
    ip, port = ip_port.split(':')
    try:
        # Запускаем bash команду для проверки доступности порта с таймаутом 5 секунд
        subprocess.check_output(['bash', '-c', f'timeout 5 bash -c "echo > /dev/tcp/{ip}/{port}"'], stderr=subprocess.STDOUT)
        message = f"{GREEN}{datetime.now()}: Порт {port} на {ip} доступен{NC}"
        print(message)
        logging.info(message)
    except subprocess.CalledProcessError as e:
        message = f"{RED}{datetime.now()}: Порт {port} на {ip} недоступен или таймаут{NC}"
        print(message)
        logging.info(message)

# Загружаем ассоциативный массив из файла конфигурации
IP_ADDRESSES = {}

with open(CONFIG_FILE, 'r') as config_file:
    for line in config_file:
        key, value = line.strip().split('=')
        IP_ADDRESSES[key] = value

# Проверка IP и портов для каждого IP
for name, ip_port in IP_ADDRESSES.items():
    ip, port = ip_port.split(':')  # Извлекаем IP и порт для проверки

    print(f"Проверка {name} ({ip_port})...")

    # Сначала проверяем доступность IP
    if check_ip(ip):
        print("Пропускаем проверку порта, так как IP доступен.")
        logging.info("Пропускаем проверку порта, так как IP доступен.")
    else:
        # Если IP недоступен, проверяем порт
        check_port(ip_port)