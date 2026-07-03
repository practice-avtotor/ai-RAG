import json
import logging
import re
from typing import Dict, List, Optional

from openai import OpenAI

from cache_manager import TranslationCache
from config import config
from prompt_builder import SYSTEM_PROMPT, PromptBuilder
from rag.config import RAGConfig
from rag.retriever import Retriever

logger = logging.getLogger(__name__)


class PatentTranslator:
    """Основной класс переводчика"""

    def __init__(self):
        self.config = config

        self.retriever = None
        self.rag_available = False
        self._init_rag()

        self.llm = self._init_llm()

        self.cache = TranslationCache(max_size=self.config.cache_size)

        logger.info("The translator has been initialized")

    def _init_rag(self) -> None:
        """Инициализация RAG"""
        try:
            rag_config = RAGConfig()
            rag_config.glossary_file = self.config.glossary_file

            self.retriever = Retriever(rag_config)
            self.rag_available = True

            logger.info(f"RAG is loaded: {self.retriever.index.ntotal} записей")

        except Exception as e:
            logger.warning(f"RAG is not loaded: {e}")
            self.rag_available = False

    def _init_llm(self):
        """Инициализация Ollama"""
        try:
            client = OpenAI(base_url=self.config.ollama_base_url, api_key="ollama")
            logger.info(f"Ollama is connected: {self.config.ollama_base_url}")
            return client

        except Exception as e:
            logger.error(f"Cant connect to Ollama: {e}")
            raise

    def _extract_json(self, text: str) -> Optional[dict]:
        """Извлекает JSON из ответа модели"""
        try:
            match = re.search(r"\{.*\}", text, re.DOTALL)

            if match:
                return json.loads(match.group(0))

            return json.loads(text)

        except json.JSONDecodeError as e:
            logger.error(f"Error while parsing JSON: {e}")
            return None

    def _call_llm(self, prompt: str) -> dict:
        """Вызывает Ollama"""
        try:
            response = self.llm.chat.completions.create(
                model=self.config.model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                extra_body={"num_ctx": 2048}
            )
            
            content = response.choices[0].message.content
            
            # Пробуем найти JSON
            result = self._extract_json(content)
            if result:
                return result
            
            # Если JSON не найден = возвращаем заглушку
            logger.warning(f"No JSON found in: {content[:200]}")
            return self._get_fallback(content[:50])
            
        except Exception as e:
            logger.error(f"Error with LLM: {e}")
            return self._get_fallback(prompt[:50])

    def _get_fallback(self, text: str) -> dict:
        """Возвращает заглушку при ошибке"""
        return {
            "russian": text,
            "chinese": text,
            "english": text,
            "category": "unknown",
            "context": "Translation failed",
        }

    def _search_rag(self, text: str, top_k: int) -> List[Dict]:
        """Поиск в RAG"""
        if not self.rag_available or not self.retriever:
            return []

        try:
            results = self.retriever.retrieve(text, top_k=top_k)
            return [r.to_dict() for r in results]

        except Exception as e:
            logger.warning(f"Error with RAG: {e}")
            return []

    def translate(self, text: str, top_k: int = 5, use_rag: bool = True) -> dict:
        """
        Основной метод перевода
        """
        if not text or not text.strip():
            return {
                "russian": "",
                "chinese": "",
                "english": "",
                "category": "",
                "context": "",
                "from_cache": False,
                "rag_used": False,
                "rag_examples": [],
            }

        cached = self.cache.get(text, top_k)

        if cached:
            return cached

        logger.info(f"🔄 Перевод: {text[:50]}...")

        rag_examples = []
        rag_used = False

        if use_rag:
            rag_examples = self._search_rag(text, top_k)
            rag_used = True

            if rag_examples:
                logger.info(f"🔍 RAG найдено: {len(rag_examples)} примеров")

        prompt = PromptBuilder.build(text, rag_examples[:3])
        llm_result = self._call_llm(prompt)

        result = {
            "original": text,
            "russian": llm_result.get("russian", text),
            "chinese": llm_result.get("chinese", text),
            "english": llm_result.get("english", text),
            "category": llm_result.get("category", "unknown"),
            "context": llm_result.get("context", ""),
            "from_cache": False,
            "rag_used": rag_used,
            "rag_examples": rag_examples[:top_k],
        }

        self.cache.set(text, top_k, result)

        return result

    def translate_batch(self, texts: List[str], top_k: int = 5, 
                        use_rag: bool = True) -> List[dict]:
        """Переводит несколько текстов"""
        results = []

        for text in texts:
            result = self.translate(text, top_k, use_rag)
            results.append(result)

        return results

    def get_stats(self) -> dict:
        """Статистика"""
        cache_stats = self.cache.get_stats()

        return {
            **cache_stats,
            "glossary_entries": self.retriever.index.ntotal
            if self.rag_available
            else 0,
            "rag_available": self.rag_available,
            "model_name": self.config.model_name,
        }


translator = PatentTranslator()
