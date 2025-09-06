"""
FastAPI сервис для анализа сайтов
Интеграция с Supabase и адаптация существующей логики
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
# import jwt  # Временно отключено
# from playwright.async_api import async_playwright  # Временно отключено

# Добавляем отладочную информацию
print("Starting AI Researcher Console API...")
try:
    print(f"Python path: {sys.path}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Files in current directory: {os.listdir('.')}")
except Exception as e:
    print(f"Debug info error: {e}")

# Добавляем путь к исходному коду  
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/src')

# Временно отключаем сложные импорты для тестирования
# from src.pipelines.classification_pipeline import EnhancedPipeline
# from src.analyzers.ai_analyzer import MultiStageAnalyzer
# from src.scrapers.content_scraper import smart_fetch_content
# import config.settings as config
# from prompt_manager import initialize_prompt_manager, get_prompt_manager

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# FastAPI приложение
app = FastAPI(
    title="AI Researcher Console API",
    description="API для анализа и классификации веб-сайтов",
    version="1.0.0"
)

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене ограничить доменами
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Безопасность
security = HTTPBearer()

# Модели данных
class AnalysisRequest(BaseModel):
    domain: str = Field(..., description="Домен для анализа")
    url: str = Field(..., description="URL для анализа")
    profile_type: str = Field(..., description="Тип профиля для анализа")

class AnalysisResponse(BaseModel):
    domain: str
    classification: str
    confidence: float
    comment: str
    processing_time: float
    raw_data: Dict[str, Any]

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str

# Глобальные переменные
# pipelines: Dict[str, EnhancedPipeline] = {}
# browser_context = None

# Инициализация (временно отключена)
# async def initialize_pipelines():
#     """Инициализация пайплайнов для всех профилей"""
#     global pipelines
#     
#     profiles = [
#         'software', 'iso', 'telemedicine', 'pharma', 'edtech', 'marketing',
#         'fintech', 'healthtech', 'elearning', 'software_products',
#         'salesforce_partner', 'hubspot_partner', 'aws', 'shopify',
#         'ai_companies', 'mobile_app', 'recruiting', 'banking', 'platforms'
#     ]
#     
#     for profile in profiles:
#         try:
#             pipelines[profile] = EnhancedPipeline(profile=profile)
#             logger.info(f"Initialized pipeline for profile: {profile}")
#         except Exception as e:
#             logger.error(f"Failed to initialize pipeline for {profile}: {e}")

# async def initialize_browser():
#     """Инициализация браузера"""
#     global browser_context
#     
#     try:
#         playwright = await async_playwright().start()
#         browser = await playwright.chromium.launch(
#             headless=True,
#             args=['--disable-dev-shm-usage', '--no-sandbox']
#         )
#         browser_context = await browser.new_context(
#             user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
#         )
#         logger.info("Browser initialized successfully")
#     except Exception as e:
#         logger.error(f"Failed to initialize browser: {e}")
#         raise

# Зависимости (временно отключены)
# async def get_pipeline(profile_type: str) -> EnhancedPipeline:
#     """Получение пайплайна для указанного профиля"""
#     if profile_type not in pipelines:
#         raise HTTPException(status_code=400, detail=f"Unsupported profile type: {profile_type}")
#     return pipelines[profile_type]

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Верификация JWT токена (временно отключена)"""
    # Временно возвращаем заглушку
    return {"user_id": "test", "role": "admin"}

# API endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Проверка состояния сервиса"""
    try:
        # Проверяем доступность основных компонентов
        status = "healthy"
        
        # Проверка переменных окружения
        required_env_vars = ["GOOGLE_API_KEY"]
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        
        if missing_vars:
            status = "degraded"
            logger.warning(f"Missing environment variables: {missing_vars}")
        
        return HealthResponse(
            status=status,
            timestamp=datetime.now().isoformat(),
            version="1.0.0"
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now().isoformat(),
            version="1.0.0"
        )

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_website(
    request: AnalysisRequest,
    token_data: Dict[str, Any] = Depends(verify_token)
    # pipeline: EnhancedPipeline = Depends(get_pipeline)  # Временно отключено
):
    """Анализ одного веб-сайта (временно отключен)"""
    
    # Временно возвращаем заглушку
    return AnalysisResponse(
        domain=request.domain,
        classification="Service temporarily unavailable",
        confidence=0.0,
        comment="Analysis service is being initialized",
        processing_time=0.0,
        raw_data={"status": "initializing"}
    )

@app.post("/analyze-batch")
async def analyze_batch(
    requests: list[AnalysisRequest],
    background_tasks: BackgroundTasks,
    token_data: Dict[str, Any] = Depends(verify_token)
):
    """Анализ батча веб-сайтов (асинхронно)"""
    
    if len(requests) > 100:  # Лимит на размер батча
        raise HTTPException(status_code=400, detail="Batch size too large (max 100)")
    
    # Запуск анализа в фоне
    background_tasks.add_task(process_batch_analysis, requests, token_data)
    
    return {
        "message": f"Batch analysis started for {len(requests)} websites",
        "batch_id": f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    }

async def process_batch_analysis(requests: list[AnalysisRequest], token_data: Dict[str, Any]):
    """Обработка батча анализов в фоне (временно отключена)"""
    
    logger.info(f"Batch analysis requested for {len(requests)} websites")
    logger.info("Batch processing temporarily disabled - returning mock results")
    
    # Временная заглушка
    results = []
    errors = []
    
    for request in requests:
        # Мок результат
        results.append({
            "domain": request.domain,
            "result": {
                "classification": "Service temporarily unavailable",
                "confidence": 0.0,
                "comment": "Batch processing is being initialized",
                "processing_time": 0.0
            }
        })
    
    logger.info(f"Mock batch analysis completed: {len(results)} processed")
    return {"results": results, "errors": errors}

@app.get("/profiles")
async def get_available_profiles():
    """Получение списка доступных профилей"""
    return {
        "profiles": ["software", "fintech", "edtech", "healthtech"],
        "descriptions": {
            "software": "Программные продукты и SaaS решения",
            "fintech": "Финансовые технологии",
            "edtech": "Образовательные технологии",
            "healthtech": "Медицинские технологии"
        },
        "status": "Service temporarily in minimal mode"
    }

@app.get("/prompts")
async def get_prompts(
    profile_type: str = None,
    prompt_type: str = None,
    token_data: Dict[str, Any] = Depends(verify_token)
):
    """Получение списка промптов (временно отключено)"""
    
    return {"prompts": [], "status": "Service temporarily unavailable"}

@app.post("/prompts")
async def create_prompt(
    prompt_data: Dict[str, Any],
    token_data: Dict[str, Any] = Depends(verify_token)
):
    """Создание нового промпта (временно отключено)"""
    
    return {"status": "Service temporarily unavailable"}

@app.put("/prompts/{prompt_id}")
async def update_prompt(
    prompt_id: str,
    update_data: Dict[str, Any],
    token_data: Dict[str, Any] = Depends(verify_token)
):
    """Обновление промпта (временно отключено)"""
    
    return {"status": "Service temporarily unavailable"}

@app.post("/prompts/{prompt_id}/set-default")
async def set_default_prompt(
    prompt_id: str,
    token_data: Dict[str, Any] = Depends(verify_token)
):
    """Установка промпта как активного по умолчанию (временно отключено)"""
    
    return {"status": "Service temporarily unavailable"}

# События приложения
@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    try:
        logger.info("Starting AI Researcher Console API...")
        
        # Проверка критических переменных окружения
        port = os.getenv("PORT", "8000")
        environment = os.getenv("ENVIRONMENT", "development")
        
        logger.info(f"Environment: {environment}")
        logger.info(f"Port: {port}")
        
        # Проверка наличия Google API ключей
        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key:
            logger.info("Google API key found")
        else:
            logger.warning("Google API key not found - some features will be disabled")
        
        logger.info("API initialized successfully (minimal mode)")
        print("✅ API startup completed successfully")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        print(f"❌ API startup failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Очистка при завершении"""
    logger.info("Shutting down AI Researcher Console API...")

# Запуск сервера
if __name__ == "__main__":
    try:
        port = int(os.getenv("PORT", 8000))
        host = os.getenv("HOST", "0.0.0.0")
        environment = os.getenv("ENVIRONMENT", "development")
        
        print(f"🚀 Starting AI Researcher Console API")
        print(f"   Host: {host}")
        print(f"   Port: {port}")
        print(f"   Environment: {environment}")
        print(f"   Working Directory: {os.getcwd()}")
        
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=environment == "development",
            log_level="info"
        )
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        import traceback
        traceback.print_exc()
        raise
