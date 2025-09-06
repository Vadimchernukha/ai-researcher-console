#!/bin/bash

# Скрипт деплоя AI Researcher Console на Supabase
# Использование: ./deploy.sh [environment]

set -e

ENVIRONMENT=${1:-production}
PROJECT_NAME="ai-researcher-console"

echo "🚀 Деплой AI Researcher Console в окружение: $ENVIRONMENT"

# Проверка наличия Supabase CLI
if ! command -v supabase &> /dev/null; then
    echo "❌ Supabase CLI не установлен. Установите его:"
    echo "npm install -g supabase"
    exit 1
fi

# Проверка авторизации в Supabase
if ! supabase projects list &> /dev/null; then
    echo "❌ Не авторизован в Supabase. Выполните:"
    echo "supabase login"
    exit 1
fi

# Создание проекта (если не существует)
echo "📋 Проверка проекта Supabase..."
if ! supabase projects list | grep -q "$PROJECT_NAME"; then
    echo "🆕 Создание нового проекта Supabase..."
    supabase projects create "$PROJECT_NAME" --region us-east-1
else
    echo "✅ Проект $PROJECT_NAME уже существует"
fi

# Получение ссылки на проект
PROJECT_REF=$(supabase projects list | grep "$PROJECT_NAME" | awk '{print $1}')
echo "🔗 Project Reference: $PROJECT_REF"

# Инициализация Supabase (если не инициализирован)
if [ ! -f "supabase/config.toml" ]; then
    echo "🔧 Инициализация Supabase..."
    supabase init
fi

# Связывание с удаленным проектом
echo "🔗 Связывание с удаленным проектом..."
supabase link --project-ref "$PROJECT_REF"

# Применение миграций базы данных
echo "🗄️ Применение миграций базы данных..."
supabase db push

# Деплой Edge Functions
echo "⚡ Деплой Edge Functions..."
supabase functions deploy analyze-website
supabase functions deploy create-session
supabase functions deploy process-session
supabase functions deploy manage-prompts
supabase functions deploy get-active-prompt

# Настройка переменных окружения для Edge Functions
echo "🔐 Настройка переменных окружения..."
supabase secrets set PYTHON_SERVICE_URL="https://your-api-domain.com"
supabase secrets set PYTHON_SERVICE_TOKEN="your-service-token"
supabase secrets set GOOGLE_API_KEY="$GOOGLE_API_KEY"
supabase secrets set GOOGLE_API_KEY2="$GOOGLE_API_KEY2"

# Создание админ пользователя
echo "👤 Создание админ пользователя..."
echo "Выполните в Supabase Dashboard:"
echo "1. Перейдите в Authentication > Users"
echo "2. Создайте пользователя с email: admin@example.com"
echo "3. Установите пароль"
echo "4. В SQL Editor выполните:"
echo "UPDATE profiles SET role = 'admin', credits = 999999 WHERE email = 'admin@example.com';"

# Миграция промптов
echo "📝 Миграция промптов..."
if [ -f "scripts/migrate_prompts.py" ]; then
    echo "Запуск миграции промптов..."
    python scripts/migrate_prompts.py
else
    echo "⚠️ Скрипт миграции промптов не найден"
fi

# Деплой API сервиса (если используется внешний хостинг)
if [ "$ENVIRONMENT" = "production" ]; then
    echo "🌐 Деплой API сервиса..."
    
    # Здесь можно добавить деплой на Railway, Render, или другой сервис
    # Например, для Railway:
    # railway login
    # railway up --service api
    
    echo "⚠️ Не забудьте настроить деплой API сервиса на вашем хостинге"
    echo "Рекомендуемые сервисы: Railway, Render, DigitalOcean App Platform"
fi

# Настройка домена (опционально)
if [ "$ENVIRONMENT" = "production" ]; then
    echo "🌍 Настройка домена..."
    echo "В Supabase Dashboard:"
    echo "1. Перейдите в Settings > General"
    echo "2. Добавьте ваш домен в Custom Domains"
    echo "3. Настройте DNS записи"
fi

# Финальная проверка
echo "✅ Проверка деплоя..."
supabase status

echo ""
echo "🎉 Деплой завершен!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Откройте Supabase Dashboard: https://supabase.com/dashboard/project/$PROJECT_REF"
echo "2. Создайте админ пользователя (см. инструкции выше)"
echo "3. Настройте API сервис на внешнем хостинге"
echo "4. Обновите переменные окружения PYTHON_SERVICE_URL"
echo "5. Протестируйте API endpoints"
echo ""
echo "🔗 Полезные ссылки:"
echo "- Supabase Dashboard: https://supabase.com/dashboard/project/$PROJECT_REF"
echo "- API Docs: https://$PROJECT_REF.supabase.co/rest/v1/"
echo "- Edge Functions: https://$PROJECT_REF.supabase.co/functions/v1/"
echo ""
echo "📚 Документация:"
echo "- Supabase: https://supabase.com/docs"
echo "- Edge Functions: https://supabase.com/docs/guides/functions"
echo "- Database: https://supabase.com/docs/guides/database"
