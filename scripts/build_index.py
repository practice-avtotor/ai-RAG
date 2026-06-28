#!/usr/bin/env python3
import argparse
import logging
import sys

from rag.config import RAGConfig
from rag.index_builder import IndexBuilder

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

def main():
    parser = argparse.ArgumentParser(description="Build RAG index")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    
    config = RAGConfig()
    try:
        builder = IndexBuilder(config)
        builder.build(force_rebuild=args.force)
        print("Index built successfully!")
    except Exception as e:
        logging.error(f"Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()