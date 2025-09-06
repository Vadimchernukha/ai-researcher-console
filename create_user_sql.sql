-- Создание пользователя lgchernukha@gmail.com через SQL
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

-- 2. Создаем профиль для пользователя
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

-- 3. Проверяем, что пользователь создан
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
