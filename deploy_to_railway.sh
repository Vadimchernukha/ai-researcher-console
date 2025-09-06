#!/bin/bash

# 🚀 Деплой Python API на Railway

echo "🚀 Деплой Python API на Railway"
echo "==============================="

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

echo "🎯 Рекомендация: Railway - самый простой способ деплоя Python API"
echo ""

echo "📋 Пошаговая инструкция:"
echo ""

echo "1️⃣ Создание аккаунта Railway"
echo "   Откройте: https://railway.app"
echo "   Нажмите 'Start a New Project'"
echo "   Войдите через GitHub (рекомендуется)"
echo ""

read -p "Нажмите Enter после создания аккаунта..."

echo ""
echo "2️⃣ Создание проекта"
echo "   Нажмите 'Deploy from GitHub repo'"
echo "   Выберите ваш репозиторий"
echo "   Выберите папку 'api/' (важно!)"
echo "   Railway автоматически определит Python проект"
echo ""

read -p "Нажмите Enter после создания проекта..."

echo ""
echo "3️⃣ Настройка переменных окружения"
echo "   В Railway Dashboard добавьте:"
echo ""

echo "SUPABASE_URL=https://vuznvbjsimejtoppzppv.supabase.co"
echo "SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ1em52YmpzaW1lanRvcHB6cHB2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUyNTI3NTAsImV4cCI6MjA3MDgyODc1MH0.P8MDGDQIGoHObgRBFdeFWvbVjsShqOGcGhKEMRa-8B4"
echo "SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ1em52YmpzaW1lanRvcHB6cHB2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTI1Mjc1MCwiZXhwIjoyMDcwODI4NzUwfQ.kpUbkTvP5Lrsk6Tw5Km3WbWXfwHkg69b1H_1YMyAdIM"
echo "GOOGLE_API_KEY=AIzaSyCxaE6KtU2iYuBhxyjeyZLANWj5apDc6PM"
echo "GOOGLE_API_KEY2=AIzaSyAhDmoZAa_RVmP1SfC8Yg04ymM2XcuH5lM"
echo "JWT_SECRET=ai-researcher-jwt-secret-2024"
echo ""

read -p "Нажмите Enter после настройки переменных..."

echo ""
echo "4️⃣ Деплой"
echo "   Railway автоматически начнет деплой"
echo "   Дождитесь завершения (2-3 минуты)"
echo "   Скопируйте URL вашего API"
echo ""

read -p "Нажмите Enter после завершения деплоя..."

echo ""
echo "5️⃣ Обновление переменных в Supabase"
echo "   После получения URL:"
echo "   Вернитесь в Supabase Dashboard"
echo "   Обновите PYTHON_SERVICE_URL на ваш Railway URL"
echo ""

read -p "Введите URL вашего Railway API: " RAILWAY_URL

if [ -z "$RAILWAY_URL" ]; then
    print_warning "URL не введен. Обновите PYTHON_SERVICE_URL в Supabase Dashboard позже"
else
    print_success "URL получен: $RAILWAY_URL"
    echo ""
    echo "🔧 Обновите переменную в Supabase Dashboard:"
    echo "   PYTHON_SERVICE_URL=$RAILWAY_URL"
fi

echo ""
print_success "🎉 Деплой на Railway завершен!"
echo ""
echo "✅ API доступен по URL: $RAILWAY_URL"
echo "✅ Автоматический HTTPS"
echo "✅ Автоматические обновления при пуше в GitHub"
echo ""
echo "🚀 Следующий шаг: Миграция промптов!"
