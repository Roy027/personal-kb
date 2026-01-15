from typing import List, Tuple, Dict, Any
from src.kb.retrieve.retriever import Retriever, Reranker
from src.kb.index.vector_store import get_retriever
from src.kb.rag.llm import LocalLLM
from src.kb.rag.prompt import SYSTEM_PROMPT, build_rag_prompt
from src.kb.schema import Document

class AnswerEngine:
    def __init__(self, index_path: str = "./data/index", llm_model: str = "qwen3:8b"):
        # Instantiate Retriever dependencies manually or via helper
        embedder, vector_store = get_retriever(index_path=index_path)
        reranker = Reranker() # Default model
        
        self.retriever = Retriever(embedder=embedder, vector_store=vector_store, reranker=reranker)
        self.llm = LocalLLM(model=llm_model)

    def answer(self, query: str, top_k: int = 10, top_n: int = 3, file_filters: List[str] = None) -> Tuple[str, List[Document]]:
        """
        End-to-end RAG pipeline:
        1. Retrieve documents (Recall + Rerank)
        2. Build Prompt
        3. Generate Answer
        
        Returns:
            (answer_text, source_documents)
        """
        # 1. Retrieve
        print(f"Retrieving for query: {query}...")
        relevant_docs = self.retriever.retrieve(query, top_k=top_k, top_n=top_n, file_filters=file_filters)
        
        if not relevant_docs:
            return "No relevant documents found in the knowledge base.", []

        # 2. Build Prompt
        user_prompt = build_rag_prompt(query, relevant_docs)
        
        # 3. Generate
        print("Generating answer...")
        answer = self.llm.generate(prompt=user_prompt, system_prompt=SYSTEM_PROMPT)
        
        return answer, relevant_docs
