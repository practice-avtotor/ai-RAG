import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class RAGConfig:
    """
    Конфигурация для RAG системы.
    """
    # пути к данным
    data_dir: Path = Path("data")
    glossary_file: Path = Path("data/merged_glossary.jsonl")
    index_file: Path = Path("data/faiss.index")
    metadata_file: Path = Path("data/metadata.pkl")
    embeddings_file: Path = Path("data/embeddings.npy")
    
    # Настройки модели
    embedding_model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"
    device: Optional[str] = None
    
    # Настройки FAISS
    faiss_index_type: str = "IndexFlatIP"
    dimension: int = 384
    
    # Настройки извлечения (retrieval)
    default_top_k: int = 5
    min_similarity: float = 0.75
    
    # Представление
    batch_size: int = 32
    num_threads: int = 4
    
    def __post_init__(self):
        """Проверка путей и создание каталогов."""
        self.data_dir = Path(self.data_dir).absolute()
        self.glossary_file = Path(self.glossary_file).absolute()
        self.index_file = Path(self.index_file).absolute()
        self.metadata_file = Path(self.metadata_file).absolute()
        self.embeddings_file = Path(self.embeddings_file).absolute()
        
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_env(cls) -> "RAGConfig":
        return cls()