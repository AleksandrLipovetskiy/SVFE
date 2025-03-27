#!/usr/bin/env python3

import os
import sys
import glob
import gzip
from datetime import datetime
import chardet
import multiprocessing
from functools import partial

def detect_encoding(raw_data):
    """Определяет кодировку данных"""
    result = chardet.detect(raw_data[:10000])  # Анализируем первые 10000 байт
    return result['encoding'] if result['confidence'] > 0.7 else 'latin-1'  # Возвращаем latin-1 как запасной вариант

def process_file(file_path, search_values):
    """Обрабатывает один файл с поиском заданных значений"""
    try:
        # Читаем образец для определения кодировки
        with gzip.open(file_path, 'rb') as f:
            sample = f.read(10000)
        detected_encoding = detect_encoding(sample)
        
        # Пробуем разные кодировки для чтения файла
        for encoding in {detected_encoding, 'utf-8', 'cp1251', 'latin-1', 'koi8-r'}:
            try:
                with gzip.open(file_path, 'rt', encoding=encoding) as f:
                    # Возвращаем строки, содержащие искомые значения
                    return [line.strip() for line in f if any(value in line for value in search_values)]
            except UnicodeDecodeError:
                continue  # Пробуем следующую кодировку при ошибке декодирования
            except Exception as e:
                print(f"Ошибка при чтении архива {file_path}: {e}")
                return []
        print(f"Не удалось декодировать {file_path} ни в одной кодировке")
        return []
    except Exception as e:
        print(f"Ошибка при обработке архива {file_path}: {e}")
        return []

def search_and_move_strings(directory_pattern, search_values):
    """Ищет строки в файлах и записывает результаты в новый файл"""
    # Формируем имя выходного файла с временной меткой
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(os.getcwd(), f"search_posting_{current_time}.txt")
    
    # Получаем список файлов по заданной маске
    files_to_search = glob.glob(directory_pattern)
    if not files_to_search:
        print("Файлы по указанной маске не найдены")
        return

    # Создаем пул процессов для параллельной обработки
    with multiprocessing.Pool(processes=8) as pool:
        process_partial = partial(process_file, search_values=search_values)
        found_lines = pool.map(process_partial, files_to_search)
    
    # Объединяем результаты из всех файлов
    found_lines = [line for sublist in found_lines for line in sublist if sublist]
    
    # Записываем найденные строки в файл
    if found_lines:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(found_lines))
            print(f"Найдено {len(found_lines)} строк. Результат записан в {output_file}")
        except Exception as e:
            print(f"Ошибка при записи в файл: {e}")
    else:
        print("Совпадений не найдено")

def get_search_values(arg):
    """Получает массив значений из файла или строки аргументов"""
    if os.path.isfile(arg):
        # Читаем значения из файла с попыткой разных кодировок
        for encoding in {'utf-8', 'cp1251', 'latin-1', 'koi8-r'}:
            try:
                with open(arg, 'r', encoding=encoding) as f:
                    return [line.strip() for line in f if line.strip()]
            except (UnicodeDecodeError, Exception):
                continue
        print(f"Не удалось прочитать файл {arg}")
        sys.exit(1)
    # Разделяем строку значений по запятой
    return [value.strip() for value in arg.split(',') if value.strip()]

def main():
    """Основная функция обработки аргументов и запуска поиска"""
    if len(sys.argv) < 2:
        print("Использование: python script.py <путь_с_маской> [значения или файл]")
        print("Пример: python script.py /home/user/OPS_2025*.gz /home/user/values.txt")
        print("Пример: python script.py /home/user/OPS_2025*.gz 452179279285,452166059532")
        sys.exit(1)

    directory_pattern = sys.argv[1]
    # Объединяем все аргументы после первого в одну строку
    search_arg = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else ""
    search_values = get_search_values(search_arg) if search_arg else []
    
    if not search_values:
        print("Не указаны значения для поиска")
        sys.exit(1)
        
    search_and_move_strings(directory_pattern, search_values)

if __name__ == "__main__":
    main()