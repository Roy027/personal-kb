from typing import List
from src.kb.schema import Document

SYSTEM_PROMPT = """You are a precise knowledge base assistant. 
Your task is to answer the user's question strictly based on the provided context documents.

Rules:
1. Use ONLY the information from the context. Do not use outside knowledge.
2. If the answer is not present in the context, state clearly: "I cannot find the answer in the provided documents."
3. Cite your sources DETAILEDLY. Append the reference at the end of the sentence.
   - Format: [Source: filename, Page: X] (if Page is available)
   - Or: [Source: filename] (if Page is N/A)
4. IMPORTANT: Answer in the SAME LANGUAGE as the user's question. If the user asks in Chinese, answer in Chinese.
5. Keep the answer concise and relevant.
"""

def format_context(documents: List[Document]) -> str:
    """
    Formats a list of documents into a single context string.
    """
    context_parts = []
    for i, doc in enumerate(documents, 1):
        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page_number", "N/A")
        chunk_idx = doc.metadata.get("chunk_index", "N/A")
        
        # Prepare location info string
        location_info = f"Source: {source}"
        if page != "N/A":
            location_info += f", Page: {page}"
        if chunk_idx != "N/A":
            location_info += f", Chunk: {chunk_idx}"
            
        # Format: 
        # [Document 1] (Source: test.pdf, Page: 1, Chunk: 5)
        # Content...
        part = f"[Document {i}] ({location_info})\n{doc.content.strip()}"
        context_parts.append(part)
    
    return "\n\n".join(context_parts)

def build_rag_prompt(query: str, documents: List[Document]) -> str:
    """
    Constructs the final user prompt with context.
    """
    context_str = format_context(documents)
    
    return f"""Context information is below:
---------------------
{context_str}
---------------------

Given the context information and not prior knowledge, answer the query.
Query: {query}
"""
