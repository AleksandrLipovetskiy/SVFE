import subprocess
import logging
from datetime import datetime

# Определяем цветовые коды 
GREEN = '\033[0;32m'
RED = '\033[0;31m'
NC = '\033[0m' # Без цвета 

# Файл для логирования 
LOG_FILE = "./check_log.log"

# Файл с IP-адресами 
CONFIG_FILE = "./ip_addres.conf"

# Настройка логирования
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(message)s')

# Проверка существования файла конфигурации
import os
if not os.path.isfile(CONFIG_FILE):
    message = f"Файл конфигурации {CONFIG_FILE} не найден."
    print(message)
    logging.info(message)
    exit(1)

# Функция для проверки доступности IP 
def check_ip(ip, name):
    try:
        subprocess.check_output(["ping", "-c", "3", ip], stderr=subprocess.STDOUT)
        message = f"{GREEN}{datetime.now()}: {name} по IP-{ip} OK - доступен{NC}"
        print(message)
        logging.info(message)
        return True
    except subprocess.CalledProcessError:
        message = f"{RED}{datetime.now()}: {name} по IP-{ip} недоступен{NC}"
        print(message)
        logging.info(message)
        return False

# Функция для проверки доступности порта с таймаутом 
def check_port(ip_port):
    ip, port = ip_port.split(':')
    try:
        # Проверка порта с помощью /dev/tcp с таймаутом в 5 секунд 
        subprocess.check_output(["timeout", "5", "bash", "-c", f"echo > /dev/tcp/{ip}/{port}"], stderr=subprocess.DEVNULL)
        message = f"{GREEN}{datetime.now()}: Порт {port} на {ip} доступен{NC}"
        print(message)
        logging.info(message)
    except subprocess.CalledProcessError:
        message = f"{RED}{datetime.now()}: Порт {port} на {ip} недоступен или таймаут{NC}"
        print(message)
        logging.info(message)

# Загружаем ассоциативный массив из файла конфигурации 
IP_ADDRESSES = {}

with open(CONFIG_FILE, 'r') as config_file:
    for line in config_file:
        if '=' in line:  # Пропускаем строки без знака равенства
            key, value = line.strip().split('=', 1)
            IP_ADDRESSES[key] = value

# Проверка IP и портов для каждого IP 
for name, ip_port in IP_ADDRESSES.items():
    print(f"Проверка {name} ({ip_port})")

    # Проверяем доступность IP 
    ip, port = ip_port.split(':', 1)  # Разделяем IP и порт для проверки 
    check_ip(ip, name)

    # Если порт равен 'ANY', пропускаем проверку порта 
    if port == 'ANY':
        message = f"Порт для {ip} установлен как 'ANY'. Пропускаем проверку порта."
        print(message)
        logging.info(message)
    else:
        # Проверяем доступность порта 
        check_port(ip_port)