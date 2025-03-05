#!/usr/bin/env python3

import re
import sys
from datetime import datetime

def parse_log_file(file_path):
    try:
        # Формируем имя выходного файла с датой
        current_date = datetime.now().strftime("%Y-%m-%d")
        output_file = f"pars_{current_date}.log"
        
        with open(file_path, 'r') as file:
            content = file.read()
            messages = content.split('cut here')
            
            # Открываем файл для записи результатов
            with open(output_file, 'w') as out_file:
                for message in messages:
                    # Ищем в любом месте строки
                    reg_utrnno_match = re.search(r'Reg_utrnno\s*(\d+)', message)
                    utrnno_match = re.search(r'utrnno:\s*(\d+)', message)
                    
                    num1 = reg_utrnno_match.group(1) if reg_utrnno_match else 'None'
                    num2 = utrnno_match.group(1) if utrnno_match else 'None'
                    
                    # Записываем в файл вместо вывода в консоль
                    out_file.write(f"'{num1}', '{num2}'\n")
                
        print(f"Результаты записаны в {output_file}")
                
    except FileNotFoundError:
        print(f"Ошибка: Файл {file_path} не найден")
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: ./script.py <путь_к_файлу>")
        sys.exit(1)
    
    log_file_path = sys.argv[1]
    parse_log_file(log_file_path)