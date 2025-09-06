# Переменные окружения для Edge Functions

## Настройка в Supabase Dashboard

1. Откройте: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/settings/functions
2. Добавьте следующие переменные:

### Основные переменные:
```
PYTHON_SERVICE_URL=https://your-api-domain.com
PYTHON_SERVICE_TOKEN=your-service-token
GOOGLE_API_KEY=your-google-api-key
GOOGLE_API_KEY2=your-backup-google-api-key
```

### Дополнительные переменные:
```
SUPABASE_URL=https://vuznvbjsimejtoppzppv.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
JWT_SECRET=your-jwt-secret
```

## Получение ключей:

### 1. Supabase ключи:
- Откройте: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/settings/api
- Скопируйте:
  - `URL`: https://vuznvbjsimejtoppzppv.supabase.co
  - `anon public`: ваш anon key
  - `service_role`: ваш service role key

### 2. Google API ключи:
- Откройте: https://console.cloud.google.com/apis/credentials
- Создайте API ключи для Gemini API
- Добавьте в переменные GOOGLE_API_KEY и GOOGLE_API_KEY2

### 3. Python Service:
- После деплоя Python API сервиса
- Добавьте URL в PYTHON_SERVICE_URL
- Создайте токен для PYTHON_SERVICE_TOKEN

## Пример настройки:

```bash
# В Supabase Dashboard > Settings > Edge Functions
PYTHON_SERVICE_URL=https://ai-researcher-api.railway.app
PYTHON_SERVICE_TOKEN=sk-1234567890abcdef
GOOGLE_API_KEY=AIzaSyB1234567890abcdef
GOOGLE_API_KEY2=AIzaSyB0987654321fedcba
SUPABASE_URL=https://vuznvbjsimejtoppzppv.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
JWT_SECRET=your-super-secret-jwt-key
```
