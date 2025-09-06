# Интеграция с Lovable для Frontend

Этот документ содержит всю необходимую информацию для создания frontend интерфейса в Lovable.

## 🔗 API Endpoints

### Базовый URL
```
https://your-project-ref.supabase.co/functions/v1
```

### Аутентификация
Все запросы требуют JWT токен в заголовке:
```javascript
headers: {
  'Authorization': `Bearer ${jwtToken}`,
  'Content-Type': 'application/json'
}
```

## 📊 API Endpoints

### 1. Анализ одного сайта
```javascript
POST /analyze-website

// Request
{
  "domain": "example.com",
  "url": "https://example.com", 
  "profile_type": "software"
}

// Response
{
  "id": "uuid",
  "domain": "example.com",
  "classification": "Software Lead",
  "confidence": 85.5,
  "comment": "Компания разрабатывает SaaS платформу...",
  "processing_time": 12.3,
  "credits_used": 1
}
```

### 2. Создание сессии анализа
```javascript
POST /create-session

// Request
{
  "name": "My Analysis Session",
  "profile_type": "software",
  "domains": ["example.com", "test.com", "demo.com"]
}

// Response
{
  "session_id": "uuid",
  "total_domains": 3,
  "estimated_credits": 3,
  "message": "Session created successfully. 3 credits will be used."
}
```

### 3. Обработка сессии
```javascript
POST /process-session

// Request
{
  "session_id": "uuid"
}

// Response
{
  "session_id": "uuid",
  "status": "processing",
  "message": "Started processing 3 domains",
  "total_domains": 3,
  "processed_domains": 0
}
```

## 🗄️ Supabase Client

### Инициализация
```javascript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://your-project-ref.supabase.co'
const supabaseKey = 'your-anon-key'

export const supabase = createClient(supabaseUrl, supabaseKey)
```

### Аутентификация
```javascript
// Регистрация
const { data, error } = await supabase.auth.signUp({
  email: 'user@example.com',
  password: 'password123'
})

// Вход
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'password123'
})

// Выход
await supabase.auth.signOut()

// Получение текущего пользователя
const { data: { user } } = await supabase.auth.getUser()
```

## 📋 Таблицы базы данных

### profiles
```javascript
{
  id: "uuid",
  email: "user@example.com",
  full_name: "John Doe",
  role: "user", // "admin" | "user"
  credits: 100,
  subscription_plan: "free", // "free" | "basic" | "pro" | "business"
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z"
}
```

### analyses
```javascript
{
  id: "uuid",
  user_id: "uuid",
  domain: "example.com",
  url: "https://example.com",
  profile_type: "software",
  status: "completed", // "pending" | "processing" | "completed" | "failed"
  result_classification: "Software Lead",
  result_confidence: 85.5,
  result_comment: "Компания разрабатывает SaaS...",
  processing_time_seconds: 12.3,
  credits_used: 1,
  raw_data: { /* полные данные анализа */ },
  error_message: null,
  created_at: "2024-01-01T00:00:00Z",
  completed_at: "2024-01-01T00:00:10Z"
}
```

### analysis_sessions
```javascript
{
  id: "uuid",
  user_id: "uuid",
  name: "My Analysis Session",
  profile_type: "software",
  total_domains: 10,
  processed_domains: 8,
  successful_analyses: 7,
  failed_analyses: 1,
  status: "processing", // "pending" | "processing" | "completed" | "failed" | "cancelled"
  credits_used: 8,
  created_at: "2024-01-01T00:00:00Z",
  started_at: "2024-01-01T00:00:05Z",
  completed_at: null
}
```

### credit_transactions
```javascript
{
  id: "uuid",
  user_id: "uuid",
  amount: -1, // отрицательное для списания, положительное для пополнения
  transaction_type: "usage", // "purchase" | "usage" | "bonus" | "refund"
  description: "Analysis of example.com",
  analysis_id: "uuid",
  created_at: "2024-01-01T00:00:00Z"
}
```

## 🎨 UI Компоненты

### 1. Dashboard
- Показ баланса кредитов
- Статистика анализов
- Последние результаты
- Быстрый анализ

### 2. Анализ сайта
- Форма ввода URL/домена
- Выбор профиля анализа
- Кнопка "Анализировать"
- Показ результата

### 3. Батчевый анализ
- Загрузка CSV файла
- Выбор профиля
- Создание сессии
- Мониторинг прогресса

### 4. История анализов
- Таблица с результатами
- Фильтры по дате/профилю
- Экспорт результатов
- Детальный просмотр

### 5. Управление кредитами
- Покупка кредитов
- История транзакций
- Тарифные планы

### 6. Админ панель (только для админов)
- Управление пользователями
- Статистика системы
- Управление кредитами

## 💳 Тарифные планы

```javascript
const subscriptionPlans = [
  {
    name: "free",
    price: 0,
    credits: 100,
    description: "Бесплатный план - 100 анализов"
  },
  {
    name: "basic", 
    price: 10,
    credits: 1000,
    description: "Базовый план - 1000 анализов за $10"
  },
  {
    name: "pro",
    price: 30, 
    credits: 10000,
    description: "Профессиональный план - 10000 анализов за $30"
  },
  {
    name: "business",
    price: 99,
    credits: 50000, 
    description: "Бизнес план - 50000 анализов за $99"
  }
]
```

## 🔍 Профили анализа

```javascript
const analysisProfiles = [
  { value: "software", label: "Программные продукты и SaaS" },
  { value: "iso", label: "Компании с ISO сертификацией" },
  { value: "telemedicine", label: "Телемедицинские сервисы" },
  { value: "pharma", label: "Фармацевтические компании" },
  { value: "edtech", label: "Образовательные технологии" },
  { value: "marketing", label: "Маркетинговые агентства" },
  { value: "fintech", label: "Финансовые технологии" },
  { value: "healthtech", label: "Медицинские технологии" },
  { value: "elearning", label: "Онлайн обучение" },
  { value: "software_products", label: "Продуктовые IT компании" },
  { value: "salesforce_partner", label: "Партнеры Salesforce" },
  { value: "hubspot_partner", label: "Партнеры HubSpot" },
  { value: "aws", label: "Партнеры AWS" },
  { value: "shopify", label: "Партнеры Shopify" },
  { value: "ai_companies", label: "AI компании" },
  { value: "mobile_app", label: "Мобильные приложения" },
  { value: "recruiting", label: "Рекрутинговые агентства" },
  { value: "banking", label: "Банковские услуги" },
  { value: "platforms", label: "IT платформы" }
]
```

## 🚀 Примеры кода

### Анализ одного сайта
```javascript
const analyzeWebsite = async (domain, url, profileType) => {
  const { data: { session } } = await supabase.auth.getSession()
  
  if (!session) {
    throw new Error('Not authenticated')
  }

  const response = await fetch(`${supabaseUrl}/functions/v1/analyze-website`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${session.access_token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      domain,
      url,
      profile_type: profileType
    })
  })

  if (!response.ok) {
    throw new Error('Analysis failed')
  }

  return await response.json()
}
```

### Создание сессии анализа
```javascript
const createAnalysisSession = async (name, profileType, domains) => {
  const { data: { session } } = await supabase.auth.getSession()
  
  const response = await fetch(`${supabaseUrl}/functions/v1/create-session`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${session.access_token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name,
      profile_type: profileType,
      domains
    })
  })

  return await response.json()
}
```

### Получение истории анализов
```javascript
const getAnalysisHistory = async (limit = 50) => {
  const { data, error } = await supabase
    .from('analyses')
    .select('*')
    .order('created_at', { ascending: false })
    .limit(limit)

  if (error) throw error
  return data
}
```

### Получение профиля пользователя
```javascript
const getUserProfile = async () => {
  const { data: { user } } = await supabase.auth.getUser()
  
  if (!user) return null

  const { data, error } = await supabase
    .from('profiles')
    .select('*')
    .eq('id', user.id)
    .single()

  if (error) throw error
  return data
}
```

## 🎯 Рекомендуемый UX Flow

1. **Регистрация/Вход** → Dashboard
2. **Dashboard** → Показ кредитов + быстрый анализ
3. **Анализ сайта** → Ввод URL → Выбор профиля → Результат
4. **Батчевый анализ** → Загрузка CSV → Создание сессии → Мониторинг
5. **История** → Просмотр результатов → Экспорт
6. **Кредиты** → Покупка → История транзакций

## 🔐 Безопасность

- Все API вызовы требуют аутентификации
- RLS политики защищают данные пользователей
- Админ функции доступны только пользователям с ролью "admin"
- Валидация всех входных данных

## 📱 Responsive Design

- Мобильная версия для анализа на ходу
- Адаптивные таблицы для истории
- Touch-friendly интерфейс
- Оптимизация для планшетов

## 🎨 Дизайн система

- Современный минималистичный дизайн
- Профессиональная цветовая схема
- Четкая типографика
- Интуитивная навигация
- Быстрая обратная связь (loading states, success/error messages)
