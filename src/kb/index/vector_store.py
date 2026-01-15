import os
import faiss
import numpy as np
import pickle
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from src.kb.schema import Document

class Embedder:
    """Handles embedding generation."""
    
    def __init__(self, model_name: str = "BAAI/bge-m3"):
        self.model = SentenceTransformer(model_name)
        
    def embed_documents(self, documents: List[Document]) -> np.ndarray:
        texts = [doc.content for doc in documents]
        embeddings = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
        return np.array(embeddings)
        
    def embed_query(self, query: str) -> np.ndarray:
        return self.model.encode([query], normalize_embeddings=True)[0]

class VectorStore:
    """FAISS-based vector store."""
    
    def __init__(self, index_path: str = "./data/index"):
        self.index_path = index_path
        self.index_file = os.path.join(index_path, "index.faiss")
        self.metadata_file = os.path.join(index_path, "metadata.pkl")
        
        if not os.path.exists(index_path):
            os.makedirs(index_path)
            
        self.index = None
        self.metadata: List[Document] = []
        
        # Load existing index if available
        if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
            self.load()
            
    def add_documents(self, documents: List[Document], embeddings: np.ndarray):
        """Adds documents and their embeddings to the index."""
        dimension = embeddings.shape[1]
        
        if self.index is None:
            self.index = faiss.IndexFlatIP(dimension) # Inner Product (Cosine Similarity since normalized)
            
        self.index.add(embeddings)
        self.metadata.extend(documents)
        
    def save(self):
        """Persists the index and metadata to disk."""
        if self.index:
            faiss.write_index(self.index, self.index_file)
        with open(self.metadata_file, "wb") as f:
            pickle.dump(self.metadata, f)
            
    def load(self):
        """Loads the index and metadata from disk."""
        self.index = faiss.read_index(self.index_file)
        with open(self.metadata_file, "rb") as f:
            self.metadata = pickle.load(f)
            
    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Document]:
        """Searches for the most similar documents."""
        if not self.index or len(self.metadata) == 0:
            return []
            
        # FAISS expects 2D array
        query_vector = np.array([query_embedding]) 
        distances, indices = self.index.search(query_vector, top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.metadata):
                doc = self.metadata[idx]
                # Inject score into metadata just for reference (optional)
                # doc.metadata["score"] = float(distances[0][i]) 
                results.append(doc)
                
        return results

def get_retriever(model_name="BAAI/bge-m3", index_path="./data/index"):
    embedder = Embedder(model_name)
    store = VectorStore(index_path)
    return embedder, store
