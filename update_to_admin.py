#!/usr/bin/env python3
"""
Скрипт для обновления профиля lgchernukha@gmail.com до админа
"""

import os
import sys
from supabase import create_client, Client

def update_to_admin():
    """Обновляет профиль до админа с бесконечными кредитами"""
    
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
        
        # Обновляем профиль до админа
        print("🔧 Обновление профиля до админа...")
        
        update_data = {
            "role": "admin",
            "credits": 999999,
            "subscription_plan": "free"
        }
        
        profile_response = supabase.table('profiles').update(update_data).eq('id', user_id).execute()
        
        if profile_response.data:
            print("✅ Профиль обновлен до админа")
            print(f"📧 Email: {email}")
            print(f"🔑 Пароль: 200815462Cv!")
            print(f"💳 Кредиты: 999,999 (бесконечные)")
            print(f"👑 Роль: admin")
            return True
        else:
            print("❌ Ошибка обновления профиля")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Обновление профиля lgchernukha@gmail.com до админа")
    print("=" * 60)
    
    if update_to_admin():
        print("\n🎉 Профиль успешно обновлен до админа!")
        print("📧 Email: lgchernukha@gmail.com")
        print("🔑 Пароль: 200815462Cv!")
        print("💳 Кредиты: 999,999 (бесконечные)")
        print("👑 Роль: admin")
    else:
        print("\n❌ Не удалось обновить профиль")
        sys.exit(1)
