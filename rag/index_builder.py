import logging
import pickle
from pathlib import Path
from typing import List, Tuple

import faiss

from .config import RAGConfig
from .embedder import Embedder
from .loader import GlossaryLoader

logger = logging.getLogger(__name__)

class IndexBuilder:
    """
    Строит индекс FAISS на основе записей глоссария.
    """
    
    def __init__(self, config: RAGConfig):
        self.config = config
        self.loader = GlossaryLoader(config)
        self.embedder = Embedder(config)
    
    def index_exists(self) -> bool:
        """Проверяет, существует ли индекс"""
        return self.config.index_file.exists() and self.config.metadata_file.exists()
    
    def build(self, force_rebuild: bool = False) -> None:
        if self.config.index_file.exists() and not force_rebuild:
            logger.info("Index already exists. Use --force to rebuild.")
            return
        
        entries = self.loader.load()
        if not entries:
            raise ValueError("No glossary entries to index.")
        
        texts = [entry.chinese for entry in entries]
        embeddings = self.embedder.encode_batch(texts)
        
        self.embedder.save_embeddings(embeddings, self.config.embeddings_file)
        
        logger.info("Building FAISS index...")
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings)
        
        faiss.write_index(index, str(self.config.index_file))
        logger.info(f"Saved FAISS index with {index.ntotal} vectors")
        
        metadata = [entry.to_dict() for entry in entries]
        with open(self.config.metadata_file, "wb") as f:
            pickle.dump(metadata, f)
        logger.info("Saved metadata")
    
    @staticmethod
    def load_index_and_metadata(index_path: Path, metadata_path: Path
                                ) -> Tuple[faiss.Index, List[dict]]:
        index = faiss.read_index(str(index_path))
        
        with open(metadata_path, "rb") as f:
            metadata = pickle.load(f)
        
        return index, metadata
