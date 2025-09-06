#!/bin/bash

# 🚀 Настройка переменных окружения через Supabase CLI

echo "🚀 Настройка переменных окружения через Supabase CLI"
echo "=================================================="

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

# Проверяем наличие npx
if ! command -v npx &> /dev/null; then
    print_error "npx не найден. Установите Node.js"
    exit 1
fi

# Проверяем наличие supabase CLI
if ! npx supabase --version &> /dev/null; then
    print_error "Supabase CLI не найден"
    exit 1
fi

print_status "Настройка переменных окружения через CLI..."

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

print_status "Установка переменных окружения..."

# Устанавливаем переменные через CLI
npx supabase secrets set PYTHON_SERVICE_URL="$PYTHON_URL"
npx supabase secrets set PYTHON_SERVICE_TOKEN="$PYTHON_TOKEN"
npx supabase secrets set GOOGLE_API_KEY="$GOOGLE_KEY1"
npx supabase secrets set GOOGLE_API_KEY2="$GOOGLE_KEY2"
npx supabase secrets set SUPABASE_URL="https://vuznvbjsimejtoppzppv.supabase.co"
npx supabase secrets set SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ1em52YmpzaW1lanRvcHB6cHB2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUyNTI3NTAsImV4cCI6MjA3MDgyODc1MH0.P8MDGDQIGoHObgRBFdeFWvbVjsShqOGcGhKEMRa-8B4"
npx supabase secrets set SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ1em52YmpzaW1lanRvcHB6cHB2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTI1Mjc1MCwiZXhwIjoyMDcwODI4NzUwfQ.kpUbkTvP5Lrsk6Tw5Km3WbWXfwHkg69b1H_1YMyAdIM"
npx supabase secrets set JWT_SECRET="$JWT_SECRET"

if [ $? -eq 0 ]; then
    print_success "Переменные окружения успешно установлены!"
    echo ""
    echo "✅ PYTHON_SERVICE_URL: $PYTHON_URL"
    echo "✅ PYTHON_SERVICE_TOKEN: $PYTHON_TOKEN"
    echo "✅ GOOGLE_API_KEY: $GOOGLE_KEY1"
    echo "✅ GOOGLE_API_KEY2: $GOOGLE_KEY2"
    echo "✅ SUPABASE_URL: https://vuznvbjsimejtoppzppv.supabase.co"
    echo "✅ SUPABASE_ANON_KEY: установлен"
    echo "✅ SUPABASE_SERVICE_ROLE_KEY: установлен"
    echo "✅ JWT_SECRET: $JWT_SECRET"
    echo ""
    print_success "🎉 Все переменные окружения настроены!"
else
    print_error "Ошибка установки переменных окружения"
    exit 1
fi
