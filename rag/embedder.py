import logging
import torch
from pathlib import Path
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer

from .config import RAGConfig

logger = logging.getLogger(__name__)

class Embedder:
    """
    Обрабатывает векторизацию текста с использованием SentenceTransformer.
    """
    
    def __init__(self, config: RAGConfig):
        self.config = config
        self.model: SentenceTransformer = self._load_model()
    
    def _load_model(self) -> SentenceTransformer:
        device = self.config.device or ("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Loading embedding model on {device}")
        
        model = SentenceTransformer(
            self.config.embedding_model_name,
            device=device,
        )
        model.eval()
        return model
    
    def encode(self, text: str) -> np.ndarray:
        return self.encode_batch([text])[0]
    
    def encode_batch(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.array([], dtype=np.float32)
        
        with torch.no_grad():
            embeddings = self.model.encode(
                texts,
                batch_size=self.config.batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )
        return embeddings.astype(np.float32)
    
    def save_embeddings(self, embeddings: np.ndarray, path: Path):
        np.save(path, embeddings)
        logger.info(f"Saved embeddings to {path}")