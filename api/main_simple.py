"""
Простая версия FastAPI сервиса для тестирования
"""

import os
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel

# FastAPI приложение
app = FastAPI(
    title="AI Researcher Console API",
    description="API для анализа и классификации веб-сайтов",
    version="1.0.0"
)

# Модели данных
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str

# API endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Проверка состояния сервиса"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )

@app.get("/")
async def root():
    """Корневой endpoint"""
    return {"message": "AI Researcher Console API is running!"}

@app.get("/test")
async def test():
    """Тестовый endpoint"""
    return {"message": "Test endpoint is working!"}

# Запуск сервера
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "main_simple:app",
        host=host,
        port=port,
        log_level="info"
    )
