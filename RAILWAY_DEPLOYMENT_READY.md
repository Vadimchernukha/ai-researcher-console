# 🚀 Деплой Python API на Railway - Готово!

## 🎯 **Рекомендация: Railway**

**Почему Railway:**
- ✅ **Простота**: Автоматически определяет Python проект
- ✅ **Быстрота**: Деплой за 2-3 минуты
- ✅ **Бесплатно**: 500 часов в месяц бесплатно
- ✅ **Автоматические обновления**: При пуше в GitHub
- ✅ **Встроенные переменные окружения**
- ✅ **Автоматический HTTPS**

## 🚀 **Для деплоя:**

### **Запустите скрипт:**
```bash
./deploy_to_railway.sh
```

### **Или следуйте инструкции:**

#### **1. Создание аккаунта Railway**
- Откройте: https://railway.app
- Нажмите "Start a New Project"
- Войдите через GitHub (рекомендуется)

#### **2. Создание проекта**
- Нажмите "Deploy from GitHub repo"
- Выберите ваш репозиторий
- **Выберите папку `api/`** (важно!)
- Railway автоматически определит Python проект

#### **3. Настройка переменных окружения**
В Railway Dashboard добавьте переменные из файла `railway_env_vars.txt`:

```
SUPABASE_URL=https://vuznvbjsimejtoppzppv.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ1em52YmpzaW1lanRvcHB6cHB2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUyNTI3NTAsImV4cCI6MjA3MDgyODc1MH0.P8MDGDQIGoHObgRBFdeFWvbVjsShqOGcGhKEMRa-8B4
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ1em52YmpzaW1lanRvcHB6cHB2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTI1Mjc1MCwiZXhwIjoyMDcwODI4NzUwfQ.kpUbkTvP5Lrsk6Tw5Km3WbWXfwHkg69b1H_1YMyAdIM
GOOGLE_API_KEY=AIzaSyCxaE6KtU2iYuBhxyjeyZLANWj5apDc6PM
GOOGLE_API_KEY2=AIzaSyAhDmoZAa_RVmP1SfC8Yg04ymM2XcuH5lM
JWT_SECRET=ai-researcher-jwt-secret-2024
```

#### **4. Деплой**
- Railway автоматически начнет деплой
- Дождитесь завершения (2-3 минуты)
- Скопируйте URL вашего API

#### **5. Обновление переменных в Supabase**
После получения URL:
- Вернитесь в Supabase Dashboard
- Обновите PYTHON_SERVICE_URL на ваш Railway URL

## 🔗 **Полезные ссылки:**

- **Railway**: https://railway.app
- **Railway Docs**: https://docs.railway.app
- **Supabase Dashboard**: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/settings/functions

## ✅ **После деплоя:**

1. **API будет доступен по URL**: `https://your-project-name.railway.app`
2. **Автоматический HTTPS**
3. **Автоматические обновления** при пуше в GitHub

## 🎯 **Готово!**

**Запустите `./deploy_to_railway.sh` для интерактивного деплоя!** 🚀
