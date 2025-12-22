import os
import argparse
from typing import List
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
        print(f"Loading {file_path}...")
        return LOADERS[ext](file_path)
    else:
        print(f"Skipping unsupported file: {file_path}")
        return []

def main():
    parser = argparse.ArgumentParser(description="Ingest documents into the vector store.")
    parser.add_argument("--data-dir", type=str, default="./data/raw", help="Directory containing documents.")
    parser.add_argument("--index-path", type=str, default="./data/index", help="Path to save the index.")
    parser.add_argument("--reset", action="store_true", help="Reset the index before ingesting.")
    
    args = parser.parse_args()
    
    # Initialize components
    chunker = Chunker()
    embedder, store = get_retriever(index_path=args.index_path)
    
    if args.reset:
        print("Resetting index...")
        # Basic reset: delete files or just re-init store (VectorStore load fails safely if no file)
        # For strict reset we'd delete the files, but VectorStore overwrite on save handles it mostly if we don't load first
        # Implement explicit clear if needed, for now assuming overwrite behavior or manual deletion 
        # Actually VectorStore constructor loads existing. To reset we should probably clear metadata/index
        store.index = None
        store.metadata = []
        
    documents = []
    
    # Walk directory
    if os.path.exists(args.data_dir):
        for root, _, files in os.walk(args.data_dir):
            for file in files:
                file_path = os.path.join(root, file)
                docs = load_document(file_path)
                documents.extend(docs)
    else:
        print(f"Data directory {args.data_dir} does not exist.")
        return

    if not documents:
        print("No documents found to ingest.")
        return

    print(f"Loaded {len(documents)} raw documents/pages.")
    
    # Chunking
    print("Chunking...", end=" ", flush=True)
    chunked_docs = chunker.split_documents(documents)
    print(f"Generated {len(chunked_docs)} chunks.")
    
    # Embedding
    print("Embedding...", end=" ", flush=True)
    embeddings = embedder.embed_documents(chunked_docs)
    print("Done.")
    
    # Indexing
    print("Indexing...", end=" ", flush=True)
    store.add_documents(chunked_docs, embeddings)
    store.save()
    print("Saved index.")

if __name__ == "__main__":
    main()
