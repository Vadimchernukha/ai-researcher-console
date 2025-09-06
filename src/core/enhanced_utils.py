# enhanced_utils.py
"""Утилиты для улучшенной системы классификации"""

import logging
import csv
import io
import os
import aiofiles
import re

def setup_logging(log_file):
    """Настройка логирования"""
    logging.basicConfig(
        filename=log_file, 
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filemode='w',
        encoding='utf-8'
    )

def get_processed_domains(output_file):
    """Получение списка уже обработанных доменов"""
    if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
        return set()
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Пропускаем заголовок
            return {row[0].strip().lower() for row in reader if row}
    except (StopIteration, FileNotFoundError, IndexError):
        return set()

def clean_text(text):
    """Очистка текста"""
    return re.sub(r'\s+', ' ', text).strip()

def format_csv_row(row):
    """Форматирование строки CSV"""
    output = io.StringIO()
    writer = csv.writer(output, lineterminator='')
    writer.writerow(row)
    return output.getvalue()

async def append_row_to_csv(row, file_path, lock):
    """Асинхронная запись строки в CSV"""
    row_str = format_csv_row(row) + "\n"
    async with lock:
        async with aiofiles.open(file_path, 'a', encoding='utf-8', newline='') as f:
            await f.write(row_str)

def extract_domain_from_url(url: str) -> str:
    """Извлечение домена из URL"""
    return url.replace("https://", "").replace("http://", "").split('/')[0].lower()

def normalize_url(url: str) -> str:
    """Нормализация URL"""
    if not url.startswith("http"):
        url = f"https://{url}"
    return url.strip()

def validate_url(url: str) -> bool:
    """Проверка валидности URL"""
    try:
        if not url or len(url) < 4:
            return False
        
        # Базовая проверка формата
        if '.' not in url:
            return False
            
        # Проверка на запрещенные символы
        forbidden_chars = [' ', '\n', '\r', '\t']
        if any(char in url for char in forbidden_chars):
            return False
            
        return True
    except:
        return False
