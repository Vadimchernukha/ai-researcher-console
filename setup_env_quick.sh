#!/bin/bash

# 🚀 Быстрая настройка переменных окружения

echo "🚀 Настройка переменных окружения для AI Researcher Console"
echo "=========================================================="

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

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    print_error "python3 не найден. Установите Python 3"
    exit 1
fi

# Проверяем наличие supabase
if ! python3 -c "import supabase" 2>/dev/null; then
    print_status "Установка supabase-py..."
    pip3 install supabase
fi

# Получаем anon key
echo ""
print_status "Получите anon key из Supabase Dashboard:"
echo "📋 https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/settings/api"
echo ""
read -p "Введите SUPABASE_ANON_KEY: " ANON_KEY

if [ -z "$ANON_KEY" ]; then
    print_error "Anon key не может быть пустым"
    exit 1
fi

# Получаем Google API ключи
echo ""
print_status "Получите Google API ключи:"
echo "📋 https://console.cloud.google.com/apis/credentials"
echo ""
read -p "Введите GOOGLE_API_KEY: " GOOGLE_KEY1
read -p "Введите GOOGLE_API_KEY2 (backup): " GOOGLE_KEY2

if [ -z "$GOOGLE_KEY1" ]; then
    print_error "Google API key не может быть пустым"
    exit 1
fi

# Получаем Python Service URL
echo ""
print_status "Python Service URL (после деплоя):"
read -p "Введите PYTHON_SERVICE_URL (или нажмите Enter для пропуска): " PYTHON_URL
if [ -z "$PYTHON_URL" ]; then
    PYTHON_URL="https://your-api-domain.com"
fi

# Получаем Python Service Token
read -p "Введите PYTHON_SERVICE_TOKEN (или нажмите Enter для пропуска): " PYTHON_TOKEN
if [ -z "$PYTHON_TOKEN" ]; then
    PYTHON_TOKEN="your-service-token"
fi

# JWT Secret
read -p "Введите JWT_SECRET (или нажмите Enter для автогенерации): " JWT_SECRET
if [ -z "$JWT_SECRET" ]; then
    JWT_SECRET="ai-researcher-jwt-secret-2024"
fi

# Создаем переменные окружения
echo ""
print_status "Переменные окружения для настройки:"
echo "=========================================="

echo "PYTHON_SERVICE_URL=$PYTHON_URL"
echo "PYTHON_SERVICE_TOKEN=$PYTHON_TOKEN"
echo "GOOGLE_API_KEY=$GOOGLE_KEY1"
echo "GOOGLE_API_KEY2=$GOOGLE_KEY2"
echo "SUPABASE_URL=https://vuznvbjsimejtoppzppv.supabase.co"
echo "SUPABASE_ANON_KEY=$ANON_KEY"
echo "SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ1em52YmpzaW1lanRvcHB6cHB2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTI1Mjc1MCwiZXhwIjoyMDcwODI4NzUwfQ.kpUbkTvP5Lrsk6Tw5Km3WbWXfwHkg69b1H_1YMyAdIM"
echo "JWT_SECRET=$JWT_SECRET"

echo ""
print_success "Переменные окружения подготовлены!"
echo ""
print_status "Настройте их в Supabase Dashboard:"
echo "📋 https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/settings/functions"
echo ""
print_warning "Скопируйте переменные выше и добавьте их в раздел Environment Variables"
