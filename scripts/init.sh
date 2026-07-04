#!/bin/bash
set -e

echo "Инициализация Patent Translator"

echo ""
echo "Ожидание запуска Ollama..."
until curl -s http://ollama:11434/api/tags > /dev/null 2>&1; do
    echo "   Ожидание Ollama..."
    sleep 2
done
echo "Ollama готов"

MODEL_NAME=${LLM_MODEL:-qwen2.5:7b}
echo ""
echo "Проверка модели: $MODEL_NAME"

if curl -s http://ollama:11434/api/tags | grep -q "\"$MODEL_NAME\""; then
    echo "Модель $MODEL_NAME уже загружена"
else
    echo "📥 Скачивание модели $MODEL_NAME"
    curl -X POST http://ollama:11434/api/pull -d "{\"name\": \"$MODEL_NAME\"}" | grep -q "success" && echo "✅ Модель $MODEL_NAME загружена"
fi

echo ""
echo "Проверка глоссария..."

GLOSSARY_PATH=${GLOSSARY_PATH:-data/merged_glossary.jsonl}

if [ ! -f "$GLOSSARY_PATH" ]; then
    echo "   Глоссарий не найден: $GLOSSARY_PATH"
    echo "   Убедись, что файл существует и путь правильный"
    exit 1
fi
echo "Глоссарий найден: $GLOSSARY_PATH"

echo ""
echo "Проверка индекса FAISS..."

if [ -f "data/faiss.index" ] && [ -f "data/metadata.pkl" ]; then
    echo "Индекс FAISS уже существует"
else
    echo "Построение индекса FAISS..."
    PYTHONPATH=/app python scripts/build_index.py --force
    echo "Индекс построен"
fi

echo ""
echo ""
echo "   Запуск Patent Translator API..."
echo "   http://0.0.0.0:8000"
echo "   Docs: http://0.0.0.0:8000/docs"

exec uvicorn main:app --host 0.0.0.0 --port 8000
