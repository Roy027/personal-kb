import pytest
from unittest.mock import MagicMock, patch
from src.kb.retrieve.retriever import Retriever, Reranker
from src.kb.schema import Document

TEST_DOCS = [
    Document(content="Doc A: About cats.", metadata={"id": "A"}),
    Document(content="Doc B: About dogs.", metadata={"id": "B"}),
    Document(content="Doc C: About fish.", metadata={"id": "C"})
]

@patch("src.kb.retrieve.retriever.CrossEncoder")
def test_reranker_logic(mock_ce):
    # Setup mock
    instance = MagicMock()
    # Mock scores: C > A > B for a query "fish"
    instance.predict.return_value = [0.1, 0.05, 0.9] # standard order corresponds to input list
    mock_ce.return_value = instance
    
    reranker = Reranker("fake/path")
    
    # Input order A, B, C
    reranked = reranker.rerank("query", TEST_DOCS, top_n=2)
    
    # Expected: C (0.9), A (0.1) as top 2
    assert len(reranked) == 2
    assert reranked[0].metadata["id"] == "C"
    assert reranked[0].metadata["rerank_score"] == 0.9
    assert reranked[1].metadata["id"] == "A"

def test_retriever_flow():
    mock_embedder = MagicMock()
    mock_store = MagicMock()
    mock_reranker = MagicMock()
    
    # Mock Vector Store returns 3 docs
    mock_store.search.return_value = TEST_DOCS
    
    # Mock Reranker returns just 1 sorted doc
    mock_reranker.rerank.return_value = [TEST_DOCS[2]] # Doc C
    
    retriever = Retriever(mock_embedder, mock_store, mock_reranker)
    
    # 1. Test with Rerank
    results = retriever.retrieve("test", top_k=3, top_n=1, use_rerank=True)
    
    mock_embedder.embed_query.assert_called_once()
    mock_store.search.assert_called_with(mock_embedder.embed_query.return_value, top_k=3)
    mock_reranker.rerank.assert_called_with("test", TEST_DOCS, top_n=1)
    
    assert len(results) == 1
    assert results[0].metadata["id"] == "C"
    
    # 2. Test without Rerank
    mock_store.search.reset_mock()
    mock_reranker.rerank.reset_mock()
    
    results_no_rerank = retriever.retrieve("test", top_k=3, top_n=2, use_rerank=False)
    
    mock_reranker.rerank.assert_not_called()
    assert len(results_no_rerank) == 2
    assert results_no_rerank[0].metadata["id"] == "A" # Original order
