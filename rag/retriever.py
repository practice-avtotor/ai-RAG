import logging
from pathlib import Path
from typing import List, Optional

import faiss
import numpy as np

from .config import RAGConfig
from .embedder import Embedder
from .index_builder import IndexBuilder
from .models import GlossaryEntry, RetrievalResult

logger = logging.getLogger(__name__)

class Retriever:
    """
    Основной класс для поиска соответствующих терминов из глоссария.
    """
    def __init__(self, config: Optional[RAGConfig] = None):
        self.config = config or RAGConfig()
        self.embedder = Embedder(self.config)
        
        self.index, self.metadata = IndexBuilder.load_index_and_metadata(
            self.config.index_file, self.config.metadata_file
        )
        logger.info(f"Retriever initialized with {self.index.ntotal} entries")
    
    def retrieve(
        self, 
        text: str, 
        top_k: Optional[int] = None, 
        min_similarity: Optional[float] = None
    ) -> List[RetrievalResult]:
        if not text or not text.strip():
            return []
        
        top_k = top_k or self.config.default_top_k
        min_similarity = min_similarity or self.config.min_similarity
        
        query_embedding = self.embedder.encode(text)
        
        distances, indices = self.index.search(
            query_embedding.reshape(1, -1), top_k
        )
        
        results: List[RetrievalResult] = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            similarity = float(dist)
            if similarity < min_similarity:
                continue
            
            meta = self.metadata[idx]
            entry = GlossaryEntry.from_dict(meta)
            results.append(RetrievalResult(entry, similarity))
        
        return results
    
    def retrieve_as_dicts(self, text: str, **kwargs) -> List[dict]:
        return [r.to_dict() for r in self.retrieve(text, **kwargs)]