# 🚀 Инструкции по деплою AI Researcher Console

## 1. **Создание админ пользователя**

### Через Supabase Dashboard:
1. Откройте: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv
2. Перейдите в **SQL Editor**
3. Выполните скрипт из файла `create_admin_user.sql`:

```sql
-- Создание админ пользователя
INSERT INTO auth.users (
    instance_id, id, aud, role, email, encrypted_password,
    email_confirmed_at, raw_app_meta_data, raw_user_meta_data,
    created_at, updated_at
) VALUES (
    '00000000-0000-0000-0000-000000000000',
    gen_random_uuid(),
    'authenticated',
    'authenticated',
    'admin@example.com',
    crypt('admin123', gen_salt('bf')),
    NOW(),
    '{"provider": "email", "providers": ["email"]}',
    '{"full_name": "Admin User"}',
    NOW(),
    NOW()
);

-- Создание профиля админа
INSERT INTO public.profiles (
    id, email, full_name, role, credits, subscription_plan
) VALUES (
    (SELECT id FROM auth.users WHERE email = 'admin@example.com'),
    'admin@example.com',
    'Admin User',
    'admin',
    999999,
    'free'
);
```

**Логин админа:**
- Email: `admin@example.com`
- Пароль: `admin123`

## 2. **Настройка переменных окружения**

### В Supabase Dashboard:
1. Откройте: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/settings/functions
2. Добавьте переменные:

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

### Получение ключей:
- **Supabase ключи**: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/settings/api
- **Google API**: https://console.cloud.google.com/apis/credentials

## 3. **Деплой Python API сервиса**

### Вариант A: Railway (Рекомендуется)

1. **Установите Railway CLI:**
```bash
npm install -g @railway/cli
```

2. **Войдите в Railway:**
```bash
railway login
```

3. **Создайте проект:**
```bash
railway init
```

4. **Деплой:**
```bash
railway up
```

5. **Настройте переменные окружения:**
```bash
railway variables set SUPABASE_URL=https://vuznvbjsimejtoppzppv.supabase.co
railway variables set SUPABASE_ANON_KEY=your-anon-key
railway variables set GOOGLE_API_KEY=your-google-api-key
railway variables set JWT_SECRET=your-jwt-secret
```

### Вариант B: Render

1. **Создайте аккаунт**: https://render.com
2. **Создайте новый Web Service**
3. **Подключите GitHub репозиторий**
4. **Настройте:**
   - Build Command: `pip install -r api/requirements.txt`
   - Start Command: `cd api && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Environment: Python 3.11

### Вариант C: DigitalOcean App Platform

1. **Создайте аккаунт**: https://cloud.digitalocean.com/apps
2. **Создайте новое приложение**
3. **Подключите GitHub репозиторий**
4. **Настройте Dockerfile**: `api/Dockerfile`

## 4. **Проверка деплоя**

### После деплоя Python API:
1. Получите URL вашего API (например: `https://ai-researcher-api.railway.app`)
2. Обновите переменную `PYTHON_SERVICE_URL` в Supabase
3. Протестируйте API:

```bash
curl -X GET "https://your-api-domain.com/health"
```

### Тестирование Edge Functions:
```bash
curl -X POST "https://vuznvbjsimejtoppzppv.supabase.co/functions/v1/analyze-website" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "example.com",
    "url": "https://example.com",
    "profile_type": "software"
  }'
```

## 5. **Миграция промптов**

После создания админа и настройки API:

```bash
export SUPABASE_URL="https://vuznvbjsimejtoppzppv.supabase.co"
export SUPABASE_ANON_KEY="your-anon-key"
export ADMIN_EMAIL="admin@example.com"
export ADMIN_PASSWORD="admin123"

python scripts/migrate_prompts.py
```

## 6. **Создание frontend в Lovable**

1. Откройте: https://lovable.dev
2. Создайте новый проект
3. Используйте файл `LOVABLE_INTEGRATION.md` для интеграции
4. Настройте Supabase клиент с вашими ключами

## ✅ **Проверочный список:**

- [ ] Админ пользователь создан
- [ ] Переменные окружения настроены
- [ ] Python API задеплоен
- [ ] Edge Functions работают
- [ ] Промпты мигрированы
- [ ] Frontend создан в Lovable

## 🔗 **Полезные ссылки:**

- **Supabase Dashboard**: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv
- **Railway**: https://railway.app
- **Render**: https://render.com
- **DigitalOcean**: https://cloud.digitalocean.com/apps
- **Lovable**: https://lovable.dev

**Готово к использованию!** 🎉
