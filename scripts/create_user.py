#!/usr/bin/env python3
"""
Скрипт для создания пользователя в Supabase
"""

import os
import sys
import requests
import json
from supabase import create_client, Client

def create_user(email, password, full_name="User", role="user", credits=100):
    """Создает пользователя в Supabase"""
    
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
        
        print(f"🔐 Создание пользователя: {email}")
        
        # Создаем пользователя через Supabase Auth
        auth_response = supabase.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True,
            "user_metadata": {
                "full_name": full_name
            }
        })
        
        if auth_response.user:
            user_id = auth_response.user.id
            print(f"✅ Пользователь создан с ID: {user_id}")
            
            # Создаем профиль пользователя
            profile_data = {
                "id": user_id,
                "email": email,
                "full_name": full_name,
                "role": role,
                "credits": credits,
                "subscription_plan": "free"
            }
            
            # Вставляем профиль
            profile_response = supabase.table('profiles').insert(profile_data).execute()
            
            if profile_response.data:
                print("✅ Профиль пользователя создан")
                print(f"📧 Email: {email}")
                print(f"🔑 Пароль: {password}")
                print(f"💳 Кредиты: {credits}")
                print(f"👑 Роль: {role}")
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

def check_user_exists(email):
    """Проверяет, существует ли пользователь"""
    
    supabase_url = os.getenv('SUPABASE_URL', 'https://vuznvbjsimejtoppzppv.supabase.co')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_key:
        return False
    
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Проверяем существование пользователя
        response = supabase.table('profiles').select('*').eq('email', email).execute()
        
        if response.data:
            user = response.data[0]
            print(f"✅ Пользователь уже существует:")
            print(f"📧 Email: {user['email']}")
            print(f"👑 Роль: {user['role']}")
            print(f"💳 Кредиты: {user['credits']}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Создание пользователя для AI Researcher Console")
    print("=" * 60)
    
    # Данные пользователя
    email = "lgchernukha@gmail.com"
    password = "200815462Cv!"
    full_name = "Vadim Chernukha"
    role = "user"
    credits = 100
    
    # Проверяем, существует ли пользователь
    if check_user_exists(email):
        print(f"\n✅ Пользователь {email} уже существует!")
        sys.exit(0)
    
    # Создаем пользователя
    if create_user(email, password, full_name, role, credits):
        print(f"\n🎉 Пользователь {email} успешно создан!")
        print(f"📧 Email: {email}")
        print(f"🔑 Пароль: {password}")
        print(f"💳 Кредиты: {credits}")
        print(f"👑 Роль: {role}")
    else:
        print(f"\n❌ Не удалось создать пользователя {email}")
        sys.exit(1)
