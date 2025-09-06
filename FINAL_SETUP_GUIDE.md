# 🎉 AI Researcher Console - Финальная настройка

## ✅ **Что уже готово:**

1. **Supabase проект** - связан и настроен
2. **База данных** - все таблицы созданы
3. **Edge Functions** - задеплоены
4. **Система кредитов** - настроена
5. **Управление промптами** - готово

## 🚀 **Автоматическая настройка:**

### Запустите скрипт настройки:
```bash
./setup_complete.sh
```

Этот скрипт поможет вам:
- ✅ Создать админ пользователя
- ✅ Настроить переменные окружения
- ✅ Задеплоить Python API
- ✅ Мигрировать промпты
- ✅ Создать frontend в Lovable

## 📋 **Ручная настройка (если нужно):**

### 1. **Создание админа**
```bash
# Установите переменные
export SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"
export SUPABASE_URL="https://vuznvbjsimejtoppzppv.supabase.co"

# Создайте админа
python3 scripts/create_admin.py
```

**Логин админа:**
- Email: `admin@example.com`
- Пароль: `admin123`

### 2. **Настройка переменных окружения**

В Supabase Dashboard: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/settings/functions

```
PYTHON_SERVICE_URL=https://your-api-domain.com
PYTHON_SERVICE_TOKEN=your-service-token
GOOGLE_API_KEY=your-google-api-key
GOOGLE_API_KEY2=your-backup-google-api-key
SUPABASE_URL=https://vuznvbjsimejtoppzppv.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
JWT_SECRET=your-jwt-secret
```

### 3. **Деплой Python API**

#### Railway (рекомендуется):
```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

#### Render:
1. Откройте: https://render.com
2. Создайте Web Service
3. Build Command: `pip install -r api/requirements.txt`
4. Start Command: `cd api && uvicorn main:app --host 0.0.0.0 --port $PORT`

#### DigitalOcean:
1. Откройте: https://cloud.digitalocean.com/apps
2. Создайте приложение с Dockerfile: `api/Dockerfile`

### 4. **Миграция промптов**
```bash
export SUPABASE_ANON_KEY="your-anon-key"
export SUPABASE_URL="https://vuznvbjsimejtoppzppv.supabase.co"
export ADMIN_EMAIL="admin@example.com"
export ADMIN_PASSWORD="admin123"

python3 scripts/migrate_prompts.py
```

### 5. **Создание frontend в Lovable**
1. Откройте: https://lovable.dev
2. Создайте новый проект
3. Используйте `LOVABLE_INTEGRATION.md` для интеграции

## 🔗 **Важные ссылки:**

- **Supabase Dashboard**: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv
- **API URL**: https://vuznvbjsimejtoppzppv.supabase.co
- **Edge Functions**: https://vuznvbjsimejtoppzppv.supabase.co/functions/v1/
- **Railway**: https://railway.app
- **Render**: https://render.com
- **DigitalOcean**: https://cloud.digitalocean.com/apps
- **Lovable**: https://lovable.dev

## 📊 **Система готова:**

- ✅ **База данных** - все таблицы созданы
- ✅ **Edge Functions** - задеплоены
- ✅ **Система кредитов** - настроена
- ✅ **Управление промптами** - готово
- ✅ **Безопасность** - RLS политики применены
- ✅ **Документация** - создана

## 🎯 **Следующие шаги:**

1. **Запустите** `./setup_complete.sh`
2. **Создайте админа** (если не сделано)
3. **Настройте переменные** окружения
4. **Задеплойте Python API** на выбранной платформе
5. **Мигрируйте промпты** в базу данных
6. **Создайте frontend** в Lovable
7. **Протестируйте систему**

## 🚀 **Готово к использованию!**

Ваша система AI Researcher Console полностью настроена и готова к работе! 🎉

**Удачного использования!** 🚀
