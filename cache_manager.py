import logging
from functools import lru_cache
from typing import Dict, Optional

from config import config

logger = logging.getLogger(__name__)


class TranslationCache:
    """LRU кэш для переводов"""

    def __init__(self, max_size: int = None):

        if max_size is None:
            max_size = config.cache_size

        self.max_size = max_size
        self._cache: Dict[str, dict] = {}
        self._hits = 0
        self._misses = 0
        logger.info(f"Cache initilazed (max_size={max_size})")

    def _get_key(self, text: str, top_k: int) -> str:
        """Генерирует ключ для кэша"""
        return f"{text.lower().strip()}|{top_k}"

    @lru_cache(maxsize=1000)
    def _get_cached(self, key: str) -> Optional[dict]:
        """
        lru_cache автоматически хранит до maxsize=1000 записей
        и удаляет самые старые при переполнении.
        """
        return self._cache.get(key)

    def get(self, text: str, top_k: int) -> Optional[dict]:
        """Получает перевод из кэша"""
        key = self._get_key(text, top_k)

        cached = self._get_cached(key)

        if cached is not None:
            self._hits += 1
            result = cached.copy()
            result["from_cache"] = True
            logger.info(f"Cache HIT: {text[:50]}...")
            return result

        self._misses += 1
        return None

    def set(self, text: str, top_k: int, result: dict) -> None:
        """Сохраняет перевод в кэш"""
        key = self._get_key(text, top_k)

        self._cache[key] = result

        # Очищаем lru_cache, чтобы он перестроился с новыми данными
        self._get_cached.cache_clear()

        # Если превысили размер, удаляем самую старую запись
        if len(self._cache) > self.max_size:
            first_key = next(iter(self._cache))
            del self._cache[first_key]
            logger.debug(f"Old record deleted: {first_key[:30]}...")

    def clear(self) -> None:
        """Очищает кэш"""
        self._cache.clear()
        self._get_cached.cache_clear()
        self._hits = 0
        self._misses = 0
        logger.info("Cache cleared")

    def get_stats(self) -> dict:
        """Возвращает статистику кэша"""
        total = self._hits + self._misses

        return {
            "cache_size": len(self._cache),
            "cache_hits": self._hits,
            "cache_misses": self._misses,
            "hit_ratio": self._hits / total if total > 0 else 0.0,
            "lru_cache_info": self._get_cached.cache_info()._asdict(),
        }
