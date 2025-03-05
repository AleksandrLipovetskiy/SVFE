#!/usr/bin/env python3

import re
import sys
from datetime import datetime

def parse_log_file(file_path):
    encodings = ['utf-8', 'latin-1', 'windows-1251', 'cp866']
    
    try:
        # Читаем файл как бинарный
        with open(file_path, 'rb') as file:
            binary_content = file.read()
        
        # Пробуем декодировать с разными кодировками
        content = None
        for encoding in encodings:
            try:
                content = binary_content.decode(encoding)
                print(f"Успешно декодирован с использованием {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            raise UnicodeDecodeError("Не удалось декодировать файл с доступными кодировками")

        # Формируем имя выходного файла с датой
        current_date = datetime.now().strftime("%Y-%m-%d")
        output_file = f"pars_{current_date}.log"
        
        messages = content.split('cut here')
        
        with open(output_file, 'w', encoding='utf-8') as out_file:
            for message in messages:
                reg_utrnno_match = re.search(r'Reg_utrnno\s*(\d+)', message)
                utrnno_match = re.search(r'utrnno:\s*(\d+)', message)
                
                num1 = reg_utrnno_match.group(1) if reg_utrnno_match else 'None'
                num2 = utrnno_match.group(1) if utrnno_match else 'None'
                
                out_file.write(f"'{num1}', '{num2}'\n")
                
        print(f"Результаты записаны в {output_file}")
                
    except FileNotFoundError:
        print(f"Ошибка: Файл {file_path} не найден")
    except UnicodeDecodeError as e:
        print(f"Ошибка декодирования: {str(e)}")
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: ./script.py <путь_к_файлу>")
        sys.exit(1)
    
    log_file_path = sys.argv[1]
    parse_log_file(log_file_path)