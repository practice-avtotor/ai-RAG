#!/usr/bin/env python3
import argparse
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.config import RAGConfig
from rag.index_builder import IndexBuilder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Build FAISS index for glossary")
    parser.add_argument(
        "--force", 
        action="store_true", 
        help="Force rebuild even if index exists"
    )
    args = parser.parse_args()

    config = RAGConfig()
    builder = IndexBuilder(config)

    if not args.force and builder.index_exists():
        logger.info("Index already exists. Use --force to rebuild.")
        return

    builder.build_index()
    logger.info("Index built successfully!")


if __name__ == "__main__":
    main()
