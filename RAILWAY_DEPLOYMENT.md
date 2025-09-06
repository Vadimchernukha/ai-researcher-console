# 🚂 Railway Deployment Guide

Пошаговое руководство по деплою AI Researcher Console на Railway.

## 🔧 Исправленные проблемы

### ✅ Исправления Dockerfile:
- ✅ Добавлены все необходимые системные зависимости для Playwright
- ✅ Правильная последовательность установки: root → app user
- ✅ Поддержка переменной `PORT` от Railway
- ✅ Улучшенная обработка прав доступа

### ✅ Исправления railway.json:
- ✅ Удален конфликтующий `startCommand`
- ✅ Увеличен `healthcheckTimeout` до 300 секунд
- ✅ Оптимизированы параметры restart policy

### ✅ Исправления API:
- ✅ Улучшена обработка ошибок в `/health`
- ✅ Добавлено подробное логирование startup
- ✅ Проверка переменных окружения

## 🚀 Инструкция по деплою

### 1. Подготовка проекта

```bash
# Убедитесь что все файлы обновлены
git add .
git commit -m "Fix Railway deployment issues"
git push origin main
```

### 2. Настройка переменных окружения в Railway

Зайдите в Railway Dashboard → Variables и добавьте:

```bash
# Обязательные переменные
ENVIRONMENT=production
GOOGLE_API_KEY=your-actual-google-api-key
GOOGLE_API_KEY2=your-second-google-api-key
JWT_SECRET=your-super-secret-jwt-key-here

# Опциональные
PYTHONUNBUFFERED=1
PROFILE=software
MAX_CONCURRENT=5
```

**⚠️ ВАЖНО:** Замените `your-actual-google-api-key` на реальные API ключи!

### 3. Деплой

Railway автоматически задеплоит проект при push в main ветку.

### 4. Проверка деплоя

После деплоя проверьте:

```bash
# Замените YOUR_RAILWAY_URL на ваш URL
curl https://your-app.railway.app/health

# Или используйте тестовый скрипт
python test_railway_deployment.py https://your-app.railway.app
```

## 🔍 Troubleshooting

### Проблема: "Service unavailable" 
**Решение:** 
- Проверьте переменные окружения в Railway
- Убедитесь что `GOOGLE_API_KEY` установлен
- Проверьте логи в Railway Dashboard

### Проблема: Healthcheck timeout
**Решение:**
- Увеличен timeout до 300 секунд
- Playwright может требовать времени для инициализации

### Проблема: Permission denied
**Решение:**
- Исправлено в новом Dockerfile
- Playwright устанавливается от root, затем переключение на app user

## 📊 Мониторинг

### Логи Railway:
```bash
# В Railway Dashboard
Deployments → Logs → View logs
```

### Эндпоинты для мониторинга:
- `GET /health` - проверка состояния
- `GET /profiles` - список доступных профилей

## 🎯 Следующие шаги

После успешного деплоя базовой версии:

1. **Добавить реальную обработку** - включить pipeline
2. **Настроить Supabase** - подключить базу данных  
3. **Добавить frontend** - интеграция с Lovable
4. **Масштабирование** - оптимизация для production

## 🆘 Поддержка

Если деплой все еще не работает:

1. Проверьте логи в Railway Dashboard
2. Убедитесь что все переменные окружения установлены
3. Попробуйте локальный тест: `python test_railway_deployment.py`
4. Проверьте статус здоровья: `curl https://your-app.railway.app/health`

---

**Статус:** ✅ Готово к деплою  
**Последнее обновление:** December 2024
