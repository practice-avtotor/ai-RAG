from typing import List, Dict

SYSTEM_PROMPT = """
You are a patent translation expert.

You MUST return ONLY valid JSON. No explanations, no markdown.

Output format:
{
    "russian": "translation in Russian",
    "chinese": "translation in Chinese",
    "english": "cleaned English title",
    "category": "category",
    "context": "brief context"
}

Translate this title:
"""

class PromptBuilder:
    """Строит промпты для LLM"""

    @classmethod
    def build(cls, text: str, examples: List[Dict]) -> str:
        """
        Строит полный промпт с примерами из RAG
        """
        parts = [
            f'Patent title to translate: "{text}"',
            "",
            cls._format_examples(examples),
            "",
            "Translate this title into Russian and Chinese. Return ONLY JSON."
        ]
        
        return "\n".join(parts)

    @classmethod
    def _format_examples(cls, examples: List[Dict]) -> str:
        """Форматирует примеры из RAG"""
        if not examples:
            return "(No similar terms found in the glossary.)"
        
        lines = ["Here are some similar terms from the glossary:"]
        lines.append("")
        
        for i, ex in enumerate(examples[:3], 1):
            lines.append(f"{i}. {ex.get('english', '')}")
            lines.append(f"   RU: {ex.get('russian', '')}")
            lines.append(f"   CN: {ex.get('chinese', '')}")
            lines.append(f"   Category: {ex.get('category', '')}")
            lines.append(f"   Context: {ex.get('context', '')}")
            lines.append("")
        
        return "\n".join(lines)
