import os
import argparse
import sys

print("Loading libraries (this may take a few seconds)...", flush=True)

from typing import List
from tqdm import tqdm
from src.kb.ingestion.pdf_loader import load_pdf
from src.kb.ingestion.html_loader import load_html
from src.kb.chunking.chunker import Chunker
from src.kb.index.vector_store import get_retriever
from src.kb.schema import Document

# Supported extensions
LOADERS = {
    ".pdf": load_pdf,
    ".html": load_html,
    ".htm": load_html
}

def load_document(file_path: str) -> List[Document]:
    ext = os.path.splitext(file_path)[1].lower()
    if ext in LOADERS:
        # print(f"Loading {file_path}...") # Reduced noise
        return LOADERS[ext](file_path)
    else:
        # print(f"Skipping unsupported file: {file_path}")
        return []

def main():
    parser = argparse.ArgumentParser(description="Ingest documents into the vector store.")
    parser.add_argument("--data-dir", type=str, default="./data/raw", help="Directory containing documents.")
    parser.add_argument("--index-path", type=str, default="./data/index", help="Path to save the index.")
    parser.add_argument("--reset", action="store_true", help="Reset the index before ingesting.")
    parser.add_argument("--limit", type=int, default=None, help="Limit the number of documents to process (for testing).")
    parser.add_argument("--filename", type=str, default=None, help="Ingest a specific file only (by name).")
    
    args = parser.parse_args()
    
    # Initialize components
    print("Initializing components (downloading models if needed)...")
    chunker = Chunker()
    embedder, store = get_retriever(index_path=args.index_path)
    
    if args.reset:
        print("Resetting index...")
        store.index = None
        store.metadata = []
        
    documents = []
    
    # Walk directory
    if os.path.exists(args.data_dir):
        print("Scanning files...")
        file_list = []
        for root, _, files in os.walk(args.data_dir):
            for file in files:
                # Filter by filename if provided
                if args.filename and args.filename.lower() not in file.lower():
                    continue
                    
                file_list.append(os.path.join(root, file))
                
        if not file_list:
            if args.filename:
                print(f"File '{args.filename}' not found in {args.data_dir}.")
            else:
                print("No files found.")
            return

        print(f"Found {len(file_list)} files. Loading...")
        for file_path in tqdm(file_list, desc="Loading Files"):
            docs = load_document(file_path)
            documents.extend(docs)
            if args.limit and len(documents) >= args.limit:
                print(f"Reached limit of {args.limit} documents.")
                documents = documents[:args.limit]
                break
    else:
        print(f"Data directory {args.data_dir} does not exist.")
        return

    if not documents:
        print("No documents found to ingest.")
        return

    print(f"Loaded {len(documents)} raw documents/pages.")
    
    # Chunking
    print("Chunking...")
    chunked_docs = chunker.split_documents(documents)
    print(f"Generated {len(chunked_docs)} chunks.")
    
    # Embedding
    print("Embedding (on CPU)...")
    embeddings = embedder.embed_documents(chunked_docs)
    print("Done.")
    
    # Indexing
    print("Indexing...", end=" ", flush=True)
    store.add_documents(chunked_docs, embeddings)
    store.save()
    print("Saved index.")

if __name__ == "__main__":
    main()
