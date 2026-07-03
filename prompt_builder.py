from typing import Dict, List

SYSTEM_PROMPT = """
You are a patent translation expert.

You MUST return ONLY valid JSON. No explanations, no markdown, no extra text.

Example input: "SEAL FOR AN EXCHANGER OF HEAT"
Example output: {"russian": "Уплотнение теплообменника", "chinese": "换热器密封装置", "english": "Seal for a Heat Exchanger", "category": "heat exchangers", "context": "Устройство для герметизации соединений"}

Now translate this title into Russian, Chinese, clean English, category, and context. Return ONLY JSON.
"""


class PromptBuilder:
    """Строит промпты для LLM"""

    @classmethod
    def build(cls, text: str, examples: List[Dict]) -> str:
        """Строит полный промпт с примерами из RAG"""
        parts = [
            f'Title: "{text}"',
            "",
            cls._format_examples(examples),
            "",
            "Return ONLY JSON:",
        ]

        return "\n".join(parts)

    @classmethod
    def _format_examples(cls, examples: List[Dict]) -> str:
        """Форматирует примеры из RAG"""
        if not examples:
            return "(No similar terms found in glossary.)"

        lines = ["Similar terms from glossary:"]
        lines.append("")

        for i, ex in enumerate(examples[:2], 1):  # только 2 примера
            lines.extend(
                [
                    f"{i}. {ex.get('english', '')}",
                    f"   RU: {ex.get('russian', '')}",
                    f"   CN: {ex.get('chinese', '')}",
                    f"   Category: {ex.get('category', '')}",
                    "",
                ]
            )

        return "\n".join(lines)
