# 🔍 Где найти Environment Variables в Supabase Dashboard

## 📋 **Пошаговая инструкция:**

### **ШАГ 1: Откройте Supabase Dashboard**
- Перейдите: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv

### **ШАГ 2: Найдите раздел Settings**
- В левом меню найдите иконку **⚙️ Settings** (шестеренка)
- Нажмите на неё

### **ШАГ 3: Выберите Functions**
- В меню Settings найдите **Functions**
- Нажмите на **Functions**

### **ШАГ 4: Найдите Environment Variables**
- На странице Functions найдите раздел **Environment Variables**
- Он должен быть в верхней части страницы

## 🔍 **Альтернативные способы:**

### **Способ 1: Прямая ссылка**
- Откройте: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/settings/functions

### **Способ 2: Через Edge Functions**
- В левом меню найдите **Edge Functions**
- Нажмите на **Edge Functions**
- Найдите раздел **Environment Variables**

### **Способ 3: Через API**
- В левом меню найдите **API**
- Нажмите на **API**
- Найдите раздел **Environment Variables**

## 🚨 **Если не можете найти:**

### **Возможные причины:**
1. **Права доступа** - убедитесь, что вы владелец проекта
2. **Версия Supabase** - возможно, у вас старая версия
3. **Регион** - некоторые функции могут быть недоступны в определенных регионах

### **Что делать:**
1. **Обновите страницу** (F5)
2. **Выйдите и войдите** в аккаунт
3. **Проверьте права доступа** к проекту

## 🔧 **Альтернативный способ - через CLI:**

Если не можете найти в Dashboard, используйте CLI:

```bash
# Установите переменные через CLI
npx supabase secrets set PYTHON_SERVICE_URL=https://your-api-domain.com
npx supabase secrets set PYTHON_SERVICE_TOKEN=your-service-token
npx supabase secrets set GOOGLE_API_KEY=your-google-api-key
npx supabase secrets set GOOGLE_API_KEY2=your-backup-google-api-key
npx supabase secrets set SUPABASE_URL=https://vuznvbjsimejtoppzppv.supabase.co
npx supabase secrets set SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ1em52YmpzaW1lanRvcHB6cHB2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUyNTI3NTAsImV4cCI6MjA3MDgyODc1MH0.P8MDGDQIGoHObgRBFdeFWvbVjsShqOGcGhKEMRa-8B4
npx supabase secrets set SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ1em52YmpzaW1lanRvcHB6cHB2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTI1Mjc1MCwiZXhwIjoyMDcwODI4NzUwfQ.kpUbkTvP5Lrsk6Tw5Km3WbWXfwHkg69b1H_1YMyAdIM
npx supabase secrets set JWT_SECRET=ai-researcher-jwt-secret-2024
```

## 🎯 **Попробуйте эти ссылки:**

1. **Settings > Functions**: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/settings/functions
2. **Edge Functions**: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/functions
3. **API**: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/settings/api

## 🚀 **Если ничего не помогает:**

Используйте CLI команды выше - они точно сработают!

**Попробуйте CLI команды!** 🔧
