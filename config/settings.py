# improved_config.py
"""Улучшенная конфигурация с адаптивными настройками"""

# API ключи (лучше использовать переменные окружения)
GOOGLE_API_KEY = "AIzaSyCxaE6KtU2iYuBhxyjeyZLANWj5apDc6PM"
GOOGLE_API_KEY2 = "AIzaSyAhDmoZAa_RVmP1SfC8Yg04ymM2XcuH5lM"

# Адаптивные настройки производительности
import os
import psutil

def get_optimal_concurrency():
    """Определяет оптимальное количество параллельных процессов"""
    cpu_count = psutil.cpu_count()
    memory_gb = psutil.virtual_memory().total / (1024**3)
    
    # Увеличиваем concurrency для ускорения в 3 раза
    if memory_gb < 8:  # Слабая система
        return min(15, cpu_count * 2)
    elif memory_gb < 16:  # Средняя система
        return min(25, cpu_count * 3)
    else:  # Мощная система
        return min(35, cpu_count * 4)

# Настройки производительности (ускорение)
MAX_CONCURRENT = get_optimal_concurrency()
BATCH_SIZE_FOR_RESTART = 100  # Увеличиваем батчи
API_REQUESTS_PER_MINUTE = 40  # Лимит для Gemini API

# Настройки качества (снижены для лучшего извлечения)
MIN_CONTENT_LENGTH = 30  # Снижен с 50 до 30
MAX_CONTENT_LENGTH = 6000
MIN_CONFIDENCE_SCORE = 30  # Снижен с 40 до 30

# Настройки повторных попыток
MAX_RETRIES = 3
RETRY_DELAY_BASE = 2  # Секунды для экспоненциальной задержки
REQUEST_TIMEOUT = 30  # Секунды

# Профиль поиска/классификации (может быть переопределён через CLI):
# Допустимые значения: 'software', 'iso', 'telemedicine', 'pharma', 'edtech'
PROFILE = os.environ.get("PROFILE", "software").strip().lower()
SESSION = os.environ.get("SESSION", "session 1").strip().lower()

# Файлы (профиль-специфичные имена для безопасных параллельных запусков)
INPUT_FILE = "web.csv"
RESULTS_DIR = os.path.join("results", f"result {SESSION}")
LOGS_DIR = os.path.join("logs", f"result {SESSION}")

LOG_FILE = os.path.join(LOGS_DIR, f"processing_{PROFILE}.log")
DETAILED_LOG_FILE = os.path.join(LOGS_DIR, f"detailed_processing_{PROFILE}.log")
PASS_1_OUTPUT_FILE = os.path.join(RESULTS_DIR, f"results_extraction_{PROFILE}.csv")
PASS_2_OUTPUT_FILE = os.path.join(RESULTS_DIR, f"results_final_clean_{PROFILE}.csv")
QUALITY_REPORT_FILE = os.path.join(RESULTS_DIR, f"quality_report_{PROFILE}.csv")

# Настройки валидации (снижены для лучшего извлечения)
VALIDATION_SETTINGS = {
    'min_description_length': 10,  # Снижен с 20 до 10
    'max_description_length': 500,
    'required_fields': ['company_description', 'fintech_services', 'company_type_in_payments', 'target_audience'],
    'min_services_count': 0,  # Может быть 0 для non-fintech компаний
    'enable_strict_validation': False  # Отключена строгая валидация
}

# Настройки веб-скрапинга (ускорение)
SCRAPING_SETTINGS = {
    'page_timeout': 15000,  # уменьшено с 30s до 15s
    'wait_timeout': 5000,   # уменьшено с 10s до 5s
    'scroll_delay': 1,      # уменьшено с 2s до 1s
    'content_wait_delay': 0.5, # уменьшено с 1s до 0.5s
    'enable_smart_waiting': False,  # отключаем для скорости
    'enable_content_validation': False  # отключаем для скорости
}

# Настройки классификации
CLASSIFICATION_SETTINGS = {
    'confidence_threshold': 0.5,
    'enable_multi_stage': True,
    'enable_cross_validation': True,
    'max_classification_attempts': 3
}
