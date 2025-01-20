#!/bin/bash 

# Определяем цветовые коды 
GREEN='\033[0;32m' 
RED='\033[0;31m' 
NC='\033[0m' # Без цвета 

# Файл для логирования 
LOG_FILE="./check_log.log" 

# Файл с IP-адресами 
CONFIG_FILE="./ip_addres.conf" 

# Проверка существования файла конфигурации
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "Файл конфигурации $CONFIG_FILE не найден." | tee -a "$LOG_FILE"
    exit 1
fi

# Функция для проверки доступности IP 
check_ip() { 
    local ip=$1 
    local name=$2
    if ping -c 3 "$ip" &>> "$LOG_FILE"; then 
        printf "${GREEN}$(date): $name по IP-$ip OK - доступен${NC}\n" | tee -a "$LOG_FILE" 
        return 0 
    else 
        printf "${RED}$(date): $name по IP-$ip недоступен${NC}\n" | tee -a "$LOG_FILE" 
        return 1 
    fi 
} 

# Функция для проверки доступности порта с таймаутом 
check_port() { 
    local ip_port=$1 
    IFS=':' read -r ip port <<< "$ip_port"  # Разделяем IP и порт 

    # Проверка порта с помощью /dev/tcp с таймаутом в 5 секунд 
    if timeout 5 bash -c "echo > /dev/tcp/$ip/$port" &>/dev/null; then 
        printf "${GREEN}$(date): Порт $port на $ip доступен${NC}\n" | tee -a "$LOG_FILE" 
    else 
        printf "${RED}$(date): Порт $port на $ip недоступен или таймаут${NC}\n" | tee -a "$LOG_FILE" 
    fi 
} 

# Загружаем ассоциативный массив из файла конфигурации 
declare -A IP_ADDRESSES 

while IFS='=' read -r key value; do 
    IP_ADDRESSES["$key"]="$value" 
done < "$CONFIG_FILE" 

# Проверка IP и портов для каждого IP 
for name in "${!IP_ADDRESSES[@]}"; do 
    ip_port=${IP_ADDRESSES[$name]} 
    IFS=':' read -r ip port <<< "$ip_port"  # Извлекаем IP и порт для проверки 

    echo "Проверка $name ($ip_port)"

    # Проверяем доступность IP 
    check_ip "$ip" "$name" 

    # Если порт равен 'ANY', пропускаем проверку порта 
    if [[ "$port" == "ANY" ]]; then 
        echo "Порт для $ip установлен как 'ANY'. Пропускаем проверку порта." | tee -a "$LOG_FILE" 
    else 
        # Проверяем доступность порта 
        check_port "$ip_port" 
    fi 
done