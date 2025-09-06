# 🔧 Настройка переменных окружения в Supabase Dashboard

## 📋 **Инструкции:**

### 1. **Откройте Supabase Dashboard**
- Перейдите: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/settings/functions

### 2. **Добавьте переменные окружения**

В разделе **Environment Variables** добавьте следующие переменные:

#### **Основные переменные:**
```
PYTHON_SERVICE_URL=https://your-api-domain.com
PYTHON_SERVICE_TOKEN=your-service-token
GOOGLE_API_KEY=your-google-api-key
GOOGLE_API_KEY2=your-backup-google-api-key
```

#### **Supabase переменные:**
```
SUPABASE_URL=https://vuznvbjsimejtoppzppv.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ1em52YmpzaW1lanRvcHB6cHB2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUyNTI3NTAsImV4cCI6MjA3MDgyODc1MH0.Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ1em52YmpzaW1lanRvcHB6cHB2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTI1Mjc1MCwiZXhwIjoyMDcwODI4NzUwfQ.kpUbkTvP5Lrsk6Tw5Km3WbWXfwHkg69b1H_1YMyAdIM
JWT_SECRET=your-super-secret-jwt-key-12345
```

### 3. **Получение ключей:**

#### **Supabase ключи:**
- **URL**: https://vuznvbjsimejtoppzppv.supabase.co
- **Anon Key**: Получите в https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/settings/api
- **Service Role Key**: Уже есть у вас

#### **Google API ключи:**
- Откройте: https://console.cloud.google.com/apis/credentials
- Создайте API ключи для Gemini API
- Добавьте в переменные GOOGLE_API_KEY и GOOGLE_API_KEY2

#### **Python Service:**
- После деплоя Python API сервиса
- Добавьте URL в PYTHON_SERVICE_URL
- Создайте токен для PYTHON_SERVICE_TOKEN

### 4. **Пример настройки:**

```bash
# В Supabase Dashboard > Settings > Edge Functions
PYTHON_SERVICE_URL=https://ai-researcher-api.railway.app
PYTHON_SERVICE_TOKEN=sk-1234567890abcdef
GOOGLE_API_KEY=AIzaSyB1234567890abcdef
GOOGLE_API_KEY2=AIzaSyB0987654321fedcba
SUPABASE_URL=https://vuznvbjsimejtoppzppv.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
JWT_SECRET=your-super-secret-jwt-key-12345
```

## 🔗 **Полезные ссылки:**

- **Edge Functions Settings**: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/settings/functions
- **API Settings**: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/settings/api
- **Google Cloud Console**: https://console.cloud.google.com/apis/credentials

## ✅ **После настройки:**

1. Все Edge Functions будут иметь доступ к переменным
2. Python API сможет подключаться к Supabase
3. Система будет готова к работе

**Настройте переменные в Dashboard!** 🔧
