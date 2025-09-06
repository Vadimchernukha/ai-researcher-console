#!/bin/bash

# 🚀 Полная настройка AI Researcher Console
# Этот скрипт поможет вам завершить настройку системы

echo "🚀 AI Researcher Console - Завершение настройки"
echo "=============================================="

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверяем наличие необходимых инструментов
check_dependencies() {
    print_status "Проверка зависимостей..."
    
    if ! command -v npx &> /dev/null; then
        print_error "npx не найден. Установите Node.js"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        print_error "python3 не найден. Установите Python 3"
        exit 1
    fi
    
    print_success "Все зависимости установлены"
}

# Получаем информацию о проекте
get_project_info() {
    print_status "Получение информации о проекте..."
    
    PROJECT_ID="vuznvbjsimejtoppzppv"
    PROJECT_URL="https://vuznvbjsimejtoppzppv.supabase.co"
    
    echo "📋 Информация о проекте:"
    echo "   Project ID: $PROJECT_ID"
    echo "   URL: $PROJECT_URL"
    echo "   Dashboard: https://supabase.com/dashboard/project/$PROJECT_ID"
}

# Создание админ пользователя
create_admin() {
    print_status "Создание админ пользователя..."
    
    echo "🔐 Для создания админа нужен Service Role Key"
    echo "Получите его в: https://supabase.com/dashboard/project/$PROJECT_ID/settings/api"
    echo ""
    read -p "Введите SUPABASE_SERVICE_ROLE_KEY: " SERVICE_KEY
    
    if [ -z "$SERVICE_KEY" ]; then
        print_error "Service Role Key не может быть пустым"
        return 1
    fi
    
    export SUPABASE_SERVICE_ROLE_KEY="$SERVICE_KEY"
    export SUPABASE_URL="$PROJECT_URL"
    
    python3 scripts/create_admin.py
    
    if [ $? -eq 0 ]; then
        print_success "Админ пользователь создан!"
        echo "📧 Email: admin@example.com"
        echo "🔑 Пароль: admin123"
    else
        print_error "Не удалось создать админ пользователя"
        return 1
    fi
}

# Настройка переменных окружения
setup_environment() {
    print_status "Настройка переменных окружения..."
    
    echo "🔧 Настройте переменные в Supabase Dashboard:"
    echo "   https://supabase.com/dashboard/project/$PROJECT_ID/settings/functions"
    echo ""
    echo "📋 Добавьте следующие переменные:"
    echo "   PYTHON_SERVICE_URL=https://your-api-domain.com"
    echo "   PYTHON_SERVICE_TOKEN=your-service-token"
    echo "   GOOGLE_API_KEY=your-google-api-key"
    echo "   GOOGLE_API_KEY2=your-backup-google-api-key"
    echo "   SUPABASE_URL=$PROJECT_URL"
    echo "   SUPABASE_ANON_KEY=your-anon-key"
    echo "   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key"
    echo "   JWT_SECRET=your-jwt-secret"
    echo ""
    read -p "Нажмите Enter после настройки переменных..."
}

# Деплой Python API
deploy_api() {
    print_status "Деплой Python API сервиса..."
    
    echo "🚀 Варианты деплоя:"
    echo "1. Railway (рекомендуется)"
    echo "2. Render"
    echo "3. DigitalOcean App Platform"
    echo "4. Пропустить (сделать позже)"
    echo ""
    read -p "Выберите вариант (1-4): " choice
    
    case $choice in
        1)
            deploy_railway
            ;;
        2)
            deploy_render
            ;;
        3)
            deploy_digitalocean
            ;;
        4)
            print_warning "Деплой пропущен. Сделайте это позже."
            ;;
        *)
            print_error "Неверный выбор"
            ;;
    esac
}

# Деплой на Railway
deploy_railway() {
    print_status "Деплой на Railway..."
    
    if ! command -v railway &> /dev/null; then
        print_status "Установка Railway CLI..."
        npm install -g @railway/cli
    fi
    
    echo "🔐 Войдите в Railway:"
    railway login
    
    echo "🚀 Создание проекта..."
    railway init
    
    echo "📦 Деплой..."
    railway up
    
    print_success "Деплой на Railway завершен!"
    echo "📋 Не забудьте настроить переменные окружения в Railway Dashboard"
}

# Деплой на Render
deploy_render() {
    print_status "Деплой на Render..."
    
    echo "🌐 Откройте: https://render.com"
    echo "📋 Создайте новый Web Service с настройками:"
    echo "   Build Command: pip install -r api/requirements.txt"
    echo "   Start Command: cd api && uvicorn main:app --host 0.0.0.0 --port \$PORT"
    echo "   Environment: Python 3.11"
    echo ""
    read -p "Нажмите Enter после создания сервиса..."
}

# Деплой на DigitalOcean
deploy_digitalocean() {
    print_status "Деплой на DigitalOcean..."
    
    echo "🌐 Откройте: https://cloud.digitalocean.com/apps"
    echo "📋 Создайте новое приложение с Dockerfile: api/Dockerfile"
    echo ""
    read -p "Нажмите Enter после создания приложения..."
}

# Миграция промптов
migrate_prompts() {
    print_status "Миграция промптов..."
    
    echo "🔐 Для миграции промптов нужен Anon Key"
    echo "Получите его в: https://supabase.com/dashboard/project/$PROJECT_ID/settings/api"
    echo ""
    read -p "Введите SUPABASE_ANON_KEY: " ANON_KEY
    
    if [ -z "$ANON_KEY" ]; then
        print_error "Anon Key не может быть пустым"
        return 1
    fi
    
    export SUPABASE_ANON_KEY="$ANON_KEY"
    export SUPABASE_URL="$PROJECT_URL"
    export ADMIN_EMAIL="admin@example.com"
    export ADMIN_PASSWORD="admin123"
    
    python3 scripts/migrate_prompts.py
    
    if [ $? -eq 0 ]; then
        print_success "Промпты мигрированы!"
    else
        print_error "Не удалось мигрировать промпты"
        return 1
    fi
}

# Создание frontend
create_frontend() {
    print_status "Создание frontend в Lovable..."
    
    echo "🌐 Откройте: https://lovable.dev"
    echo "📋 Создайте новый проект"
    echo "📖 Используйте файл LOVABLE_INTEGRATION.md для интеграции"
    echo ""
    read -p "Нажмите Enter после создания проекта в Lovable..."
}

# Основная функция
main() {
    check_dependencies
    get_project_info
    
    echo ""
    echo "🎯 Выберите действия для выполнения:"
    echo "1. Создать админ пользователя"
    echo "2. Настроить переменные окружения"
    echo "3. Задеплоить Python API"
    echo "4. Мигрировать промпты"
    echo "5. Создать frontend в Lovable"
    echo "6. Выполнить все действия"
    echo "7. Выход"
    echo ""
    read -p "Выберите вариант (1-7): " choice
    
    case $choice in
        1)
            create_admin
            ;;
        2)
            setup_environment
            ;;
        3)
            deploy_api
            ;;
        4)
            migrate_prompts
            ;;
        5)
            create_frontend
            ;;
        6)
            create_admin
            setup_environment
            deploy_api
            migrate_prompts
            create_frontend
            ;;
        7)
            print_status "Выход..."
            exit 0
            ;;
        *)
            print_error "Неверный выбор"
            exit 1
            ;;
    esac
    
    echo ""
    print_success "Настройка завершена!"
    echo "📋 Проверьте файл DEPLOYMENT_STATUS.md для статуса"
}

# Запуск
main "$@"
