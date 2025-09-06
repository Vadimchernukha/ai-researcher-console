#!/usr/bin/env python3
"""
Скрипт для тестирования Railway деплоя
"""

import requests
import json
import time
import sys

def test_railway_deployment(base_url="http://localhost:8000"):
    """Тестирование основных эндпоинтов API"""
    
    print(f"🧪 Тестирование API на {base_url}")
    
    tests = [
        {
            "name": "Health Check",
            "method": "GET",
            "endpoint": "/health",
            "expected_status": 200
        },
        {
            "name": "Available Profiles",
            "method": "GET", 
            "endpoint": "/profiles",
            "expected_status": 200
        }
    ]
    
    results = []
    
    for test in tests:
        try:
            print(f"\n📋 {test['name']}...")
            
            if test["method"] == "GET":
                response = requests.get(f"{base_url}{test['endpoint']}", timeout=10)
            
            if response.status_code == test["expected_status"]:
                print(f"✅ {test['name']} - OK ({response.status_code})")
                if response.headers.get('content-type', '').startswith('application/json'):
                    data = response.json()
                    print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
                results.append(True)
            else:
                print(f"❌ {test['name']} - FAILED ({response.status_code})")
                print(f"   Response: {response.text[:200]}...")
                results.append(False)
                
        except requests.RequestException as e:
            print(f"❌ {test['name']} - CONNECTION ERROR: {e}")
            results.append(False)
        except Exception as e:
            print(f"❌ {test['name']} - ERROR: {e}")
            results.append(False)
    
    # Итоги
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Результаты тестирования:")
    print(f"   ✅ Прошло: {passed}/{total}")
    print(f"   ❌ Провалено: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 Все тесты прошли успешно! API готов к работе.")
        return True
    else:
        print("\n⚠️  Есть проблемы. Проверьте логи приложения.")
        return False

def wait_for_api(base_url="http://localhost:8000", timeout=60):
    """Ожидание запуска API"""
    print(f"⏳ Ожидание запуска API на {base_url}...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ API запущен!")
                return True
        except requests.RequestException:
            pass
        
        time.sleep(2)
        print(".", end="", flush=True)
    
    print(f"\n❌ API не запустился за {timeout} секунд")
    return False

if __name__ == "__main__":
    # Проверяем аргументы командной строки
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8000"
    
    print("🚀 Railway Deployment Test")
    print("=" * 50)
    
    # Ждем запуска API
    if wait_for_api(base_url):
        # Запускаем тесты
        success = test_railway_deployment(base_url)
        sys.exit(0 if success else 1)
    else:
        print("❌ Не удалось дождаться запуска API")
        sys.exit(1)
