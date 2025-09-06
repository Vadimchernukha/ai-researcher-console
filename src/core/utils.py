# utils.py
import logging
import csv
import io
import os
import aiofiles
import re

def setup_logging(log_file):
    logging.basicConfig(filename=log_file, level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s",
                        filemode='w')

def get_processed_domains(output_file):
    if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
        return set()
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            return {row[0].strip().lower() for row in reader if row}
    except (StopIteration, FileNotFoundError, IndexError):
        return set()

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def format_csv_row(row):
    output = io.StringIO()
    writer = csv.writer(output, lineterminator='')
    writer.writerow(row)
    return output.getvalue()

async def append_row_to_csv(row, file_path, lock):
    row_str = format_csv_row(row) + "\n"
    async with lock:
        async with aiofiles.open(file_path, 'a', encoding='utf-8', newline='') as f:
            await f.write(row_str)