-- Создание админ пользователя для AI Researcher Console
-- Выполните этот скрипт в Supabase Dashboard > SQL Editor

-- 1. Создаем пользователя в auth.users
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
    'admin@example.com',
    crypt('admin123', gen_salt('bf')),
    NOW(),
    NULL,
    NULL,
    '{"provider": "email", "providers": ["email"]}',
    '{"full_name": "Admin User"}',
    NOW(),
    NOW(),
    '',
    '',
    '',
    ''
);

-- 2. Создаем профиль для админа
INSERT INTO public.profiles (
    id,
    email,
    full_name,
    role,
    credits,
    subscription_plan
) VALUES (
    (SELECT id FROM auth.users WHERE email = 'admin@example.com'),
    'admin@example.com',
    'Admin User',
    'admin',
    999999,
    'free'
);

-- 3. Проверяем, что админ создан
SELECT 
    p.id,
    p.email,
    p.full_name,
    p.role,
    p.credits,
    p.subscription_plan,
    p.created_at
FROM public.profiles p
WHERE p.email = 'admin@example.com';
