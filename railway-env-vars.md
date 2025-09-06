# Railway Environment Variables

Настройте эти переменные в Railway Dashboard -> Variables:

## Основные настройки
```
ENVIRONMENT=production
PORT=8000
HOST=0.0.0.0
```

## Google API ключи (обязательно замените!)
```
GOOGLE_API_KEY=your-google-api-key-here
GOOGLE_API_KEY2=your-google-api-key-2-here
```

## JWT и безопасность
```
JWT_SECRET=your-super-secret-jwt-key-here
```

## Supabase (если используется)
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-key
```

## Python настройки
```
PYTHONPATH=/app
PYTHONUNBUFFERED=1
```

## Playwright настройки
```
PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
```

## Настройки профиля по умолчанию
```
PROFILE=software
SESSION=session_1
```

## Лимиты и производительность
```
MAX_CONCURRENT=5
BATCH_SIZE=50
API_REQUESTS_PER_MINUTE=30
```

## Инструкция по настройке в Railway:

1. Зайдите в Railway Dashboard
2. Выберите ваш проект
3. Перейдите в Variables
4. Добавьте все переменные выше
5. Перезапустите деплой

**Важно:** Обязательно замените `your-google-api-key-here` на реальные API ключи!
