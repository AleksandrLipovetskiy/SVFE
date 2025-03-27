#!/usr/bin/env python3

import os
import sys
import glob
import gzip
import re
from datetime import datetime
import chardet
import multiprocessing
import argparse
from functools import partial

def detect_encoding(raw_data):
    """Определяет кодировку данных"""
    result = chardet.detect(raw_data[:10000])  # Анализируем первые 10000 байт
    return result['encoding'] if result['confidence'] > 0.7 else 'latin-1'  # Возвращаем latin-1 как запасной вариант

def process_file(file_path, search_values, use_regex=False):
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
                    # Используем regex или точное вхождение в зависимости от флага
                    if use_regex:
                        return [line.strip() for line in f if any(re.search(value, line) for value in search_values)]
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

def search_and_move_strings(directory_pattern, search_values, unique=False, use_regex=False):
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
        process_partial = partial(process_file, search_values=search_values, use_regex=use_regex)
        found_lines = pool.map(process_partial, files_to_search)
    
    # Объединяем результаты из всех файлов
    found_lines = [line for sublist in found_lines for line in sublist if sublist]
    # Удаляем дубликаты, если указана опция unique
    if unique:
        found_lines = list(dict.fromkeys(found_lines))  # Сохраняем порядок
    
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

def get_search_values(args):
    """Получает массив значений из аргументов или файла"""
    if len(args) == 1 and os.path.isfile(args[0]):
        # Если передан один аргумент и это файл, читаем значения из него
        for encoding in {'utf-8', 'cp1251', 'latin-1', 'koi8-r'}:
            try:
                with open(args[0], 'r', encoding=encoding) as f:
                    return [line.strip() for line in f if line.strip()]
            except (UnicodeDecodeError, Exception):
                continue
        print(f"Не удалось прочитать файл {args[0]}")
        sys.exit(1)
    # Иначе считаем все аргументы значениями для поиска
    return [value.strip() for value in args if value.strip()]

def main():
    """Основная функция обработки аргументов и запуска поиска"""
    parser = argparse.ArgumentParser(description="Поиск строк в архивах по заданным значениям")
    parser.add_argument("-p", "--pattern", required=True, help="Маска для файлов (например, '/path/*.gz')")
    parser.add_argument("-f", "--file", help="Путь к файлу со значениями для поиска")
    parser.add_argument("-v", "--values", nargs="*", default=[], help="Значения для поиска (через пробел)")
    parser.add_argument("--unique", action="store_true", help="Удалять дублирующиеся строки в результате")
    parser.add_argument("--regex", action="store_true", help="Использовать регулярные выражения для поиска")
    
    args = parser.parse_args()

    # Проверяем, что указан либо файл, либо значения
    if not args.file and not args.values:
        parser.error("Необходимо указать либо файл (-f), либо значения (-v)")

    # Получаем значения для поиска
    if args.file:
        search_values = get_search_values([args.file])
    else:
        search_values = get_search_values(args.values)

    if not search_values:
        print("Не указаны значения для поиска")
        sys.exit(1)
        
    search_and_move_strings(args.pattern, search_values, args.unique, args.regex)

if __name__ == "__main__":
    main()