-- Схема для управления промптами в продакшене
-- Добавить к основной схеме базы данных

-- Таблица промптов
CREATE TABLE public.prompts (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    profile_type TEXT NOT NULL CHECK (profile_type IN (
        'software', 'iso', 'telemedicine', 'pharma', 'edtech', 'marketing',
        'fintech', 'healthtech', 'elearning', 'software_products',
        'salesforce_partner', 'hubspot_partner', 'aws', 'shopify',
        'ai_companies', 'mobile_app', 'recruiting', 'banking', 'platforms'
    )),
    prompt_type TEXT NOT NULL CHECK (prompt_type IN ('extraction', 'classification')),
    version INTEGER NOT NULL DEFAULT 1,
    content TEXT NOT NULL,
    variables JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    is_default BOOLEAN DEFAULT false,
    performance_score DECIMAL(5,2),
    usage_count INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2),
    avg_processing_time DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES public.profiles(id)
);

-- Таблица версий промптов
CREATE TABLE public.prompt_versions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    prompt_id UUID REFERENCES public.prompts(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    content TEXT NOT NULL,
    change_log TEXT,
    performance_metrics JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES public.profiles(id),
    UNIQUE(prompt_id, version)
);

-- Таблица аналитики промптов
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

-- Таблица A/B тестов промптов
CREATE TABLE public.prompt_experiments (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    profile_type TEXT NOT NULL,
    prompt_type TEXT NOT NULL,
    control_prompt_id UUID REFERENCES public.prompts(id),
    variant_prompt_id UUID REFERENCES public.prompts(id),
    traffic_split DECIMAL(3,2) DEFAULT 0.5, -- 0.5 = 50/50 split
    is_active BOOLEAN DEFAULT false,
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    results JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES public.profiles(id)
);

-- Таблица шаблонов промптов
CREATE TABLE public.prompt_templates (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    template_content TEXT NOT NULL,
    variables JSONB NOT NULL DEFAULT '{}',
    category TEXT,
    is_public BOOLEAN DEFAULT false,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES public.profiles(id)
);

-- Индексы для производительности
CREATE INDEX idx_prompts_profile_type ON public.prompts(profile_type);
CREATE INDEX idx_prompts_prompt_type ON public.prompts(prompt_type);
CREATE INDEX idx_prompts_is_active ON public.prompts(is_active);
CREATE INDEX idx_prompts_is_default ON public.prompts(is_default);
CREATE INDEX idx_prompt_versions_prompt_id ON public.prompt_versions(prompt_id);
CREATE INDEX idx_prompt_analytics_prompt_id ON public.prompt_analytics(prompt_id);
CREATE INDEX idx_prompt_analytics_created_at ON public.prompt_analytics(created_at);
CREATE INDEX idx_prompt_experiments_is_active ON public.prompt_experiments(is_active);

-- RLS политики
ALTER TABLE public.prompts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.prompt_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.prompt_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.prompt_experiments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.prompt_templates ENABLE ROW LEVEL SECURITY;

-- Политики для prompts
CREATE POLICY "Admins can manage all prompts" ON public.prompts
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.profiles 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

CREATE POLICY "Users can view active prompts" ON public.prompts
    FOR SELECT USING (is_active = true);

-- Политики для prompt_versions
CREATE POLICY "Admins can manage prompt versions" ON public.prompt_versions
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.profiles 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Политики для prompt_analytics
CREATE POLICY "Admins can view all analytics" ON public.prompt_analytics
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.profiles 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Политики для prompt_experiments
CREATE POLICY "Admins can manage experiments" ON public.prompt_experiments
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.profiles 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Политики для prompt_templates
CREATE POLICY "Users can view public templates" ON public.prompt_templates
    FOR SELECT USING (is_public = true);

CREATE POLICY "Admins can manage all templates" ON public.prompt_templates
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.profiles 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Функция для автоматического создания версии при обновлении промпта
CREATE OR REPLACE FUNCTION public.create_prompt_version()
RETURNS TRIGGER AS $$
BEGIN
    -- Создаем новую версию при изменении контента
    IF OLD.content IS DISTINCT FROM NEW.content THEN
        INSERT INTO public.prompt_versions (prompt_id, version, content, change_log, created_by)
        VALUES (
            NEW.id,
            NEW.version,
            OLD.content,
            'Auto-created version on update',
            NEW.created_by
        );
        
        -- Увеличиваем версию
        NEW.version = OLD.version + 1;
    END IF;
    
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Триггер для автоматического создания версий
CREATE TRIGGER create_prompt_version_trigger
    BEFORE UPDATE ON public.prompts
    FOR EACH ROW EXECUTE FUNCTION public.create_prompt_version();

-- Функция для обновления статистики промпта
CREATE OR REPLACE FUNCTION public.update_prompt_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- Обновляем статистику промпта при добавлении аналитики
    UPDATE public.prompts 
    SET 
        usage_count = usage_count + 1,
        success_rate = (
            SELECT ROUND(
                (COUNT(*) FILTER (WHERE success = true)::DECIMAL / COUNT(*)) * 100, 2
            )
            FROM public.prompt_analytics 
            WHERE prompt_id = NEW.prompt_id
        ),
        avg_processing_time = (
            SELECT ROUND(AVG(processing_time), 2)
            FROM public.prompt_analytics 
            WHERE prompt_id = NEW.prompt_id AND processing_time IS NOT NULL
        )
    WHERE id = NEW.prompt_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Триггер для обновления статистики
CREATE TRIGGER update_prompt_stats_trigger
    AFTER INSERT ON public.prompt_analytics
    FOR EACH ROW EXECUTE FUNCTION public.update_prompt_stats();

-- Функция для получения активного промпта
CREATE OR REPLACE FUNCTION public.get_active_prompt(
    p_profile_type TEXT,
    p_prompt_type TEXT
)
RETURNS TABLE (
    id UUID,
    name TEXT,
    content TEXT,
    variables JSONB,
    version INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.name,
        p.content,
        p.variables,
        p.version
    FROM public.prompts p
    WHERE p.profile_type = p_profile_type
        AND p.prompt_type = p_prompt_type
        AND p.is_active = true
        AND p.is_default = true
    ORDER BY p.updated_at DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Вставка базовых промптов из существующего кода
-- (Эти данные нужно будет заполнить из ваших существующих промптов)

-- Пример для software профиля
INSERT INTO public.prompts (name, profile_type, prompt_type, content, is_default, is_active) VALUES
('software_extraction_v1', 'software', 'extraction', 'Extract information about software company...', true, true),
('software_classification_v1', 'software', 'classification', 'Classify software company based on...', true, true);

-- Пример для edtech профиля  
INSERT INTO public.prompts (name, profile_type, prompt_type, content, is_default, is_active) VALUES
('edtech_extraction_v1', 'edtech', 'extraction', 'Extract information about EdTech company...', true, true),
('edtech_classification_v1', 'edtech', 'classification', 'Classify EdTech company based on...', true, true);
