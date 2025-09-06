# enhanced_main.py
"""
Улучшенная главная программа с многоэтапным пайплайном и мониторингом качества
"""

import asyncio
import csv
import logging
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
from tqdm import tqdm
import nest_asyncio
import aiofiles
import time

from src.pipelines.classification_pipeline import EnhancedPipeline
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config.settings as config
import src.core.enhanced_utils as utils

nest_asyncio.apply()

class EnhancedProcessor:
    """Улучшенный процессор с расширенной функциональностью"""
    
    def __init__(self, profile: str | None = None):
        # Берём профиль из аргумента, затем из ENV, затем из конфига
        effective_profile = profile or os.environ.get("PROFILE") or getattr(config, "PROFILE", "software")
        self.pipeline = EnhancedPipeline(profile=effective_profile)
        self.processed_domains = set()
        self.setup_logging()
        
    def setup_logging(self):
        """Настройка расширенного логирования (консоль — тихая)"""
        # Создаем каталоги для логов и результатов
        try:
            os.makedirs(os.path.dirname(config.LOG_FILE), exist_ok=True)
            os.makedirs(os.path.dirname(config.DETAILED_LOG_FILE), exist_ok=True)
            os.makedirs(os.path.dirname(config.PASS_2_OUTPUT_FILE), exist_ok=True)
        except Exception:
            pass

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)  # Показываем в терминале только ошибки
        file_handler_main = logging.FileHandler(config.LOG_FILE, mode='w', encoding='utf-8')
        file_handler_detail = logging.FileHandler(config.DETAILED_LOG_FILE, mode='w', encoding='utf-8')

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[file_handler_main, file_handler_detail, console_handler]
        )
    
    async def run_enhanced_processing(self, profile: str, input_file: str = "web.csv", progress_callback=None, fail_fast: bool = False):
        """Запуск улучшенной обработки"""
        
        # Подготовка файлов
        self._prepare_output_files()
        
        # Загрузка URL для обработки
        urls_to_process = self._load_urls_to_process(input_file)
        
        if not urls_to_process:
            print("✅ Все сайты уже обработаны или список пуст")
            return
        
        total_count = len(urls_to_process)
        start_dt = datetime.now()
        print(f"🚀 Обработка {total_count} сайтов | Старт: {start_dt.strftime('%H:%M:%S')}")

        write_lock = asyncio.Lock()
        pbar = tqdm(total=total_count, desc="Progress", unit="site", dynamic_ncols=True, leave=True, bar_format="{l_bar}{bar} {n_fmt}/{total_fmt}")

        total_processed = 0
        
        # Обработка батчами для стабильности
        successful_results = []
        
        for i in range(0, len(urls_to_process), config.BATCH_SIZE_FOR_RESTART):
            batch_urls = urls_to_process[i:i + config.BATCH_SIZE_FOR_RESTART]
            
            batch_results = await self._process_batch(batch_urls, write_lock, pbar, profile, fail_fast)
            successful_results.extend(batch_results)
            
            total_processed += len(batch_urls)
            # Статичный прогресс-бар без постфиксов
            if progress_callback:
                progress_callback(total_processed, len(urls_to_process))
            
            # Убираем паузы для ускорения
        
        pbar.close()
        
        # Генерируем отчет без вывода в консоль
        self.pipeline.generate_quality_report()
        
        finish_dt = datetime.now()
        print(f"\n✅ Готово за {(finish_dt - start_dt)} | Найдено: {len(successful_results)} | Результаты: {config.PASS_2_OUTPUT_FILE}")
    
    async def _process_batch(self, batch_urls: list, write_lock: asyncio.Lock, pbar: tqdm, profile: str, fail_fast: bool) -> list:
        """Обработка батча URL"""
        
        successful_results = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--disable-dev-shm-usage', '--no-sandbox']
            )
            
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            
            semaphore = asyncio.Semaphore(config.MAX_CONCURRENT)
            
            async def process_single_website(url):
                async with semaphore:
                    try:
                        # Глобальный timeout на весь сайт - 45s max
                        async with asyncio.timeout(45):
                            # Нормализация URL
                            if not url.startswith("http"):
                                url = f"https://{url}"
                                
                            # Комплексная обработка через новый пайплайн (без консольного вывода)
                            result = await self.pipeline.process_website_comprehensive(context, url)
                        
                        if result:
                            # Сохранение результата
                            await self._save_result(result, write_lock)
                            successful_results.append(result)
                            
                    except asyncio.TimeoutError:
                        logging.warning(f"Timeout 45s для {url}, пропускаем")
                    except Exception as e:
                        logging.error(f"Ошибка обработки {url}: {e}")
                        if fail_fast:
                            raise
                    finally:
                        pbar.update(1)
            
            # Запуск обработки
            tasks = [process_single_website(url) for url in batch_urls]
            if fail_fast:
                # Прерываем на первой ошибке
                for t in tasks:
                    try:
                        await t
                    except Exception:
                        await browser.close()
                        raise
            else:
                await asyncio.gather(*tasks)
            
            await browser.close()
        
        return successful_results
    
    async def _save_result(self, result: dict, write_lock: asyncio.Lock):
        """Сохранение результата в файл"""
        
        # Пишем краткий комментарий ценности (reasoning) рядом с меткой
        row = [result["domain"], result["classification"], result.get("comment", "")] 
        
        async with write_lock:
            async with aiofiles.open(config.PASS_2_OUTPUT_FILE, 'a', encoding='utf-8', newline='') as f:
                row_str = utils.format_csv_row(row) + "\n"
                await f.write(row_str)
    
    def _prepare_output_files(self):
        """Подготовка выходных файлов"""
        
        # Гарантируем наличие каталога результатов
        os.makedirs(os.path.dirname(config.PASS_2_OUTPUT_FILE), exist_ok=True)
        # Основной файл результатов
        with open(config.PASS_2_OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Domain", "Classification", "Comment"])
        
        # Загрузка уже обработанных доменов
        self.processed_domains = utils.get_processed_domains(config.PASS_2_OUTPUT_FILE)
    
    def _load_urls_to_process(self, input_file: str = None) -> list:
        """Загрузка URL для обработки"""
        
        file_to_use = input_file or config.INPUT_FILE
        try:
            with open(file_to_use, 'r', encoding='utf-8') as f:
                urls = [row[0].strip() for row in csv.reader(f) if row and row[0].strip()]
                
                # Фильтрация уже обработанных
                domain_to_url = {}
                for url in urls:
                    domain = url.replace("https://", "").replace("http://", "").split('/')[0].lower()
                    if domain not in self.processed_domains:
                        domain_to_url[domain] = url
                
                return list(domain_to_url.values())
                
        except FileNotFoundError:
            logging.error(f"Файл {config.INPUT_FILE} не найден")
            return []
    
    def _print_batch_stats(self, results: list, batch_size: int):
        """Вывод статистики по батчу"""
        
        success_rate = (len(results) / batch_size) * 100 if batch_size > 0 else 0
        print(f"   ✅ Успешно: {len(results)}/{batch_size} ({success_rate:.1f}%)")
        
        if results:
            avg_confidence = sum(r["confidence"] for r in results) / len(results)
            avg_time = sum(r["processing_time"] for r in results) / len(results)
            print(f"   📊 Средняя уверенность: {avg_confidence:.1f}%, время: {avg_time:.1f}с")
    
    def _print_final_stats(self, results: list, total_processed: int):
        """Вывод финальной статистики"""
        
        print(f"\n📈 ФИНАЛЬНАЯ СТАТИСТИКА:")
        print(f"   🎯 Всего обработано: {total_processed}")
        print(f"   ✅ Успешных классификаций: {len(results)}")
        print(f"   📊 Общий процент успеха: {(len(results)/total_processed)*100:.1f}%")
        
        if results:
            avg_confidence = sum(r["confidence"] for r in results) / len(results)
            avg_time = sum(r["processing_time"] for r in results) / len(results)
            total_time = sum(r["processing_time"] for r in results)
            
            print(f"   🎯 Средняя уверенность: {avg_confidence:.1f}%")
            print(f"   ⏱️  Среднее время на сайт: {avg_time:.1f}с")
            print(f"   ⏱️  Общее время обработки: {total_time:.1f}с")

async def main(profile: str | None = None, input_file: str = None, fail_fast: bool = False):
    """Главная функция"""
    
    print("="*60)
    print("🎯 УЛУЧШЕННАЯ СИСТЕМА КЛАССИФИКАЦИИ САЙТОВ")
    print("="*60)
    
    processor = EnhancedProcessor(profile=profile)
    
    try:
        await processor.run_enhanced_processing(profile or "software", input_file, fail_fast=fail_fast)
    except KeyboardInterrupt:
        print("\n⚠️  Программа прервана пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        logging.exception("Critical error in main")

if __name__ == "__main__":
    asyncio.run(main())
