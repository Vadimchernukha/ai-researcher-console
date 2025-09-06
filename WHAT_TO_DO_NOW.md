# 🎯 Что делать СЕЙЧАС - Простая инструкция

## ✅ **Что уже готово:**
- Supabase проект настроен
- База данных создана
- Edge Functions задеплоены
- Админ пользователь создан: `lgchernukha@gmail.com`
- Переменные окружения подготовлены

## 🚀 **Что нужно сделать ПРЯМО СЕЙЧАС:**

### **ШАГ 1: Настроить переменные окружения**

1. **Откройте ссылку:**
   https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/settings/functions

2. **Найдите раздел "Environment Variables"**

3. **Скопируйте и вставьте эти переменные:**
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

4. **Нажмите "Save"**

### **ШАГ 2: Получить Google API ключи**

1. **Откройте:** https://console.cloud.google.com/apis/credentials
2. **Создайте новый API ключ**
3. **Включите Gemini API**
4. **Скопируйте ключ**
5. **Вернитесь в Supabase Dashboard**
6. **Замените `your-google-api-key` на ваш реальный ключ**

### **ШАГ 3: Задеплоить Python API**

**Самый простой способ - Railway:**
1. Откройте: https://railway.app
2. Создайте аккаунт
3. Создайте новый проект
4. Подключите GitHub репозиторий
5. Выберите папку `api/`
6. Railway автоматически задеплоит

### **ШАГ 4: Обновить URL в переменных**

После деплоя:
1. Скопируйте URL вашего API
2. Вернитесь в Supabase Dashboard
3. Замените `https://your-api-domain.com` на ваш реальный URL

### **ШАГ 5: Мигрировать промпты**

```bash
./next_steps.sh
```

## 🎯 **Порядок выполнения:**

1. **СНАЧАЛА:** Настройте переменные в Supabase Dashboard
2. **ПОТОМ:** Получите Google API ключи
3. **ЗАТЕМ:** Задеплойте Python API на Railway
4. **ДАЛЕЕ:** Обновите URL в переменных
5. **НАКОНЕЦ:** Запустите `./next_steps.sh`

## 🚀 **Начните с ШАГА 1!**

**Откройте Supabase Dashboard и настройте переменные окружения!** 🔧
