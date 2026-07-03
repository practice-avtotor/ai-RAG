import os
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Config:
    """Глобальная конфигурация сервиса"""

    data_dir: Path = Path("data")
    glossary_file: Path = Path("data/merged_glossary.jsonl")

    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    model_name: str = os.getenv("LLM_MODEL", "qwen2.5:7b")

    default_top_k: int = 5
    min_similarity: float = 0.75

    cache_size: int = 1000

    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))

    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    def __post_init__(self):
        self.data_dir.mkdir(parents=True, exist_ok=True)


config = Config()
