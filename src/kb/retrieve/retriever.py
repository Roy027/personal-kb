from typing import List, Tuple
from sentence_transformers import CrossEncoder
from src.kb.index.vector_store import VectorStore, Embedder
from src.kb.schema import Document

class Reranker:
    """Uses a Cross-Encoder to rerank documents."""
    def __init__(self, model_name: str = "BAAI/bge-reranker-large"):
        self.model = CrossEncoder(model_name)
        
    def rerank(self, query: str, documents: List[Document], top_n: int = 3) -> List[Document]:
        if not documents:
            return []
            
        # Prepare pairs for Cross-Encoder
        pairs = [[query, doc.content] for doc in documents]
        
        # Predict scores
        scores = self.model.predict(pairs)
        
        # Combine docs with scores
        doc_scores = list(zip(documents, scores))
        
        # Sort by score descending
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Store score in metadata for debugging/reference
        results = []
        for doc, score in doc_scores[:top_n]:
            doc.metadata["rerank_score"] = float(score)
            results.append(doc)
            
        return results

class Retriever:
    """Orchestrates retrieval and reranking."""
    def __init__(self, embedder: Embedder, vector_store: VectorStore, reranker: Reranker = None):
        self.embedder = embedder
        self.vector_store = vector_store
        self.reranker = reranker
        
    def retrieve(self, query: str, top_k: int = 10, top_n: int = 3, use_rerank: bool = True, file_filters: List[str] = None) -> List[Document]:
        # 1. Vector Search (Recall)
        # If filters are present, fetch more candidates to allow for post-filtering
        search_k = top_k * 5 if file_filters is not None else top_k
        
        query_emb = self.embedder.embed_query(query)
        initial_results = self.vector_store.search(query_emb, top_k=search_k)
        
        # Apply Logic Filter
        if file_filters is not None:
            import os
            filtered_results = []
            for doc in initial_results:
                # Compare basenames
                doc_name = os.path.basename(doc.metadata.get("source", ""))
                if doc_name in file_filters:
                    filtered_results.append(doc)
            
            # Trim back to requested top_k
            initial_results = filtered_results[:top_k]
        
        if not use_rerank or not self.reranker or not initial_results:
            return initial_results[:top_n]
            
        # 2. Reranking (Precision)
        reranked_results = self.reranker.rerank(query, initial_results, top_n=top_n)
        
        return reranked_results
