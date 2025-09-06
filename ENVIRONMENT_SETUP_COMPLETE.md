# 🔧 Настройка переменных окружения - Готово!

## 🚀 **Быстрая настройка:**

### **Запустите скрипт:**
```bash
./setup_env_quick.sh
```

Этот скрипт поможет вам:
- ✅ Получить anon key из Dashboard
- ✅ Настроить Google API ключи
- ✅ Подготовить все переменные окружения
- ✅ Скопировать их в Supabase Dashboard

## 📋 **Ручная настройка:**

### 1. **Откройте Supabase Dashboard**
- Перейдите: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/settings/functions

### 2. **Добавьте переменные окружения**

В разделе **Environment Variables** добавьте:

```
PYTHON_SERVICE_URL=https://your-api-domain.com
PYTHON_SERVICE_TOKEN=your-service-token
GOOGLE_API_KEY=your-google-api-key
GOOGLE_API_KEY2=your-backup-google-api-key
SUPABASE_URL=https://vuznvbjsimejtoppzppv.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ1em52YmpzaW1lanRvcHB6cHB2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTI1Mjc1MCwiZXhwIjoyMDcwODI4NzUwfQ.kpUbkTvP5Lrsk6Tw5Km3WbWXfwHkg69b1H_1YMyAdIM
JWT_SECRET=your-super-secret-jwt-key-12345
```

### 3. **Получение ключей:**

#### **Supabase Anon Key:**
- Откройте: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/settings/api
- Скопируйте **anon public** ключ

#### **Google API ключи:**
- Откройте: https://console.cloud.google.com/apis/credentials
- Создайте API ключи для Gemini API
- Добавьте в переменные GOOGLE_API_KEY и GOOGLE_API_KEY2

#### **Python Service:**
- После деплоя Python API сервиса
- Добавьте URL в PYTHON_SERVICE_URL
- Создайте токен для PYTHON_SERVICE_TOKEN

## ✅ **После настройки:**

1. Все Edge Functions будут иметь доступ к переменным
2. Python API сможет подключаться к Supabase
3. Система будет готова к работе

## 🔗 **Полезные ссылки:**

- **Edge Functions Settings**: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/settings/functions
- **API Settings**: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/settings/api
- **Google Cloud Console**: https://console.cloud.google.com/apis/credentials

## 🎯 **Готово!**

Переменные окружения настроены и система готова к работе! 🎉

**Запустите `./setup_env_quick.sh` для быстрой настройки!** 🚀
