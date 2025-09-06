# 🔐 Создание пользователя lgchernukha@gmail.com через Dashboard

## 📋 **Инструкции:**

### 1. **Откройте Supabase Dashboard**
- Перейдите: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv

### 2. **Откройте SQL Editor**
- В левом меню выберите **SQL Editor**
- Нажмите **New Query**

### 3. **Выполните SQL скрипт**
Скопируйте и выполните следующий код:

```sql
-- Создание пользователя lgchernukha@gmail.com
INSERT INTO auth.users (
    instance_id,
    id,
    aud,
    role,
    email,
    encrypted_password,
    email_confirmed_at,
    recovery_sent_at,
    last_sign_in_at,
    raw_app_meta_data,
    raw_user_meta_data,
    created_at,
    updated_at,
    confirmation_token,
    email_change,
    email_change_token_new,
    recovery_token
) VALUES (
    '00000000-0000-0000-0000-000000000000',
    gen_random_uuid(),
    'authenticated',
    'authenticated',
    'lgchernukha@gmail.com',
    crypt('200815462Cv!', gen_salt('bf')),
    NOW(),
    NULL,
    NULL,
    '{"provider": "email", "providers": ["email"]}',
    '{"full_name": "Vadim Chernukha"}',
    NOW(),
    NOW(),
    '',
    '',
    '',
    ''
);

-- Создание профиля для пользователя
INSERT INTO public.profiles (
    id,
    email,
    full_name,
    role,
    credits,
    subscription_plan
) VALUES (
    (SELECT id FROM auth.users WHERE email = 'lgchernukha@gmail.com'),
    'lgchernukha@gmail.com',
    'Vadim Chernukha',
    'user',
    100,
    'free'
);

-- Проверка создания
SELECT 
    p.id,
    p.email,
    p.full_name,
    p.role,
    p.credits,
    p.subscription_plan,
    p.created_at
FROM public.profiles p
WHERE p.email = 'lgchernukha@gmail.com';
```

### 4. **Нажмите Run**
- Нажмите кнопку **Run** для выполнения скрипта

## ✅ **Результат:**

После успешного выполнения вы увидите:
```
✅ Пользователь создан
📧 Email: lgchernukha@gmail.com
🔑 Пароль: 200815462Cv!
💳 Кредиты: 100
👑 Роль: user
```

## 🎯 **Готово!**

Пользователь будет создан и готов к использованию в системе AI Researcher Console! 🎉

## 🔗 **Полезные ссылки:**

- **Supabase Dashboard**: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv
- **SQL Editor**: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/sql
- **Authentication**: https://supabase.com/dashboard/project/vuznvbjsimejtoppzppv/auth/users
