#!/usr/bin/env python3
"""
Скрипт для настройки переменных окружения в Supabase Edge Functions
"""

import os
import sys
import requests
import json
from supabase import create_client, Client

def setup_environment_variables():
    """Настраивает переменные окружения в Supabase"""
    
    # Получаем переменные окружения
    supabase_url = 'https://vuznvbjsimejtoppzppv.supabase.co'
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_key:
        print("❌ Ошибка: SUPABASE_SERVICE_ROLE_KEY не установлен")
        return False
    
    try:
        # Создаем клиент Supabase
        supabase: Client = create_client(supabase_url, supabase_key)
        
        print("🔧 Настройка переменных окружения...")
        
        # Получаем anon key
        print("🔐 Получите anon key из Dashboard:")
        print("📋 https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/settings/api")
        anon_key = input("Введите SUPABASE_ANON_KEY: ").strip()
        
        if not anon_key:
            print("❌ Anon key не может быть пустым")
            return False
        
        # Получаем Google API ключи
        print("\n🔑 Получите Google API ключи:")
        print("📋 https://console.cloud.google.com/apis/credentials")
        google_key1 = input("Введите GOOGLE_API_KEY: ").strip()
        google_key2 = input("Введите GOOGLE_API_KEY2 (backup): ").strip()
        
        if not google_key1:
            print("❌ Google API key не может быть пустым")
            return False
        
        # Получаем Python Service URL
        print("\n🚀 Python Service URL (после деплоя):")
        python_url = input("Введите PYTHON_SERVICE_URL: ").strip()
        if not python_url:
            python_url = "https://your-api-domain.com"
        
        # Получаем Python Service Token
        python_token = input("Введите PYTHON_SERVICE_TOKEN: ").strip()
        if not python_token:
            python_token = "your-service-token"
        
        # JWT Secret
        jwt_secret = input("Введите JWT_SECRET (или нажмите Enter для автогенерации): ").strip()
        if not jwt_secret:
            jwt_secret = "ai-researcher-jwt-secret-2024"
        
        # Создаем переменные окружения
        env_vars = {
            "PYTHON_SERVICE_URL": python_url,
            "PYTHON_SERVICE_TOKEN": python_token,
            "GOOGLE_API_KEY": google_key1,
            "GOOGLE_API_KEY2": google_key2,
            "SUPABASE_URL": supabase_url,
            "SUPABASE_ANON_KEY": anon_key,
            "SUPABASE_SERVICE_ROLE_KEY": supabase_key,
            "JWT_SECRET": jwt_secret
        }
        
        print("\n📋 Переменные окружения для настройки:")
        print("=" * 60)
        
        for key, value in env_vars.items():
            print(f"{key}={value}")
        
        print("\n🔧 Настройте эти переменные в Supabase Dashboard:")
        print("📋 https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/settings/functions")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Настройка переменных окружения для AI Researcher Console")
    print("=" * 60)
    
    if setup_environment_variables():
        print("\n✅ Переменные окружения подготовлены!")
        print("📋 Скопируйте их в Supabase Dashboard > Settings > Functions")
    else:
        print("\n❌ Не удалось подготовить переменные окружения")
        sys.exit(1)
