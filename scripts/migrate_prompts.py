#!/usr/bin/env python3
"""
Скрипт для миграции существующих промптов в базу данных
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Добавляем путь к исходному коду
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import httpx
from src.analyzers import extraction_prompts, prompts as classification_prompts

# Конфигурация
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "your-anon-key")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "your-admin-password")

# Маппинг промптов
EXTRACTION_PROMPTS = {
    "software": extraction_prompts.PROMPT_SOFTWARE_PRODUCT,
    "iso": extraction_prompts.PROMPT_EXTRACTION_ISO,
    "pharma": extraction_prompts.PROMPT_DATA_EXTRACTION_PHARMA,
    "telemedicine": extraction_prompts.PROMPT_DATA_EXTRACTION_TELEMEDICINE,
    "edtech": extraction_prompts.PROMPT_DATA_EXTRACTION_EDTECH,
    "marketing": extraction_prompts.PROMPT_DATA_EXTRACTION_MARKETING,
    "fintech": extraction_prompts.PROMPT_DATA_EXTRACTION_FINTECH,
    "healthtech": extraction_prompts.PROMPT_DATA_EXTRACTION_HEALTHTECH,
    "elearning": extraction_prompts.PROMPT_DATA_EXTRACTION_ELEARNING,
    "software_products": extraction_prompts.PROMPT_DATA_EXTRACTION_SOFTWARE_PRODUCTS,
    "salesforce_partner": extraction_prompts.PROMPT_DATA_EXTRACTION_PARTNER_ECOSYSTEM,
    "hubspot_partner": extraction_prompts.PROMPT_DATA_EXTRACTION_PARTNER_ECOSYSTEM,
    "aws": extraction_prompts.PROMPT_DATA_EXTRACTION_PARTNER_ECOSYSTEM,
    "shopify": extraction_prompts.PROMPT_DATA_EXTRACTION_PARTNER_ECOSYSTEM,
    "ai_companies": extraction_prompts.PROMPT_DATA_EXTRACTION_AI_COMPANIES,
    "mobile_app": extraction_prompts.PROMPT_DATA_EXTRACTION_MOBILE_APP,
    "recruiting": extraction_prompts.PROMPT_DATA_EXTRACTION_RECRUITING,
    "banking": extraction_prompts.PROMPT_DATA_EXTRACTION_BANKING,
    "platforms": extraction_prompts.PROMPT_DATA_EXTRACTION_PLATFORMS,
}

CLASSIFICATION_PROMPTS = {
    "software": classification_prompts.PROMPT_SOFTWARE_CLASSIFICATION,
    "iso": classification_prompts.PROMPT_ISO_MSP_CLASSIFIER,
    "pharma": classification_prompts.PROMPT_FINAL_CLASSIFICATION_PHARMA,
    "telemedicine": classification_prompts.PROMPT_TELEMEDICINE_CLASSIFIER,
    "edtech": classification_prompts.PROMPT_CONCEPT_CLASSIFICATION_EDTECH,
    "marketing": classification_prompts.PROMPT_MARKETING_CLASSIFIER,
    "fintech": classification_prompts.PROMPT_FINTECH_CLASSIFIER,
    "healthtech": classification_prompts.PROMPT_HEALTHTECH_CLASSIFIER,
    "elearning": classification_prompts.PROMPT_ELEARNING_CLASSIFIER,
    "software_products": classification_prompts.PROMPT_SOFTWARE_PRODUCTS_CLASSIFIER,
    "salesforce_partner": classification_prompts.PROMPT_SALESFORCE_PARTNER_CLASSIFIER,
    "hubspot_partner": classification_prompts.PROMPT_HUBSPOT_PARTNER_CLASSIFIER,
    "aws": classification_prompts.PROMPT_AWS_CLASSIFIER,
    "shopify": classification_prompts.PROMPT_SHOPIFY_CLASSIFIER,
    "ai_companies": classification_prompts.PROMPT_AI_COMPANIES_CLASSIFIER,
    "mobile_app": classification_prompts.PROMPT_MOBILE_APP_CLASSIFIER,
    "recruiting": classification_prompts.PROMPT_RECRUITING_CLASSIFIER,
    "banking": classification_prompts.PROMPT_BANKING_CLASSIFIER,
    "platforms": classification_prompts.PROMPT_PLATFORMS_CLASSIFIER,
}

async def get_auth_token():
    """Получение JWT токена для админа"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Content-Type": "application/json"
            },
            json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            return data["access_token"]
        else:
            raise Exception(f"Failed to authenticate: {response.status_code}")

async def create_prompt(auth_token: str, prompt_data: dict):
    """Создание промпта в базе данных"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SUPABASE_URL}/functions/v1/manage-prompts/create",
            headers={
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            },
            json=prompt_data
        )
        
        if response.status_code == 201:
            return response.json()
        else:
            print(f"Failed to create prompt {prompt_data['name']}: {response.status_code}")
            print(response.text)
            return None

async def migrate_prompts():
    """Миграция всех промптов"""
    print("🚀 Начинаем миграцию промптов...")
    
    # Получаем токен авторизации
    try:
        auth_token = await get_auth_token()
        print("✅ Авторизация успешна")
    except Exception as e:
        print(f"❌ Ошибка авторизации: {e}")
        return
    
    # Мигрируем extraction промпты
    print("\n📝 Миграция extraction промптов...")
    for profile_type, prompt_content in EXTRACTION_PROMPTS.items():
        prompt_data = {
            "name": f"{profile_type}_extraction_v1",
            "profile_type": profile_type,
            "prompt_type": "extraction",
            "content": prompt_content,
            "variables": {"content": "{content}"},
            "is_default": True,
            "is_active": True
        }
        
        result = await create_prompt(auth_token, prompt_data)
        if result:
            print(f"✅ Создан промпт: {profile_type}_extraction_v1")
        else:
            print(f"❌ Ошибка создания промпта: {profile_type}_extraction_v1")
    
    # Мигрируем classification промпты
    print("\n🎯 Миграция classification промптов...")
    for profile_type, prompt_content in CLASSIFICATION_PROMPTS.items():
        prompt_data = {
            "name": f"{profile_type}_classification_v1",
            "profile_type": profile_type,
            "prompt_type": "classification",
            "content": prompt_content,
            "variables": {"structured_summary": "{structured_summary}"},
            "is_default": True,
            "is_active": True
        }
        
        result = await create_prompt(auth_token, prompt_data)
        if result:
            print(f"✅ Создан промпт: {profile_type}_classification_v1")
        else:
            print(f"❌ Ошибка создания промпта: {profile_type}_classification_v1")
    
    print("\n🎉 Миграция завершена!")

async def verify_migration():
    """Проверка миграции"""
    print("\n🔍 Проверка миграции...")
    
    try:
        auth_token = await get_auth_token()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{SUPABASE_URL}/functions/v1/manage-prompts",
                headers={
                    "Authorization": f"Bearer {auth_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                prompts = data.get("prompts", [])
                
                print(f"📊 Всего промптов в базе: {len(prompts)}")
                
                # Группируем по типам
                extraction_count = len([p for p in prompts if p["prompt_type"] == "extraction"])
                classification_count = len([p for p in prompts if p["prompt_type"] == "classification"])
                
                print(f"📝 Extraction промптов: {extraction_count}")
                print(f"🎯 Classification промптов: {classification_count}")
                
                # Показываем активные промпты
                active_prompts = [p for p in prompts if p["is_active"] and p["is_default"]]
                print(f"✅ Активных промптов по умолчанию: {len(active_prompts)}")
                
                # Показываем по профилям
                profiles = set(p["profile_type"] for p in prompts)
                print(f"🏷️ Профилей: {len(profiles)}")
                print(f"📋 Профили: {', '.join(sorted(profiles))}")
                
            else:
                print(f"❌ Ошибка проверки: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")

if __name__ == "__main__":
    print("🔧 Миграция промптов в Supabase")
    print("=" * 50)
    
    # Проверяем переменные окружения
    if SUPABASE_URL == "https://your-project.supabase.co":
        print("❌ Установите SUPABASE_URL в переменных окружения")
        sys.exit(1)
    
    if SUPABASE_ANON_KEY == "your-anon-key":
        print("❌ Установите SUPABASE_ANON_KEY в переменных окружения")
        sys.exit(1)
    
    # Запускаем миграцию
    asyncio.run(migrate_prompts())
    
    # Проверяем результат
    asyncio.run(verify_migration())
