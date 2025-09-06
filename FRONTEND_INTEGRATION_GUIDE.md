# Frontend Integration Guide

## 🚀 Быстрый старт

### 1. Установка зависимостей
```bash
cd frontend
npm install
```

### 2. Настройка переменных окружения
Создайте файл `.env` в папке `frontend/`:
```bash
cp env.example .env
```

Отредактируйте `.env`:
```env
# API Configuration
VITE_API_BASE_URL=https://ai-researcher-console-production.up.railway.app

# Supabase Configuration
VITE_SUPABASE_URL=https://vuznvbjsimejtoppzppv.supabase.co
VITE_SUPABASE_ANON_KEY=your_actual_anon_key_here

# Development
VITE_DEV_MODE=false
VITE_MOCK_API=false
```

### 3. Запуск в режиме разработки
```bash
npm run dev
```

## 🔧 Интеграция с бэкендом

### Переключение между Mock и Real API

**Mock режим (для разработки):**
```env
VITE_MOCK_API=true
VITE_DEV_MODE=true
```

**Real API режим (для продакшена):**
```env
VITE_MOCK_API=false
VITE_DEV_MODE=false
```

### Использование API хуков

```typescript
// В компонентах используйте хуки вместо прямых вызовов API
import { useAnalysisResults, useAnalyzeUrl, useBatchSessions } from '../hooks/useApi';

function MyComponent() {
  const { data: results, isLoading } = useAnalysisResults(userId);
  const analyzeMutation = useAnalyzeUrl();
  
  const handleAnalyze = () => {
    analyzeMutation.mutate({ url: 'https://example.com', profileType: 'software' });
  };
  
  return (
    <div>
      {isLoading ? 'Loading...' : results?.map(result => ...)}
      <button onClick={handleAnalyze}>Analyze</button>
    </div>
  );
}
```

## 🔐 Аутентификация

### Настройка Supabase Auth
```typescript
import { useAuth } from '../hooks/useAuth';

function LoginPage() {
  const { signIn, signUp, user, loading, error } = useAuth();
  
  const handleLogin = async (email: string, password: string) => {
    try {
      await signIn(email, password);
      // Redirect to dashboard
    } catch (error) {
      console.error('Login failed:', error);
    }
  };
  
  return (
    <form onSubmit={handleLogin}>
      {/* Login form */}
    </form>
  );
}
```

### Защищенные маршруты
```typescript
import { useAuth } from '../hooks/useAuth';
import { Navigate } from 'react-router-dom';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  
  if (loading) return <div>Loading...</div>;
  if (!user) return <Navigate to="/login" />;
  
  return <>{children}</>;
}
```

## 📊 Работа с данными

### Анализ результатов
```typescript
// Получение результатов анализа
const { data: results, isLoading, error } = useAnalysisResults(userId, {
  profile_type: 'software',
  limit: 10
});

// Создание нового анализа
const analyzeMutation = useAnalyzeUrl();
const handleAnalyze = (url: string, profileType: string) => {
  analyzeMutation.mutate({ url, profileType });
};
```

### Батч анализ
```typescript
// Получение сессий
const { data: sessions } = useBatchSessions(userId);

// Создание батч анализа
const batchMutation = useAnalyzeBatch();
const handleBatchAnalyze = (requests: Array<{url: string, profile_type: string}>) => {
  batchMutation.mutate(requests);
};
```

## 🎨 Темы и стили

### Переключение темы
```typescript
import { useTheme } from 'next-themes';

function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  
  return (
    <button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}>
      {theme === 'dark' ? '☀️' : '🌙'}
    </button>
  );
}
```

## 🚀 Деплой

### Сборка для продакшена
```bash
npm run build
```

### Переменные окружения для продакшена
```env
VITE_API_BASE_URL=https://ai-researcher-console-production.up.railway.app
VITE_SUPABASE_URL=https://vuznvbjsimejtoppzppv.supabase.co
VITE_SUPABASE_ANON_KEY=your_production_anon_key
VITE_MOCK_API=false
VITE_DEV_MODE=false
```

## 🔍 Отладка

### Проверка подключения к API
```typescript
import { useHealth } from '../hooks/useApi';

function HealthCheck() {
  const { data: health, isLoading, error } = useHealth();
  
  return (
    <div>
      {isLoading && 'Checking health...'}
      {error && `Error: ${error.message}`}
      {health && `Status: ${health.status}`}
    </div>
  );
}
```

### Логирование запросов
```typescript
// В api.ts добавьте логирование
private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  console.log(`API Request: ${options.method || 'GET'} ${endpoint}`);
  // ... rest of the method
}
```

## 📝 Следующие шаги

1. **Настройте переменные окружения** с реальными ключами
2. **Протестируйте аутентификацию** - создайте пользователя в Supabase
3. **Проверьте API подключение** - убедитесь что бэкенд отвечает
4. **Замените mock данные** на реальные вызовы в компонентах
5. **Настройте деплой** на Vercel/Netlify

## 🆘 Решение проблем

### Ошибка CORS
- Убедитесь что `CORS_ORIGINS` в бэкенде включает ваш домен
- Проверьте что фронт и бэк используют правильные URL

### Ошибки аутентификации
- Проверьте Supabase ключи
- Убедитесь что пользователь существует в Supabase
- Проверьте RLS политики в Supabase

### API не отвечает
- Проверьте Railway деплой
- Убедитесь что `/health` эндпоинт работает
- Проверьте логи в Railway dashboard
