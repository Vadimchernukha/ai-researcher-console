#!/bin/bash

# 🚀 Следующие шаги для AI Researcher Console

echo "🚀 AI Researcher Console - Следующие шаги"
echo "=========================================="

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo "🎯 Что у нас уже готово:"
echo "✅ Supabase проект настроен"
echo "✅ База данных создана"
echo "✅ Edge Functions задеплоены"
echo "✅ Админ пользователь создан: lgchernukha@gmail.com"
echo "✅ Переменные окружения подготовлены"
echo ""

echo "🚀 Что нужно сделать СЕЙЧАС:"
echo ""

echo "📋 ШАГ 1: Настроить переменные окружения в Supabase"
echo "1. Откройте: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/settings/functions"
echo "2. Найдите раздел 'Environment Variables'"
echo "3. Добавьте переменные из файла environment_variables.txt"
echo "4. Нажмите 'Save'"
echo ""

read -p "Нажмите Enter после настройки переменных..."

echo ""
echo "📋 ШАГ 2: Получить Google API ключи"
echo "1. Откройте: https://console.cloud.google.com/apis/credentials"
echo "2. Создайте новый API ключ"
echo "3. Включите Gemini API"
echo "4. Скопируйте ключ"
echo "5. Вернитесь в Supabase Dashboard"
echo "6. Замените 'your-google-api-key' на ваш реальный ключ"
echo ""

read -p "Нажмите Enter после получения Google API ключей..."

echo ""
echo "📋 ШАГ 3: Задеплоить Python API сервис"
echo ""
echo "Выберите платформу для деплоя:"
echo "1. Railway (рекомендуется)"
echo "2. Render"
echo "3. DigitalOcean"
echo "4. Пропустить (сделать позже)"
echo ""

read -p "Выберите вариант (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Railway:"
        echo "1. Откройте: https://railway.app"
        echo "2. Создайте аккаунт"
        echo "3. Создайте новый проект"
        echo "4. Подключите GitHub репозиторий"
        echo "5. Выберите папку 'api/'"
        echo "6. Railway автоматически задеплоит"
        ;;
    2)
        echo ""
        echo "🚀 Render:"
        echo "1. Откройте: https://render.com"
        echo "2. Создайте Web Service"
        echo "3. Подключите GitHub"
        echo "4. Build Command: pip install -r requirements.txt"
        echo "5. Start Command: uvicorn main:app --host 0.0.0.0 --port \$PORT"
        ;;
    3)
        echo ""
        echo "🚀 DigitalOcean:"
        echo "1. Откройте: https://cloud.digitalocean.com/apps"
        echo "2. Создайте приложение"
        echo "3. Подключите GitHub"
        echo "4. Выберите Dockerfile: api/Dockerfile"
        ;;
    4)
        echo ""
        echo "⏭️ Деплой пропущен"
        ;;
esac

echo ""
read -p "Нажмите Enter после деплоя Python API..."

echo ""
echo "📋 ШАГ 4: Обновить переменные окружения"
echo "1. Скопируйте URL вашего API"
echo "2. Вернитесь в Supabase Dashboard"
echo "3. Замените 'https://your-api-domain.com' на ваш реальный URL"
echo ""

read -p "Нажмите Enter после обновления URL..."

echo ""
echo "📋 ШАГ 5: Мигрировать промпты"
echo ""

# Устанавливаем переменные для миграции
export SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ1em52YmpzaW1lanRvcHB6cHB2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUyNTI3NTAsImV4cCI6MjA3MDgyODc1MH0.P8MDGDQIGoHObgRBFdeFWvbVjsShqOGcGhKEMRa-8B4"
export SUPABASE_URL="https://vuznvbjsimejtoppzppv.supabase.co"
export ADMIN_EMAIL="lgchernukha@gmail.com"
export ADMIN_PASSWORD="200815462Cv!"

echo "🔧 Миграция промптов..."
python3 scripts/migrate_prompts.py

if [ $? -eq 0 ]; then
    print_success "Промпты успешно мигрированы!"
else
    print_error "Ошибка миграции промптов"
fi

echo ""
echo "📋 ШАГ 6: Создать frontend в Lovable"
echo "1. Откройте: https://lovable.dev"
echo "2. Создайте новый проект"
echo "3. Используйте файл LOVABLE_INTEGRATION.md для интеграции"
echo ""

read -p "Нажмите Enter после создания frontend..."

echo ""
print_success "🎉 Все шаги выполнены!"
echo ""
echo "🎯 Система готова к работе:"
echo "✅ Supabase настроен"
echo "✅ Python API задеплоен"
echo "✅ Промпты мигрированы"
echo "✅ Frontend создан"
echo ""
echo "🚀 AI Researcher Console готов к использованию!"
