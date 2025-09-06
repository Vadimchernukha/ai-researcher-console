#!/bin/bash

# 🚀 Быстрое создание пользователя lgchernukha@gmail.com

echo "🚀 Создание пользователя lgchernukha@gmail.com"
echo "=============================================="

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

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    print_error "python3 не найден. Установите Python 3"
    exit 1
fi

# Проверяем наличие pip
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 не найден. Установите pip"
    exit 1
fi

# Устанавливаем зависимости если нужно
print_status "Проверка зависимостей..."
if ! python3 -c "import supabase" 2>/dev/null; then
    print_status "Установка supabase-py..."
    pip3 install supabase
fi

# Получаем Service Role Key
echo ""
print_status "Для создания пользователя нужен Service Role Key"
echo "📋 Получите ключ в: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/settings/api"
echo ""
read -p "Введите SUPABASE_SERVICE_ROLE_KEY: " SERVICE_KEY

if [ -z "$SERVICE_KEY" ]; then
    print_error "Service Role Key не может быть пустым"
    exit 1
fi

# Устанавливаем переменные окружения
export SUPABASE_SERVICE_ROLE_KEY="$SERVICE_KEY"
export SUPABASE_URL="https://vuznvbjsimejtoppzppv.supabase.co"

# Создаем пользователя
print_status "Создание пользователя..."
python3 scripts/create_user.py

if [ $? -eq 0 ]; then
    print_success "Пользователь успешно создан!"
    echo ""
    echo "📧 Email: lgchernukha@gmail.com"
    echo "🔑 Пароль: 200815462Cv!"
    echo "💳 Кредиты: 100"
    echo "👑 Роль: user"
    echo ""
    echo "🎉 Пользователь готов к использованию!"
else
    print_error "Не удалось создать пользователя"
    exit 1
fi
