# 🚀 Статус деплоя AI Researcher Console

## ✅ **Выполнено:**

### 1. **Проект Supabase**
- ✅ Связан с существующим проектом: `vuznvbjsimejtoppzppv`
- ✅ Применены миграции базы данных
- ✅ Созданы все необходимые таблицы

### 2. **База данных**
- ✅ Таблица `profiles` - пользователи с ролями и кредитами
- ✅ Таблица `analyses` - результаты анализа сайтов
- ✅ Таблица `analysis_sessions` - сессии батчевой обработки
- ✅ Таблица `credit_transactions` - история транзакций
- ✅ Таблица `subscription_plans` - тарифные планы
- ✅ Таблица `system_settings` - системные настройки
- ✅ Таблица `prompts` - управление промптами
- ✅ Таблица `prompt_versions` - версионирование промптов
- ✅ Таблица `prompt_analytics` - аналитика промптов
- ✅ RLS политики для безопасности

### 3. **Edge Functions**
- ✅ `analyze-website` - анализ одного сайта
- ✅ `create-session` - создание сессии анализа
- ✅ `process-session` - обработка батча сайтов
- ✅ `manage-prompts` - управление промптами
- ✅ `get-active-prompt` - получение активных промптов

### 4. **Система кредитов**
- ✅ 4 тарифных плана: Free (100), Basic ($10/1000), Pro ($30/10000), Business ($99/50000)
- ✅ 1 кредит = 1 анализ сайта
- ✅ Админ имеет неограниченные кредиты (999999)
- ✅ Автоматическое списание кредитов

## 🔧 **Следующие шаги:**

### 1. **Создание админ пользователя**
```bash
# Откройте Supabase Dashboard:
# https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv

# 1. Перейдите в Authentication > Users
# 2. Создайте пользователя с email: admin@example.com
# 3. Установите пароль
# 4. В SQL Editor выполните:
UPDATE profiles SET role = 'admin', credits = 999999 WHERE email = 'admin@example.com';
```

### 2. **Настройка переменных окружения**
```bash
# В Supabase Dashboard > Settings > Edge Functions
# Добавьте переменные:
PYTHON_SERVICE_URL=https://your-api-domain.com
PYTHON_SERVICE_TOKEN=your-service-token
GOOGLE_API_KEY=your-google-api-key
GOOGLE_API_KEY2=your-backup-google-api-key
```

### 3. **Деплой Python API сервиса**
```bash
# Варианты хостинга:
# - Railway: https://railway.app
# - Render: https://render.com
# - DigitalOcean App Platform: https://cloud.digitalocean.com/apps

# Настройте переменные окружения:
SUPABASE_URL=https://vuznvbjsimejtoppzppv.supabase.co
SUPABASE_ANON_KEY=your-anon-key
GOOGLE_API_KEY=your-google-api-key
JWT_SECRET=your-jwt-secret
```

### 4. **Миграция промптов**
```bash
# После создания админ пользователя:
export SUPABASE_URL="https://vuznvbjsimejtoppzppv.supabase.co"
export SUPABASE_ANON_KEY="your-anon-key"
export ADMIN_EMAIL="admin@example.com"
export ADMIN_PASSWORD="your-admin-password"

python scripts/migrate_prompts.py
```

## 📊 **Информация о проекте:**

- **Project ID**: `vuznvbjsimejtoppzppv`
- **Region**: `us-east-2`
- **Dashboard**: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv
- **API URL**: https://vuznvbjsimejtoppzppv.supabase.co
- **Edge Functions**: https://vuznvbjsimejtoppzppv.supabase.co/functions/v1/

## 🔗 **API Endpoints:**

### Анализ сайта
```http
POST https://vuznvbjsimejtoppzppv.supabase.co/functions/v1/analyze-website
Authorization: Bearer <jwt-token>
Content-Type: application/json

{
  "domain": "example.com",
  "url": "https://example.com",
  "profile_type": "software"
}
```

### Создание сессии
```http
POST https://vuznvbjsimejtoppzppv.supabase.co/functions/v1/create-session
Authorization: Bearer <jwt-token>
Content-Type: application/json

{
  "name": "My Analysis Session",
  "profile_type": "software",
  "domains": ["example.com", "test.com"]
}
```

### Управление промптами (только админ)
```http
GET https://vuznvbjsimejtoppzppv.supabase.co/functions/v1/manage-prompts
Authorization: Bearer <admin-jwt-token>
```

## 🎯 **Готово к использованию:**

1. ✅ **База данных** - все таблицы созданы
2. ✅ **Edge Functions** - все функции задеплоены
3. ✅ **Система кредитов** - настроена
4. ✅ **Управление промптами** - готово
5. ✅ **Безопасность** - RLS политики применены

## 🚀 **Следующий этап:**

1. Создайте админ пользователя
2. Настройте переменные окружения
3. Задеплойте Python API сервис
4. Мигрируйте промпты
5. Создайте frontend в Lovable

**Система готова к работе!** 🎉
