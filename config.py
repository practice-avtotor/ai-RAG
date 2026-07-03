import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Глобальная конфигурация сервиса"""

    # Ollama
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    model_name: str = os.getenv("LLM_MODEL", "qwen2.5:7b")

    # Настройки генерации
    llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.0"))
    llm_context_size: int = int(os.getenv("LLM_CONTEXT_SIZE", "2048"))

    # FastAPI
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # RAG
    rag_top_k: int = int(os.getenv("RAG_TOP_K", "5"))
    rag_min_similarity: float = float(os.getenv("RAG_MIN_SIMILARITY", "0.75"))

    # Кэш
    cache_size: int = int(os.getenv("CACHE_SIZE", "1000"))

    # Пути
    data_dir: Path = Path(os.getenv("DATA_DIR", "data"))
    glossary_file: Path = Path(os.getenv("GLOSSARY_PATH", "data/merged_glossary.jsonl"))

    def __post_init__(self):
        self.data_dir.mkdir(parents=True, exist_ok=True)


config = Config()
