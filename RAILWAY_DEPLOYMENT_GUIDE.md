# 🚀 Деплой Python API на Railway

## 📋 **Пошаговая инструкция:**

### **ШАГ 1: Подготовка проекта**

1. **Убедитесь, что у вас есть GitHub репозиторий**
2. **Проверьте, что папка `api/` содержит:**
   - `main.py` (FastAPI приложение)
   - `requirements.txt` (зависимости)
   - `Dockerfile` (опционально)

### **ШАГ 2: Создание аккаунта Railway**

1. **Откройте:** https://railway.app
2. **Нажмите "Start a New Project"**
3. **Войдите через GitHub** (рекомендуется)

### **ШАГ 3: Создание проекта**

1. **Нажмите "Deploy from GitHub repo"**
2. **Выберите ваш репозиторий**
3. **Выберите папку `api/`** (важно!)
4. **Railway автоматически определит Python проект**

### **ШАГ 4: Настройка переменных окружения**

В Railway Dashboard добавьте:

```
SUPABASE_URL=https://vuznvbjsimejtoppzppv.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ1em52YmpzaW1lanRvcHB6cHB2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUyNTI3NTAsImV4cCI6MjA3MDgyODc1MH0.P8MDGDQIGoHObgRBFdeFWvbVjsShqOGcGhKEMRa-8B4
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ1em52YmpzaW1lanRvcHB6cHB2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTI1Mjc1MCwiZXhwIjoyMDcwODI4NzUwfQ.kpUbkTvP5Lrsk6Tw5Km3WbWXfwHkg69b1H_1YMyAdIM
GOOGLE_API_KEY=AIzaSyCxaE6KtU2iYuBhxyjeyZLANWj5apDc6PM
GOOGLE_API_KEY2=AIzaSyAhDmoZAa_RVmP1SfC8Yg04ymM2XcuH5lM
JWT_SECRET=ai-researcher-jwt-secret-2024
```

### **ШАГ 5: Деплой**

1. **Railway автоматически начнет деплой**
2. **Дождитесь завершения** (2-3 минуты)
3. **Скопируйте URL** вашего API

### **ШАГ 6: Обновление переменных в Supabase**

После получения URL:
1. **Вернитесь в Supabase Dashboard**
2. **Обновите PYTHON_SERVICE_URL** на ваш Railway URL

## 🔗 **Полезные ссылки:**

- **Railway**: https://railway.app
- **Railway Docs**: https://docs.railway.app
- **Supabase Dashboard**: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/settings/functions

## ✅ **После деплоя:**

1. **API будет доступен по URL**: `https://your-project-name.railway.app`
2. **Автоматический HTTPS**
3. **Автоматические обновления** при пуше в GitHub

## 🎯 **Готово!**

**Начните с создания аккаунта на Railway!** 🚀
