-- Схема базы данных для AI Researcher Console
-- Создание таблиц для системы кредитов и анализа сайтов

-- Включаем расширения
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Таблица пользователей (расширяет auth.users)
CREATE TABLE public.profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('admin', 'user')),
    credits INTEGER NOT NULL DEFAULT 0,
    subscription_plan TEXT DEFAULT 'free' CHECK (subscription_plan IN ('free', 'basic', 'pro', 'business')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Таблица тарифных планов
CREATE TABLE public.subscription_plans (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    price_usd DECIMAL(10,2) NOT NULL,
    credits_included INTEGER NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Таблица транзакций кредитов
CREATE TABLE public.credit_transactions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    amount INTEGER NOT NULL, -- положительное для пополнения, отрицательное для списания
    transaction_type TEXT NOT NULL CHECK (transaction_type IN ('purchase', 'usage', 'bonus', 'refund')),
    description TEXT,
    analysis_id UUID REFERENCES public.analyses(id) ON DELETE SET NULL, -- для транзакций использования
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Таблица анализов сайтов
CREATE TABLE public.analyses (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    domain TEXT NOT NULL,
    url TEXT NOT NULL,
    profile_type TEXT NOT NULL CHECK (profile_type IN (
        'software', 'iso', 'telemedicine', 'pharma', 'edtech', 'marketing', 
        'fintech', 'healthtech', 'elearning', 'software_products', 
        'salesforce_partner', 'hubspot_partner', 'aws', 'shopify', 
        'ai_companies', 'mobile_app', 'recruiting', 'banking', 'platforms'
    )),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    result_classification TEXT,
    result_confidence DECIMAL(5,2),
    result_comment TEXT,
    processing_time_seconds DECIMAL(10,2),
    credits_used INTEGER DEFAULT 1,
    raw_data JSONB, -- полные данные анализа
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Таблица сессий анализа (для батчевой обработки)
CREATE TABLE public.analysis_sessions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    name TEXT NOT NULL,
    profile_type TEXT NOT NULL,
    total_domains INTEGER NOT NULL,
    processed_domains INTEGER DEFAULT 0,
    successful_analyses INTEGER DEFAULT 0,
    failed_analyses INTEGER DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')),
    credits_used INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Таблица доменов для сессий
CREATE TABLE public.session_domains (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    session_id UUID REFERENCES public.analysis_sessions(id) ON DELETE CASCADE NOT NULL,
    domain TEXT NOT NULL,
    url TEXT NOT NULL,
    analysis_id UUID REFERENCES public.analyses(id) ON DELETE SET NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Таблица системных настроек
CREATE TABLE public.system_settings (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    key TEXT NOT NULL UNIQUE,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Индексы для производительности
CREATE INDEX idx_profiles_email ON public.profiles(email);
CREATE INDEX idx_profiles_role ON public.profiles(role);
CREATE INDEX idx_analyses_user_id ON public.analyses(user_id);
CREATE INDEX idx_analyses_domain ON public.analyses(domain);
CREATE INDEX idx_analyses_status ON public.analyses(status);
CREATE INDEX idx_analyses_created_at ON public.analyses(created_at);
CREATE INDEX idx_credit_transactions_user_id ON public.credit_transactions(user_id);
CREATE INDEX idx_credit_transactions_created_at ON public.credit_transactions(created_at);
CREATE INDEX idx_analysis_sessions_user_id ON public.analysis_sessions(user_id);
CREATE INDEX idx_session_domains_session_id ON public.session_domains(session_id);

-- RLS (Row Level Security) политики
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.credit_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analysis_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.session_domains ENABLE ROW LEVEL SECURITY;

-- Политики для profiles
CREATE POLICY "Users can view own profile" ON public.profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Admins can view all profiles" ON public.profiles
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.profiles 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Политики для analyses
CREATE POLICY "Users can view own analyses" ON public.analyses
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create analyses" ON public.analyses
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Admins can view all analyses" ON public.analyses
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.profiles 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Политики для credit_transactions
CREATE POLICY "Users can view own transactions" ON public.credit_transactions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Admins can view all transactions" ON public.credit_transactions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.profiles 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Политики для analysis_sessions
CREATE POLICY "Users can view own sessions" ON public.analysis_sessions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create sessions" ON public.analysis_sessions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Admins can view all sessions" ON public.analysis_sessions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.profiles 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Политики для session_domains
CREATE POLICY "Users can view own session domains" ON public.session_domains
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.analysis_sessions 
            WHERE id = session_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create session domains" ON public.session_domains
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.analysis_sessions 
            WHERE id = session_id AND user_id = auth.uid()
        )
    );

-- Функция для автоматического создания профиля при регистрации
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name, role, credits, subscription_plan)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email),
        CASE 
            WHEN NEW.email = 'admin@example.com' THEN 'admin'
            ELSE 'user'
        END,
        CASE 
            WHEN NEW.email = 'admin@example.com' THEN 999999
            ELSE 100
        END,
        'free'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Триггер для автоматического создания профиля
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Функция для обновления updated_at
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Триггеры для обновления updated_at
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- Вставка тарифных планов
INSERT INTO public.subscription_plans (name, price_usd, credits_included, description) VALUES
('free', 0.00, 100, 'Бесплатный план - 100 анализов'),
('basic', 10.00, 1000, 'Базовый план - 1000 анализов за $10'),
('pro', 30.00, 10000, 'Профессиональный план - 10000 анализов за $30'),
('business', 99.00, 50000, 'Бизнес план - 50000 анализов за $99');

-- Вставка системных настроек
INSERT INTO public.system_settings (key, value, description) VALUES
('api_limits', '{"max_concurrent_requests": 5, "rate_limit_per_minute": 60}', 'Лимиты API'),
('analysis_settings', '{"max_domains_per_session": 1000, "timeout_seconds": 45}', 'Настройки анализа'),
('credit_settings', '{"credits_per_analysis": 1, "admin_unlimited": true}', 'Настройки кредитов');
