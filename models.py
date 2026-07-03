from typing import List, Optional

from pydantic import BaseModel


class TranslateRequest(BaseModel):
    """Запрос на перевод"""

    text: str
    top_k: Optional[int] = 5
    use_rag: Optional[bool] = True


class TranslateResponse(BaseModel):
    """Ответ на перевод"""

    original: str
    russian: str
    chinese: str
    english: str
    category: str
    context: str
    from_cache: bool
    rag_used: bool
    rag_examples: List[dict]


class HealthResponse(BaseModel):
    """Ответ на проверку здоровья"""

    status: str
    glossary_entries: int
    model_name: str
    rag_available: bool


class StatsResponse(BaseModel):
    """Статистика"""

    cache_size: int
    cache_hits: int
    cache_misses: int
    hit_ratio: float
    glossary_entries: int
    rag_available: bool
    model_name: str
