from dataclasses import dataclass
from typing import List, Optional

@dataclass
class GlossaryEntry:
    """
    Представляет собой одно слово из автомобильного глоссария.
    """
    chinese: str
    russian: str
    english: str
    category: str
    context: str = ""

    def to_dict(self) -> dict:
        return {
            "chinese": self.chinese,
            "russian": self.russian,
            "english": self.english,
            "category": self.category,
            "context": self.context,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GlossaryEntry":
        return cls(
            chinese=data["chinese"],
            russian=data["russian"],
            english=data.get("english", ""),
            category=data.get("category", "general"),
            context=data.get("context", ""),
        )

class RetrievalResult:
    """Результат операции поиска с оценкой сходства."""
    
    def __init__(self, entry: GlossaryEntry, similarity: float):
        self.entry = entry
        self.similarity = similarity

    def to_dict(self) -> dict:
        data = self.entry.to_dict()
        data["similarity"] = float(self.similarity)
        return data