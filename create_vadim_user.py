#!/usr/bin/env python3
"""
Скрипт для создания пользователя lgchernukha@gmail.com
"""

import os
import sys
from supabase import create_client, Client

def create_vadim_user():
    """Создает пользователя lgchernukha@gmail.com"""
    
    # Получаем переменные окружения
    supabase_url = 'https://vuznvbjsimejtoppzppv.supabase.co'
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_key:
        print("❌ Ошибка: SUPABASE_SERVICE_ROLE_KEY не установлен")
        print("Получите ключ в: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/settings/api")
        print("Затем выполните: export SUPABASE_SERVICE_ROLE_KEY='your-key'")
        return False
    
    try:
        # Создаем клиент Supabase
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Данные пользователя
        email = "lgchernukha@gmail.com"
        password = "200815462Cv!"
        full_name = "Vadim Chernukha"
        role = "user"
        credits = 100
        
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

if __name__ == "__main__":
    print("🚀 Создание пользователя lgchernukha@gmail.com")
    print("=" * 60)
    
    if create_vadim_user():
        print("\n🎉 Пользователь успешно создан!")
        print("📧 Email: lgchernukha@gmail.com")
        print("🔑 Пароль: 200815462Cv!")
        print("💳 Кредиты: 100")
        print("👑 Роль: user")
    else:
        print("\n❌ Не удалось создать пользователя")
        sys.exit(1)
