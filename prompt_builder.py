import logging
from pathlib import Path
from typing import Dict, List

import yaml

logger = logging.getLogger(__name__)


DEFAULT_SYSTEM_PROMPT = """You are a patent translation expert.

You MUST return ONLY valid JSON. No explanations, no markdown, no extra text.

Example input: "SEAL FOR AN EXCHANGER OF HEAT"
Example output: {"russian": "Уплотнение теплообменника", "chinese": "换热器密封装置", "english": "Seal for a Heat Exchanger", "category": "heat exchangers", "context": "Устройство для герметизации соединений"}

Now translate this title into Russian, Chinese, clean English, category, and context. Return ONLY JSON."""


class PromptBuilder:
    """Строит промпты для LLM"""

    _system_prompt: str = None

    @classmethod
    def _load_system_prompt(cls) -> str:
        """
        Загружает SYSTEM_PROMPT:
        1. Из prompts.yaml (если есть и парсится)
        2. Иначе DEFAULT_SYSTEM_PROMPT
        """

        if cls._system_prompt is not None:
            return cls._system_prompt

        yaml_path = Path("prompts.yaml")

        if yaml_path.exists():
            try:
                with open(yaml_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)

                    if data and "system_prompt" in data:
                        prompt = data["system_prompt"].strip()

                        if prompt:
                            logger.info("SYSTEM_PROMPT loaded from prompts.yaml")
                            cls._system_prompt = prompt
                            return prompt

            except Exception as e:
                logger.warning(f"Error while loading prompts.yaml: {e}")

        logger.info("Using DEFAULT_SYSTEM_PROMPT")
        cls._system_prompt = DEFAULT_SYSTEM_PROMPT
        return cls._system_prompt

    @classmethod
    def get_system_prompt(cls) -> str:
        """Возвращает SYSTEM_PROMPT (с загрузкой при первом вызове)"""
        return cls._load_system_prompt()

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
        from config import config

        if not examples:
            return "(No similar terms found in glossary.)"

        lines = ["Similar terms from glossary:"]
        lines.append("")

        max_examples = config.rag_examples_in_prompt

        for i, ex in enumerate(examples[:max_examples], 1):
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


SYSTEM_PROMPT = PromptBuilder.get_system_prompt()
