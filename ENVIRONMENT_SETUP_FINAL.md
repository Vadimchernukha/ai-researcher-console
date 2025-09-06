# 🔧 Настройка переменных окружения - Финальные инструкции

## ✅ **Готовые переменные окружения:**

### **Скопируйте эти переменные в Supabase Dashboard:**

```
PYTHON_SERVICE_URL=https://your-api-domain.com
PYTHON_SERVICE_TOKEN=your-service-token
GOOGLE_API_KEY=your-google-api-key
GOOGLE_API_KEY2=your-backup-google-api-key
SUPABASE_URL=https://vuznvbjsimejtoppzppv.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ1em52YmpzaW1lanRvcHB6cHB2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUyNTI3NTAsImV4cCI6MjA3MDgyODc1MH0.P8MDGDQIGoHObgRBFdeFWvbVjsShqOGcGhKEMRa-8B4
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ1em52YmpzaW1lanRvcHB6cHB2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTI1Mjc1MCwiZXhwIjoyMDcwODI4NzUwfQ.kpUbkTvP5Lrsk6Tw5Km3WbWXfwHkg69b1H_1YMyAdIM
JWT_SECRET=ai-researcher-jwt-secret-2024
```

## 🚀 **Быстрая настройка:**

### **Запустите скрипт:**
```bash
./setup_env_with_keys.sh
```

Этот скрипт поможет вам:
- ✅ Настроить Google API ключи
- ✅ Подготовить Python Service URL
- ✅ Создать файл с переменными

## 📋 **Ручная настройка:**

### 1. **Откройте Supabase Dashboard**
- Перейдите: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/settings/functions

### 2. **Добавьте переменные окружения**
- В разделе **Environment Variables**
- Скопируйте переменные выше

### 3. **Настройте Google API ключи**
- Откройте: https://console.cloud.google.com/apis/credentials
- Создайте API ключи для Gemini API
- Замените `your-google-api-key` и `your-backup-google-api-key`

### 4. **Настройте Python Service**
- После деплоя Python API сервиса
- Замените `https://your-api-domain.com` на реальный URL
- Замените `your-service-token` на реальный токен

## ✅ **Готовые переменные:**

- ✅ **SUPABASE_URL**: https://vuznvbjsimejtoppzppv.supabase.co
- ✅ **SUPABASE_ANON_KEY**: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ1em52YmpzaW1lanRvcHB6cHB2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUyNTI3NTAsImV4cCI6MjA3MDgyODc1MH0.P8MDGDQIGoHObgRBFdeFWvbVjsShqOGcGhKEMRa-8B4
- ✅ **SUPABASE_SERVICE_ROLE_KEY**: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ1em52YmpzaW1lanRvcHB6cHB2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTI1Mjc1MCwiZXhwIjoyMDcwODI4NzUwfQ.kpUbkTvP5Lrsk6Tw5Km3WbWXfwHkg69b1H_1YMyAdIM
- ✅ **JWT_SECRET**: ai-researcher-jwt-secret-2024

## 🔗 **Полезные ссылки:**

- **Edge Functions Settings**: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/settings/functions
- **Google Cloud Console**: https://console.cloud.google.com/apis/credentials

## 🎯 **Готово!**

Переменные окружения готовы к настройке в Supabase Dashboard! 🎉

**Скопируйте переменные выше в Dashboard!** 🔧
