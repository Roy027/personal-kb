import argparse
from src.kb.index.vector_store import get_retriever

def main():
    parser = argparse.ArgumentParser(description="Query the knowledge base.")
    parser.add_argument("query", type=str, help="The query string.")
    parser.add_argument("--index-path", type=str, default="./data/index", help="Path to the index.")
    parser.add_argument("--top-k", type=int, default=3, help="Number of results to return.")
    
    args = parser.parse_args()
    
    # Load index
    embedder, store = get_retriever(index_path=args.index_path)
    
    # Embed query
    query_emb = embedder.embed_query(args.query)
    
    # Search
    results = store.search(query_emb, top_k=args.top_k)
    
    # Display results
    print(f"\nQuery: {args.query}\n")
    if not results:
        print("No results found.")
    else:
        for i, doc in enumerate(results):
            print(f"--- Result {i+1} ---")
            print(f"Source: {doc.metadata.get('file_name', 'Unknown')}")
            print(f"Page/Chunk: {doc.metadata.get('page_number', 'N/A')} / {doc.metadata.get('chunk_index', 'N/A')}")
            print(f"Content:\n{doc.content.strip()[:500]}...") # Preview
            print("\n")

if __name__ == "__main__":
    main()
