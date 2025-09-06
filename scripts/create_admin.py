#!/usr/bin/env python3
"""
Скрипт для создания админ пользователя в Supabase
"""

import os
import sys
import requests
import json
from supabase import create_client, Client

def create_admin_user():
    """Создает админ пользователя в Supabase"""
    
    # Получаем переменные окружения
    supabase_url = os.getenv('SUPABASE_URL', 'https://vuznvbjsimejtoppzppv.supabase.co')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_key:
        print("❌ Ошибка: SUPABASE_SERVICE_ROLE_KEY не установлен")
        print("Получите ключ в: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/settings/api")
        return False
    
    try:
        # Создаем клиент Supabase
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Данные админа
        admin_email = "admin@example.com"
        admin_password = "admin123"
        admin_name = "Admin User"
        
        print(f"🔐 Создание админ пользователя: {admin_email}")
        
        # Создаем пользователя через Supabase Auth
        auth_response = supabase.auth.admin.create_user({
            "email": admin_email,
            "password": admin_password,
            "email_confirm": True,
            "user_metadata": {
                "full_name": admin_name
            }
        })
        
        if auth_response.user:
            user_id = auth_response.user.id
            print(f"✅ Пользователь создан с ID: {user_id}")
            
            # Создаем профиль админа
            profile_data = {
                "id": user_id,
                "email": admin_email,
                "full_name": admin_name,
                "role": "admin",
                "credits": 999999,
                "subscription_plan": "free"
            }
            
            # Вставляем профиль
            profile_response = supabase.table('profiles').insert(profile_data).execute()
            
            if profile_response.data:
                print("✅ Профиль админа создан")
                print(f"📧 Email: {admin_email}")
                print(f"🔑 Пароль: {admin_password}")
                print(f"💳 Кредиты: 999,999")
                print(f"👑 Роль: admin")
                return True
            else:
                print("❌ Ошибка создания профиля")
                return False
        else:
            print("❌ Ошибка создания пользователя")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def check_admin_exists():
    """Проверяет, существует ли админ пользователь"""
    
    supabase_url = os.getenv('SUPABASE_URL', 'https://vuznvbjsimejtoppzppv.supabase.co')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_key:
        return False
    
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Проверяем существование админа
        response = supabase.table('profiles').select('*').eq('email', 'admin@example.com').execute()
        
        if response.data:
            admin = response.data[0]
            print(f"✅ Админ уже существует:")
            print(f"📧 Email: {admin['email']}")
            print(f"👑 Роль: {admin['role']}")
            print(f"💳 Кредиты: {admin['credits']}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Создание админ пользователя для AI Researcher Console")
    print("=" * 60)
    
    # Проверяем, существует ли админ
    if check_admin_exists():
        print("\n✅ Админ пользователь уже существует!")
        sys.exit(0)
    
    # Создаем админа
    if create_admin_user():
        print("\n🎉 Админ пользователь успешно создан!")
        print("\n📋 Следующие шаги:")
        print("1. Настройте переменные окружения в Supabase Dashboard")
        print("2. Задеплойте Python API сервис")
        print("3. Мигрируйте промпты: python scripts/migrate_prompts.py")
    else:
        print("\n❌ Не удалось создать админ пользователя")
        sys.exit(1)
