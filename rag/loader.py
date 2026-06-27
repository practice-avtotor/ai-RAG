import json
import logging
from pathlib import Path
from typing import List

from .models import GlossaryEntry
from .config import RAGConfig

logger = logging.getLogger(__name__)

class GlossaryLoader:
    """
    Загружает и проверяет глоссарий из файла JSONL.
    """
    
    def __init__(self, config: RAGConfig):
        self.config = config
    
    def load(self) -> List[GlossaryEntry]:
        if not self.config.glossary_file.exists():
            logger.error(f"Glossary file not found: {self.config.glossary_file}")
            raise FileNotFoundError(f"Glossary file not found: {self.config.glossary_file}")
        
        entries: List[GlossaryEntry] = []
        with open(self.config.glossary_file, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    entry = GlossaryEntry.from_dict(data)
                    entries.append(entry)
                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    logger.warning(f"Invalid entry at line {line_num}: {e}. Skipping.")
                    continue
        
        logger.info(f"Loaded {len(entries)} glossary entries")
        return entries