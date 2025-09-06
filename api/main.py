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
import time
import json
import httpx
from bs4 import BeautifulSoup
import google.generativeai as genai
from supabase import create_client, Client
from collections import defaultdict, deque
from fastapi.responses import PlainTextResponse
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

# CORS настройки (через ENV CORS_ORIGINS="https://app.example.com,https://admin.example.com")
_cors_env = os.getenv("CORS_ORIGINS", "").strip()
_cors_list = [o.strip() for o in _cors_env.split(",") if o.strip()] if _cors_env else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting (per IP + path)
_rate_buckets: Dict[str, deque] = defaultdict(deque)
RATE_LIMIT_MAX = int(os.getenv("RATE_LIMIT_MAX", "60"))
RATE_LIMIT_WINDOW_SEC = int(os.getenv("RATE_LIMIT_WINDOW_SEC", "60"))

@app.middleware("http")
async def rate_limit(request, call_next):
    now = time.time()
    try:
        ip = request.client.host if request.client else "unknown"
        key = f"{ip}:{request.url.path}"
        bucket = _rate_buckets[key]
        # prune old
        while bucket and now - bucket[0] > RATE_LIMIT_WINDOW_SEC:
            bucket.popleft()
        if len(bucket) >= RATE_LIMIT_MAX:
            return PlainTextResponse("Too Many Requests", status_code=429)
        bucket.append(now)
    except Exception:
        pass
    return await call_next(request)

# Простое логирование запросов/ответов
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        duration_ms = int((time.time() - start_time) * 1000)
        logger.info(
            "HTTP %s %s -> %s in %dms",
            request.method,
            request.url.path,
            getattr(response, "status_code", "-"),
            duration_ms,
        )
        return response
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        logger.error(
            "HTTP %s %s -> ERROR %s in %dms",
            request.method,
            request.url.path,
            str(e),
            duration_ms,
        )
        raise

# Безопасность
security = HTTPBearer()

# Supabase client (optional)
supabase_client: Optional[Client] = None

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

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Верификация JWT токена через Supabase Auth.

    Требует ENV: SUPABASE_URL, SUPABASE_ANON_KEY (или SERVICE_KEY)
    В non-production режиме при отсутствии ENV — допускает заглушку.
    """
    token = credentials.credentials if credentials else None
    if not token:
        raise HTTPException(status_code=401, detail="Missing authorization token")

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_api_key = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
    environment = os.getenv("ENVIRONMENT", "development").lower()

    if not supabase_url or not supabase_api_key:
        if environment == "production":
            raise HTTPException(status_code=500, detail="Auth not configured")
        logger.warning("Supabase auth env not set, using stub auth (non-production)")
        return {"user_id": "dev-user", "role": "admin"}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(
                f"{supabase_url.rstrip('/')}/auth/v1/user",
                headers={
                    "apikey": supabase_api_key,
                    "Authorization": f"Bearer {token}",
                },
            )
            if res.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid or expired token")
            user = res.json() or {}
            user_id = user.get("id")
            role = "user"

            # Пытаемся получить роль из profiles
            try:
                if supabase_client and user_id:
                    prof = supabase_client.table("profiles").select("role").eq("id", user_id).limit(1).execute()
                    if getattr(prof, "data", None):
                        role = (prof.data[0] or {}).get("role", role)
            except Exception as e:
                logger.warning(f"Fetch profile role failed: {e}")

            return {"user_id": user_id, "role": role}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auth verification error: {e}")
        raise HTTPException(status_code=500, detail="Auth service error")


def _get_page_text(url: str, timeout_seconds: float = 10.0) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
    }
    with httpx.Client(follow_redirects=True, timeout=timeout_seconds) as client:
        r = client.get(url, headers=headers)
        r.raise_for_status()
        html = r.text
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript", "iframe"]):
        tag.decompose()
    text = soup.get_text(" ", strip=True)
    return text[:6000]


def _get_gemini_model():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is not set")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        model_name="gemini-1.5-flash-latest",
        generation_config={"temperature": 0.1, "response_mime_type": "application/json"},
    )

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

async def _run_minimal_analysis(url: str, domain: str, profile_type: str) -> Dict[str, Any]:
    """Общий минимальный анализ: возвращает словарь с полями для AnalysisResponse."""
    started = time.time()

    if not url.startswith("http"):
        url = f"https://{url}"

    # 1) Получение текста страницы
    page_text = await asyncio.to_thread(_get_page_text, url)
    if not page_text or len(page_text) < 50:
        raise HTTPException(status_code=422, detail="Insufficient page content")

    # 2) Классификация через Gemini (простая схема Match/No Match)
    model = await asyncio.to_thread(_get_gemini_model)
    prompt = (
        "You are a business analyst. Decide if this website represents a software product/company "
        "relevant to B2B software profiles. Return strict JSON with fields: reasoning, classification, final_output.\n\n"
        f"Content:\n{page_text[:4000]}\n\n"
        "Rules: classification is either 'Match' or 'No Match'. final_output must be either '+ Relevant - Software Lead' or '- Not Relevant'."
    )

    resp = await model.generate_content_async(prompt)
    raw_text = (resp.text or "").strip()
    parsed = None
    try:
        parsed = json.loads(raw_text)
    except Exception:
        if "{" in raw_text and "}" in raw_text:
            candidate = raw_text[raw_text.find("{") : raw_text.rfind("}") + 1]
            try:
                parsed = json.loads(candidate)
            except Exception:
                parsed = None

    if not parsed or not isinstance(parsed, dict):
        parsed = {
            "reasoning": "Fallback: could not parse structured response",
            "classification": "No Match",
            "final_output": "- Not Relevant",
        }

    classification = str(parsed.get("classification", "No Match")).strip()
    final_output = str(parsed.get("final_output", "- Not Relevant")).strip()
    reasoning = str(parsed.get("reasoning", "")).strip()
    took = time.time() - started

    result = {
        "domain": domain,
        "classification": final_output if classification == "Match" else "Not Relevant",
        "confidence": 70.0 if classification == "Match" else 30.0,
        "comment": reasoning or "Minimal Gemini classification",
        "processing_time": took,
        "raw_data": {"gemini": parsed},
        "_url": url,
        "_match": classification == "Match",
    }
    return result


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_website(
    request: AnalysisRequest,
    token_data: Dict[str, Any] = Depends(verify_token),
):
    """Минимальный анализ сайта: httpx + BeautifulSoup + Gemini классификация."""

    try:
        r = await _run_minimal_analysis(request.url, request.domain, request.profile_type)
        response_obj = AnalysisResponse(
            domain=r["domain"],
            classification=r["classification"],
            confidence=r["confidence"],
            comment=r["comment"],
            processing_time=r["processing_time"],
            raw_data=r["raw_data"],
        )

        # Save to Supabase if configured (best-effort)
        try:
            if supabase_client:
                payload = {
                    "user_id": token_data.get("user_id"),
                    "domain": request.domain,
                    "url": r["_url"],
                    "profile_type": request.profile_type,
                    "status": "completed",
                    "result_classification": response_obj.classification,
                    "result_confidence": response_obj.confidence,
                    "result_comment": response_obj.comment,
                    "processing_time_seconds": round(response_obj.processing_time, 2),
                    "raw_data": response_obj.raw_data,
                }
                supabase_client.table("analyses").insert(payload).execute()
        except Exception as e:
            logger.warning(f"Supabase save failed: {e}")

        return response_obj

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analyze error for {request.url}: {e}")
        took = 0.0
        response_obj = AnalysisResponse(
            domain=request.domain,
            classification="Service temporarily unavailable",
            confidence=0.0,
            comment=str(e),
            processing_time=took,
            raw_data={"error": str(e)},
        )

        # Attempt to store failed analysis too
        try:
            if supabase_client:
                payload = {
                    "user_id": token_data.get("user_id"),
                    "domain": request.domain,
                    "url": request.url,
                    "profile_type": request.profile_type,
                    "status": "failed",
                    "error_message": str(e),
                    "raw_data": response_obj.raw_data,
                }
                supabase_client.table("analyses").insert(payload).execute()
        except Exception as se:
            logger.warning(f"Supabase save (failed case) error: {se}")

        return response_obj

@app.post("/analyze-batch")
async def analyze_batch(
    requests: list[AnalysisRequest],
    background_tasks: BackgroundTasks,
    token_data: Dict[str, Any] = Depends(verify_token),
):
    """Анализ батча сайтов: создает сессию (Supabase) и запускает фоновой процесс."""

    if len(requests) > 100:
        raise HTTPException(status_code=400, detail="Batch size too large (max 100)")

    session_id = None
    try:
        if supabase_client:
            # Создаем сессию
            name = f"session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            profile_type = requests[0].profile_type if requests else "software"
            insert_res = supabase_client.table("analysis_sessions").insert({
                "user_id": token_data.get("user_id"),
                "name": name,
                "profile_type": profile_type,
                "total_domains": len(requests),
                "status": "processing",
                "started_at": datetime.now().isoformat(),
            }).execute()
            session_id = (insert_res.data or [{}])[0].get("id")

            # Добавляем домены
            rows = [{
                "session_id": session_id,
                "domain": r.domain,
                "url": r.url,
                "status": "pending",
            } for r in requests]
            supabase_client.table("session_domains").insert(rows).execute()
    except Exception as e:
        logger.warning(f"Supabase session init failed: {e}")

    # Запуск фона
    background_tasks.add_task(process_batch_analysis, requests, token_data, session_id)

    return {
        "message": f"Batch analysis started for {len(requests)} websites",
        "session_id": session_id,
    }

async def process_batch_analysis(
    requests: list[AnalysisRequest],
    token_data: Dict[str, Any],
    session_id: Optional[str] = None,
):
    """Обработка батча: параллельный минимальный анализ + сохранение в Supabase."""

    logger.info(f"Batch analysis started: {len(requests)} websites, session={session_id}")
    semaphore = asyncio.Semaphore(5)
    results = []
    errors = []

    async def worker(req: AnalysisRequest):
        async with semaphore:
            try:
                r = await _run_minimal_analysis(req.url, req.domain, req.profile_type)

                # Save to analyses
                analysis_id = None
                try:
                    if supabase_client:
                        payload = {
                            "user_id": token_data.get("user_id"),
                            "domain": req.domain,
                            "url": r["_url"],
                            "profile_type": req.profile_type,
                            "status": "completed",
                            "result_classification": r["classification"],
                            "result_confidence": r["confidence"],
                            "result_comment": r["comment"],
                            "processing_time_seconds": round(r["processing_time"], 2),
                            "raw_data": r["raw_data"],
                        }
                        ins = supabase_client.table("analyses").insert(payload).execute()
                        analysis_id = (ins.data or [{}])[0].get("id")
                        if session_id:
                            # update session_domains
                            supabase_client.table("session_domains").update({
                                "status": "completed",
                                "analysis_id": analysis_id,
                            }).eq("session_id", session_id).eq("domain", req.domain).execute()
                except Exception as se:
                    logger.warning(f"Supabase save in batch failed: {se}")

                results.append({"domain": req.domain, "analysis_id": analysis_id, "result": r})
            except Exception as e:
                errors.append({"domain": req.domain, "error": str(e)})
                try:
                    if supabase_client and session_id:
                        supabase_client.table("session_domains").update({
                            "status": "failed",
                        }).eq("session_id", session_id).eq("domain", req.domain).execute()
                except Exception:
                    pass

    await asyncio.gather(*(worker(r) for r in requests))

    # finalize session
    try:
        if supabase_client and session_id:
            supabase_client.table("analysis_sessions").update({
                "processed_domains": len(results) + len(errors),
                "successful_analyses": len(results),
                "failed_analyses": len(errors),
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
            }).eq("id", session_id).execute()
    except Exception as e:
        logger.warning(f"Supabase finalize session failed: {e}")

    logger.info(f"Batch analysis finished: {len(results)} ok, {len(errors)} failed")
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
    """Прокси к Edge Function manage-prompts (GET). Требуется admin."""
    if token_data.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    supabase_url = os.getenv("SUPABASE_URL")
    if not supabase_url:
        raise HTTPException(status_code=500, detail="Supabase not configured")

    headers = {
        "Content-Type": "application/json",
        # Передаем исходный токен; если недоступен, fallback на service key
        "Authorization": f"Bearer {os.getenv('SUPABASE_SERVICE_KEY')}",
        "apikey": os.getenv("SUPABASE_SERVICE_KEY") or "",
    }
    params = {}
    if profile_type:
        params["profile_type"] = profile_type
    if prompt_type:
        params["prompt_type"] = prompt_type

    async with httpx.AsyncClient(timeout=float(os.getenv("SUPABASE_EDGE_TIMEOUT", "10"))) as client:
        resp = await client.get(f"{supabase_url.rstrip('/')}/functions/v1/manage-prompts", headers=headers, params=params)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json()

@app.post("/prompts")
async def create_prompt(
    prompt_data: Dict[str, Any],
    token_data: Dict[str, Any] = Depends(verify_token)
):
    """Создание промпта через Edge Function manage-prompts/create. Admin only."""
    if token_data.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    supabase_url = os.getenv("SUPABASE_URL")
    if not supabase_url:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('SUPABASE_SERVICE_KEY')}",
        "apikey": os.getenv("SUPABASE_SERVICE_KEY") or "",
    }
    async with httpx.AsyncClient(timeout=float(os.getenv("SUPABASE_EDGE_TIMEOUT", "10"))) as client:
        resp = await client.post(f"{supabase_url.rstrip('/')}/functions/v1/manage-prompts/create", headers=headers, json=prompt_data)
        if resp.status_code not in (200, 201):
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json()

@app.put("/prompts/{prompt_id}")
async def update_prompt(
    prompt_id: str,
    update_data: Dict[str, Any],
    token_data: Dict[str, Any] = Depends(verify_token)
):
    """Обновление промпта через Edge Function manage-prompts/update. Admin only."""
    if token_data.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    supabase_url = os.getenv("SUPABASE_URL")
    if not supabase_url:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('SUPABASE_SERVICE_KEY')}",
        "apikey": os.getenv("SUPABASE_SERVICE_KEY") or "",
    }
    payload = {"id": prompt_id, **update_data}
    async with httpx.AsyncClient(timeout=float(os.getenv("SUPABASE_EDGE_TIMEOUT", "10"))) as client:
        resp = await client.post(f"{supabase_url.rstrip('/')}/functions/v1/manage-prompts/update", headers=headers, json=payload)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json()

@app.post("/prompts/{prompt_id}/set-default")
async def set_default_prompt(
    prompt_id: str,
    token_data: Dict[str, Any] = Depends(verify_token)
):
    """Установка промпта по умолчанию через Edge Function manage-prompts/set-default. Admin only."""
    if token_data.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    supabase_url = os.getenv("SUPABASE_URL")
    if not supabase_url:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('SUPABASE_SERVICE_KEY')}",
        "apikey": os.getenv("SUPABASE_SERVICE_KEY") or "",
    }
    async with httpx.AsyncClient(timeout=float(os.getenv("SUPABASE_EDGE_TIMEOUT", "10"))) as client:
        resp = await client.post(f"{supabase_url.rstrip('/')}/functions/v1/manage-prompts/set-default", headers=headers, json={"id": prompt_id})
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json()

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
        
        # Проверка ключей/ENV
        google_key = os.getenv("GOOGLE_API_KEY")
        logger.info("Google API key: %s", "set" if google_key else "missing")

        # Проверка Supabase ENV
        supabase_url_present = bool(os.getenv("SUPABASE_URL"))
        supabase_key_present = bool(os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY"))
        logger.info("Supabase URL: %s, key: %s", "set" if supabase_url_present else "missing", "set" if supabase_key_present else "missing")
        
        # Инициализация Supabase при наличии ENV
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        if supabase_url and supabase_key:
            global supabase_client
            supabase_client = create_client(supabase_url, supabase_key)
            logger.info("Supabase client initialized")
        else:
            logger.info("Supabase env not set, skipping client init")

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
