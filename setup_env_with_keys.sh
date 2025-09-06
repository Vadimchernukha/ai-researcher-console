#!/bin/bash

# 🚀 Настройка переменных окружения с готовыми ключами

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

# Готовые ключи
SUPABASE_URL="https://vuznvbjsimejtoppzppv.supabase.co"
SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ1em52YmpzaW1lanRvcHB6cHB2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUyNTI3NTAsImV4cCI6MjA3MDgyODc1MH0.P8MDGDQIGoHObgRBFdeFWvbVjsShqOGcGhKEMRa-8B4"
SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ1em52YmpzaW1lanRvcHB6cHB2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTI1Mjc1MCwiZXhwIjoyMDcwODI4NzUwfQ.kpUbkTvP5Lrsk6Tw5Km3WbWXfwHkg69b1H_1YMyAdIM"
JWT_SECRET="ai-researcher-jwt-secret-2024"

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

# Создаем переменные окружения
echo ""
print_status "Переменные окружения для настройки:"
echo "=========================================="

echo "PYTHON_SERVICE_URL=$PYTHON_URL"
echo "PYTHON_SERVICE_TOKEN=$PYTHON_TOKEN"
echo "GOOGLE_API_KEY=$GOOGLE_KEY1"
echo "GOOGLE_API_KEY2=$GOOGLE_KEY2"
echo "SUPABASE_URL=$SUPABASE_URL"
echo "SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY"
echo "SUPABASE_SERVICE_ROLE_KEY=$SUPABASE_SERVICE_ROLE_KEY"
echo "JWT_SECRET=$JWT_SECRET"

echo ""
print_success "Переменные окружения подготовлены!"
echo ""
print_status "Настройте их в Supabase Dashboard:"
echo "📋 https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/settings/functions"
echo ""
print_warning "Скопируйте переменные выше и добавьте их в раздел Environment Variables"

# Создаем файл с переменными
cat > environment_variables.txt << EOF
PYTHON_SERVICE_URL=$PYTHON_URL
PYTHON_SERVICE_TOKEN=$PYTHON_TOKEN
GOOGLE_API_KEY=$GOOGLE_KEY1
GOOGLE_API_KEY2=$GOOGLE_KEY2
SUPABASE_URL=$SUPABASE_URL
SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY=$SUPABASE_SERVICE_ROLE_KEY
JWT_SECRET=$JWT_SECRET
EOF

echo ""
print_success "Переменные сохранены в файл: environment_variables.txt"
