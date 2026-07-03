import logging

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from config import config
from models import HealthResponse, StatsResponse, TranslateRequest, TranslateResponse
from translator import translator

logging.basicConfig(
    level=getattr(logging, config.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Patent Translator API",
    description="RAG-based patent translation with Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/", response_model=dict)
async def root():
    """Корневой эндпоинт"""
    return {
        "service": "Patent Translator",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "/translate": "POST - Translate patent title",
            "/translate_batch": "POST - Translate multiple titles",
            "/health": "GET - Service health",
            "/stats": "GET - Statistics",
            "/cache/clear": "POST - Clear cache",
        },
    }


@app.post("/translate", response_model=TranslateResponse)
async def translate(request: TranslateRequest):
    """
    Переводит один патентный заголовок.

    - `text`: заголовок патента на английском
    - `top_k`: количество примеров из RAG (по умолчанию 5)
    - `use_rag`: использовать RAG или нет (по умолчанию true)
    """
    try:
        result = translator.translate(
            text=request.text, top_k=request.top_k, use_rag=request.use_rag
        )
        return result

    except Exception as e:
        logger.error(f"Translation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/translate_batch", response_model=list[TranslateResponse])
async def translate_batch(texts: list[str], top_k: int = 5, use_rag: bool = True):
    """
    Переводит несколько заголовков за раз.

    - `texts`: список заголовков патентов на английском
    - `top_k`: количество примеров из RAG
    - `use_rag`: использовать RAG или нет
    """
    try:
        results = translator.translate_batch(texts, top_k, use_rag)
        return results

    except Exception as e:
        logger.error(f"Batch transfer error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health", response_model=HealthResponse)
async def health():
    """Проверка здоровья сервиса"""
    stats = translator.get_stats()

    return HealthResponse(
        status="ok",
        glossary_entries=stats["glossary_entries"],
        model_name=stats["model_name"],
        rag_available=stats["rag_available"],
    )


@app.get("/stats", response_model=StatsResponse)
async def stats():
    """Статистика кэша и RAG"""
    return translator.get_stats()


@app.post("/cache/clear")
async def clear_cache():
    """Очистка кэша"""
    translator.cache.clear()
    return JSONResponse(content={"status": "cache cleared"})


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.api_host,
        port=config.api_port,
        reload=True,
        log_level=config.log_level.lower(),
    )
