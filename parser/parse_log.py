#!/usr/bin/env python3

import re
import sys

def parse_log_file(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            messages = content.split('cut here')
            
            for message in messages:
                tuta1_match = re.search(r'tuta1\s*(\d+)', message)
                tuta2_match = re.search(r'tuta2\s*(\d+)', message)
                
                num1 = tuta1_match.group(1) if tuta1_match else 'None'
                num2 = tuta2_match.group(1) if tuta2_match else 'None'
                
                print(f"'{num1}', '{num2}'")
                
    except FileNotFoundError:
        print(f"Ошибка: Файл {file_path} не найден")
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    # Проверяем, передан ли аргумент
    if len(sys.argv) != 2:
        print("Использование: ./script.py <путь_к_файлу>")
        sys.exit(1)
    
    # Первый аргумент (sys.argv[1]) - путь к файлу
    log_file_path = sys.argv[1]
    parse_log_file(log_file_path)