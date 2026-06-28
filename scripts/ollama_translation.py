import pandas as pd
import json
import os
import time
import re
from tqdm import tqdm
from openai import OpenAI

INPUT_CSV = "merged.csv"
OUTPUT_JSON = "glossary_output.json"
BATCH_SIZE = 5
MODEL_NAME = "qwen2.5:7b"  # Или "mistral:7b-instruct"

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

# ==========================================
# PROMPT TEMPLATE
# ==========================================
SYSTEM_PROMPT = """You are an expert patent translator specializing in mechanical engineering, thermal systems, and industrial equipment.

TASK: For each patent title provided, output a JSON object with:
- "chinese": professional Chinese translation using standard technical terminology
- "russian": professional Russian translation using standard GOST/technical terminology
- "english": cleaned-up English title (fix typos, normalize terminology)
- "category": specific technical category in English (e.g., "heat exchangers", "pumps", "combustion engines", "solar energy")
- "context": 1-sentence Russian explanation of what the device/system does

CRITICAL RULES:
1. Translate TECHNICAL TERMS accurately — "seal" = уплотнение (NOT рыба/селедка), "heat exchanger" = теплообменник
2. Do NOT transliterate — translate meaning
3. Use proper engineering terminology in all 3 languages
4. Output ONLY the JSON array, no markdown, no explanations

Example:
Input: "SEAL FOR AN EXCHANGER OF HEAT"
Output: [
  {
    "chinese": "换热器密封装置",
    "russian": "Уплотнение теплообменника",
    "english": "Seal for a Heat Exchanger",
    "category": "heat exchangers",
    "context": "Устройство для герметизации соединений в теплообменном аппарате."
  }
]"""

def extract_json_from_response(text):
    """Извлекает JSON из ответа модели"""
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    text = text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(text)
    except:
        return None

def process_batch(batch_titles):
    titles_str = "\n".join([f"- {title}" for title in batch_titles])
    user_prompt = f"Process these patent titles into JSON format:\n{titles_str}"

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                extra_body={"num_ctx": 4096}
            )
            content = response.choices[0].message.content
            result = extract_json_from_response(content)
            if result:
                return result
        except Exception as e:
            print(f"\n⚠️ Attempt {attempt+1} failed: {e}")
            time.sleep(2 ** attempt)

    return None

def main():
    if not os.path.exists(INPUT_CSV):
        print(f"❌ {INPUT_CSV} not found!")
        return

    df = pd.read_csv(INPUT_CSV)
    titles = df['title'].dropna().tolist()  # Убрал .unique() — дубликаты оставляем
    print(f"📊 Всего названий: {len(titles)}")

    # Загружаем прогресс
    if os.path.exists(OUTPUT_JSON):
        try:
            with open(OUTPUT_JSON, 'r', encoding='utf-8') as f:
                glossary = json.load(f)
        except:
            glossary = []
    else:
        glossary = []

    print(f"✅ Уже обработано: {len(glossary)}")
    print(f"⏳ Осталось: {len(titles) - len(glossary)}\n")

    if len(glossary) >= len(titles):
        print("🎉 Всё готово!")
        return

    # Продолжаем с того места, где остановились
    start_index = len(glossary)
    remaining_titles = titles[start_index:]

    for i in tqdm(range(0, len(remaining_titles), BATCH_SIZE), desc="Генерация глоссария"):
        batch = remaining_titles[i:i + BATCH_SIZE]
        result = process_batch(batch)

        if result:
            glossary.extend(result)
            with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
                json.dump(glossary, f, ensure_ascii=False, indent=2)
        else:
            print(f"\n❌ Ошибка на батче {i}")

        time.sleep(1)

    print(f"\n🎉 Готово! Глоссарий сохранён в {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
