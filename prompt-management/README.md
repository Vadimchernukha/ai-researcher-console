# Управление промптами в продакшене

Система для динамического управления промптами без передеплоя приложения.

## 🎯 Проблема

В текущей системе промпты захардкожены в коде:
- Нужно передеплоить приложение для изменения промптов
- Нет версионирования промптов
- Нет A/B тестирования
- Сложно отслеживать эффективность промптов

## 💡 Решения

### 1. База данных (Рекомендуется)

Хранить промпты в Supabase с версионированием и A/B тестированием.

### 2. Внешние сервисы

Использовать специализированные сервисы для управления промптами.

### 3. Файловая система

Хранить промпты в файлах с hot-reload.

## 🏗️ Архитектура

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Admin Panel   │    │   Supabase DB   │    │   Python API    │
│   (Lovable)     │◄──►│   (Prompts)     │◄──►│   (Cache)       │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📊 Схема базы данных

### Таблица prompts
```sql
CREATE TABLE public.prompts (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    profile_type TEXT NOT NULL,
    prompt_type TEXT NOT NULL CHECK (prompt_type IN ('extraction', 'classification')),
    version INTEGER NOT NULL DEFAULT 1,
    content TEXT NOT NULL,
    variables JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    is_default BOOLEAN DEFAULT false,
    performance_score DECIMAL(5,2),
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES public.profiles(id)
);
```

### Таблица prompt_versions
```sql
CREATE TABLE public.prompt_versions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    prompt_id UUID REFERENCES public.prompts(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    content TEXT NOT NULL,
    change_log TEXT,
    performance_metrics JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES public.profiles(id)
);
```

### Таблица prompt_analytics
```sql
CREATE TABLE public.prompt_analytics (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    prompt_id UUID REFERENCES public.prompts(id) ON DELETE CASCADE,
    analysis_id UUID REFERENCES public.analyses(id) ON DELETE CASCADE,
    success BOOLEAN NOT NULL,
    processing_time DECIMAL(10,2),
    confidence_score DECIMAL(5,2),
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🔧 Реализация

### 1. Обновление схемы БД

Добавить таблицы промптов в существующую схему.

### 2. API для управления промптами

Создать Edge Functions для CRUD операций с промптами.

### 3. Кэширование в Python API

Кэшировать активные промпты в Redis/Memory.

### 4. Admin панель

Интерфейс для управления промптами в Lovable.

## 🚀 Преимущества

- ✅ Hot-swap промптов без передеплоя
- ✅ Версионирование и откат изменений
- ✅ A/B тестирование промптов
- ✅ Аналитика эффективности
- ✅ Роли и права доступа
- ✅ Шаблоны и переменные
- ✅ Автоматическое обновление кэша

## 📈 Аналитика

- Время обработки по промптам
- Процент успешных анализов
- Уровень уверенности
- Частота ошибок
- Сравнение версий

## 🔄 Workflow

1. **Создание промпта** → Admin панель
2. **Тестирование** → A/B тест на части трафика
3. **Активация** → Установка как default
4. **Мониторинг** → Аналитика эффективности
5. **Оптимизация** → Итерации на основе данных
