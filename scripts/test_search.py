#!/usr/bin/env python3
import argparse
import logging
import sys

from rag.config import RAGConfig
from rag.retriever import Retriever

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

def main():
    parser = argparse.ArgumentParser(description="Test RAG search")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--min-sim", type=float, default=0.7)
    parser.add_argument("--text", type=str)
    args = parser.parse_args()
    
    retriever = Retriever()
    
    if args.text:
        results = retriever.retrieve(args.text, top_k=args.top_k, min_similarity=args.min_sim)
        print_results(results)
    else:
        print("Interactive mode (type 'exit' to quit)")
        while True:
            text = input("\n请输入中文文本: ").strip()
            if text.lower() in ["exit", "quit", "выход"]:
                break
            if text:
                results = retriever.retrieve(text, top_k=args.top_k, min_similarity=args.min_sim)
                print_results(results)

def print_results(results):
    if not results:
        print("No results.")
        return
    for i, res in enumerate(results, 1):
        print(f"\n{i}. {res.entry.chinese} → {res.entry.russian} (score: {res.similarity:.4f})")

if __name__ == "__main__":
    main()