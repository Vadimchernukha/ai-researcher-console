# run_enhanced.py
"""
Запуск 6-этапной системы классификации
"""

import os
import sys
import argparse

# Проверяем наличие входного файла (опционально)
input_file = 'data/sample_domains.csv'
if not os.path.exists(input_file):
    print(f"⚠️  ВНИМАНИЕ: Файл {input_file} не найден!")
    print("   Создайте файл с доменами или укажите другой путь")
    print("   Пример: python scripts/run_classifier.py --profile software --input your_file.csv")
    # Не выходим, позволяем пользователю указать файл

try:
    # ВАЖНО: сначала определить профиль и положить в ENV, затем импортировать main
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import asyncio
    AVAILABLE_PROFILES = [
        "software", "iso", "telemedicine", "pharma", "edtech",
        # Промпт для клиентов - Client Profiles
        "marketing", "fintech", "healthtech", "elearning", "software_products",
        "salesforce_partner", "hubspot_partner", "aws", "shopify", 
        "ai_companies", "mobile_app", "recruiting", "banking", "platforms"
    ]

    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=AVAILABLE_PROFILES, default=None)
    parser.add_argument("--input", help="Input CSV file with domains", default="data/sample_domains.csv")
    parser.add_argument("--session", help="Logical session name (e.g., 'session 1')", default=None)
    parser.add_argument("--fail-fast", action="store_true", help="Stop processing on first critical error")
    args = parser.parse_args()

    # 1) Приоритет у флага
    selected_profile = args.profile

    # 2) Если флаг не задан — берем из env
    if not selected_profile:
        selected_profile = os.environ.get("PROFILE")

    # 3) Если нет и в env — спросим интерактивно
    if not selected_profile:
        print("\nВыберите профиль поиска/классификации:")
        for idx, name in enumerate(AVAILABLE_PROFILES, 1):
            print(f"  {idx}. {name}")
        try:
            choice = input("Введите номер (по умолчанию 1): ").strip()
            if not choice:
                selected_profile = AVAILABLE_PROFILES[0]
            else:
                choice_idx = int(choice)
                if 1 <= choice_idx <= len(AVAILABLE_PROFILES):
                    selected_profile = AVAILABLE_PROFILES[choice_idx - 1]
                else:
                    print("Неверный выбор, использую профиль по умолчанию: software")
                    selected_profile = AVAILABLE_PROFILES[0]
        except Exception:
            print("Не удалось прочитать выбор, использую профиль по умолчанию: software")
            selected_profile = AVAILABLE_PROFILES[0]

    # Прокидываем профиль/сессию вниз по пайплайну через env ДО импорта main (важно для путей файлов)
    os.environ["PROFILE"] = selected_profile
    if args.session:
        os.environ["SESSION"] = args.session
    if args.fail_fast:
        os.environ["FAIL_FAST"] = "true"
    print(f"Профиль: {selected_profile} | Сессия: {os.environ.get('SESSION','session 1')}")

    # Импортируем main после установки PROFILE
    from src.main import main

    # Запускаем главную функцию
    asyncio.run(main(profile=selected_profile, input_file=args.input, fail_fast=args.fail_fast))
    
except ImportError as e:
    print(f"❌ ОШИБКА ИМПОРТА: {e}")
    print("🔧 Убедитесь, что установлены зависимости: pip install psutil")
    
except Exception as e:
    print(f"❌ ОШИБКА: {e}")
    print("🔧 Попробуйте запустить оригинальную версию: python src/main.py")
    
    import traceback
    traceback.print_exc()
