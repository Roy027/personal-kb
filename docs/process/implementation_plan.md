# Issue #7: Retrieval + Rerank Pipeline

## Goal
Implement a robust retrieval pipeline that combines vector search (Top-K) with a Cross-Encoder Reranker to improve result relevance.

## Proposed Changes

### 1. Retriever Class
Create `src/kb/retrieve/retriever.py`.
- **Class**: `Retriever`
- **Components**:
    - `VectorStore` (existing): For initial broad recall (Top-K).
    - `Reranker` (new): For precise scoring of (Query, Document) pairs.
- **Method**: `retrieve(query: str, top_k: int = 5, top_n: int = 3) -> List[Document]`
    1. Get `top_k` results from Vector Store.
    2. Pass specific (Query, Document) pairs to Reranker.
    3. Sort by new score.
    4. Return `top_n` results.

### 2. Reranker Implementation
- Use `sentence-transformers` CrossEncoder or HuggingFace `AutoModelForSequenceClassification`.
- Model: `BAAI/bge-reranker-large` (as per PRD).
- **Optimization**: Load model only when needed or keep it loaded if memory permits.

### 3. CLI Update
- Update `scripts/query.py` to use the new `Retriever` class instead of raw `VectorStore` search.
- Add `--rerank` flag (default True).

## Verification Plan
### Automated Tests
- `tests/test_retriever.py`:
    - Mock Reranker to verify filtering/sorting logic.
    - Test integration with VectorStore.
