#!/usr/bin/env python3
"""
Скрипт для создания только профиля пользователя (если пользователь уже существует в auth)
"""

import os
import sys
from supabase import create_client, Client

def create_profile_only():
    """Создает только профиль для существующего пользователя"""
    
    # Получаем переменные окружения
    supabase_url = 'https://vuznvbjsimejtoppzppv.supabase.co'
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_key:
        print("❌ Ошибка: SUPABASE_SERVICE_ROLE_KEY не установлен")
        return False
    
    try:
        # Создаем клиент Supabase
        supabase: Client = create_client(supabase_url, supabase_key)
        
        email = "lgchernukha@gmail.com"
        full_name = "Vadim Chernukha"
        role = "user"
        credits = 100
        
        print(f"🔍 Поиск пользователя: {email}")
        
        # Ищем пользователя в auth.users
        auth_users = supabase.auth.admin.list_users()
        
        user_id = None
        for user in auth_users:
            if user.email == email:
                user_id = user.id
                break
        
        if not user_id:
            print("❌ Пользователь не найден в auth.users")
            return False
        
        print(f"✅ Пользователь найден с ID: {user_id}")
        
        # Проверяем, есть ли уже профиль
        existing_profile = supabase.table('profiles').select('*').eq('id', user_id).execute()
        
        if existing_profile.data:
            print("✅ Профиль уже существует:")
            profile = existing_profile.data[0]
            print(f"📧 Email: {profile['email']}")
            print(f"👑 Роль: {profile['role']}")
            print(f"💳 Кредиты: {profile['credits']}")
            return True
        
        # Создаем профиль
        print("🔧 Создание профиля...")
        profile_data = {
            "id": user_id,
            "email": email,
            "full_name": full_name,
            "role": role,
            "credits": credits,
            "subscription_plan": "free"
        }
        
        profile_response = supabase.table('profiles').insert(profile_data).execute()
        
        if profile_response.data:
            print("✅ Профиль пользователя создан")
            print(f"📧 Email: {email}")
            print(f"🔑 Пароль: 200815462Cv!")
            print(f"💳 Кредиты: {credits}")
            print(f"👑 Роль: {role}")
            return True
        else:
            print("❌ Ошибка создания профиля")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Создание профиля для lgchernukha@gmail.com")
    print("=" * 60)
    
    if create_profile_only():
        print("\n🎉 Профиль успешно создан!")
        print("📧 Email: lgchernukha@gmail.com")
        print("🔑 Пароль: 200815462Cv!")
        print("💳 Кредиты: 100")
        print("👑 Роль: user")
    else:
        print("\n❌ Не удалось создать профиль")
        sys.exit(1)
