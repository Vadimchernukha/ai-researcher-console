# AI Researcher Console - Деплой на Supabase

Это руководство по развертыванию AI Researcher Console на Supabase с системой кредитов и админкой.

## 🏗️ Архитектура

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Supabase      │    │   Python API    │
│   (Lovable)     │◄──►│   (Database +   │◄──►│   (Analysis)    │
│                 │    │   Auth + Edge   │    │                 │
│                 │    │   Functions)    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 Предварительные требования

1. **Supabase CLI**
   ```bash
   npm install -g supabase
   ```

2. **Docker** (для локальной разработки)
   ```bash
   # Установите Docker Desktop
   ```

3. **Google AI API ключи**
   - Получите ключи в [Google AI Studio](https://makersuite.google.com/app/apikey)

## 🚀 Быстрый старт

### 1. Клонирование и настройка

```bash
# Клонируйте репозиторий
git clone <your-repo>
cd ai-researcher-console

# Установите зависимости
pip install -r requirements.txt
pip install -r api/requirements.txt

# Настройте переменные окружения
cp env.production .env
# Отредактируйте .env файл с вашими ключами
```

### 2. Деплой на Supabase

```bash
# Авторизация в Supabase
supabase login

# Запуск деплоя
./deploy.sh production
```

### 3. Настройка админ пользователя

1. Откройте [Supabase Dashboard](https://supabase.com/dashboard)
2. Перейдите в **Authentication > Users**
3. Создайте пользователя с email: `admin@example.com`
4. В **SQL Editor** выполните:
   ```sql
   UPDATE profiles 
   SET role = 'admin', credits = 999999 
   WHERE email = 'admin@example.com';
   ```

## 🔧 Детальная настройка

### База данных

Схема включает следующие таблицы:

- **profiles** - пользователи с ролями и кредитами
- **analyses** - результаты анализа сайтов
- **analysis_sessions** - сессии батчевой обработки
- **credit_transactions** - история транзакций кредитов
- **subscription_plans** - тарифные планы

### Edge Functions

Деплоятся следующие функции:

- **analyze-website** - анализ одного сайта
- **create-session** - создание сессии анализа
- **process-session** - обработка батча сайтов

### API Сервис

Python FastAPI сервис для анализа сайтов:

```bash
# Локальный запуск
cd api
uvicorn main:app --reload

# Docker запуск
docker-compose up api
```

## 💳 Система кредитов

### Тарифные планы

| План | Цена | Кредиты | Описание |
|------|------|---------|----------|
| Free | $0 | 100 | Бесплатный план |
| Basic | $10 | 1,000 | Базовый план |
| Pro | $30 | 10,000 | Профессиональный |
| Business | $99 | 50,000 | Бизнес план |

### Логика списания

- 1 кредит = 1 анализ сайта
- Админ пользователь имеет неограниченные кредиты
- Кредиты списываются только при успешном анализе

## 🔐 Безопасность

### Аутентификация

- JWT токены через Supabase Auth
- Row Level Security (RLS) политики
- Роли: `admin`, `user`

### API Безопасность

- Bearer токены для API сервиса
- CORS настройки
- Валидация входных данных
- Rate limiting (через Supabase)

### Переменные окружения

```bash
# Обязательные
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
GOOGLE_API_KEY=your-google-api-key
JWT_SECRET=your-jwt-secret

# Опциональные
PYTHON_SERVICE_URL=https://your-api.com
PYTHON_SERVICE_TOKEN=your-service-token
```

## 🌐 Деплой API сервиса

### Railway (Рекомендуется)

1. Подключите GitHub репозиторий
2. Настройте переменные окружения
3. Деплой автоматический при push

### Render

1. Создайте Web Service
2. Подключите репозиторий
3. Настройте build команду: `pip install -r api/requirements.txt`
4. Настройте start команду: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### DigitalOcean App Platform

1. Создайте App
2. Подключите репозиторий
3. Настройте Dockerfile в папке `api/`

## 📊 Мониторинг

### Логи

- Supabase Edge Functions: Dashboard > Functions > Logs
- API сервис: зависит от хостинга
- База данных: Dashboard > Logs

### Метрики

- Количество анализов
- Использование кредитов
- Время обработки
- Ошибки

## 🔄 Обновление

### Код

```bash
# Обновление Edge Functions
supabase functions deploy analyze-website
supabase functions deploy create-session
supabase functions deploy process-session

# Обновление схемы БД
supabase db push
```

### API сервис

```bash
# Перезапуск на хостинге
# Или автоматический деплой при push
```

## 🐛 Отладка

### Локальная разработка

```bash
# Запуск Supabase локально
supabase start

# Запуск API сервиса
cd api
uvicorn main:app --reload

# Тестирование
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{"domain": "example.com", "url": "https://example.com", "profile_type": "software"}'
```

### Проверка статуса

```bash
# Статус Supabase
supabase status

# Проверка Edge Functions
supabase functions list

# Логи Edge Functions
supabase functions logs analyze-website
```

## 📚 API Документация

### Endpoints

#### Анализ сайта
```http
POST /functions/v1/analyze-website
Authorization: Bearer <jwt-token>
Content-Type: application/json

{
  "domain": "example.com",
  "url": "https://example.com",
  "profile_type": "software"
}
```

#### Создание сессии
```http
POST /functions/v1/create-session
Authorization: Bearer <jwt-token>
Content-Type: application/json

{
  "name": "My Analysis Session",
  "profile_type": "software",
  "domains": ["example.com", "test.com"]
}
```

#### Обработка сессии
```http
POST /functions/v1/process-session
Authorization: Bearer <jwt-token>
Content-Type: application/json

{
  "session_id": "uuid"
}
```

## 🆘 Поддержка

### Частые проблемы

1. **Ошибка авторизации**
   - Проверьте JWT токен
   - Убедитесь что пользователь существует в БД

2. **Недостаточно кредитов**
   - Проверьте баланс пользователя
   - Админ имеет неограниченные кредиты

3. **Ошибка анализа**
   - Проверьте Google API ключи
   - Убедитесь что API сервис доступен

### Контакты

- Документация: [Supabase Docs](https://supabase.com/docs)
- Поддержка: [Supabase Discord](https://discord.supabase.com)

## 📝 Лицензия

MIT License - см. файл LICENSE
