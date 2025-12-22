import pytest
import numpy as np
import os
import shutil
from unittest.mock import MagicMock, patch
from src.kb.index.vector_store import Embedder, VectorStore
from src.kb.schema import Document

# Test data
TEST_DOCS = [
    Document(content="Apple is a fruit.", metadata={"id": 1}),
    Document(content="Car is a vehicle.", metadata={"id": 2}),
    Document(content="Banana is yellow.", metadata={"id": 3})
]

@pytest.fixture
def mock_embedder():
    with patch("src.kb.index.vector_store.SentenceTransformer") as mock:
        # Create a fake embedding function that returns distinct vectors
        # Dimension = 2 for simplicity
        def fake_encode(texts, normalize_embeddings=True):
            embeddings = []
            for t in texts:
                if "fruit" in t or "Banana" in t:
                    embeddings.append([1.0, 0.0]) # fruit-ish vector
                elif "vehicle" in t:
                    embeddings.append([0.0, 1.0]) # vehicle-ish vector
                else:
                    embeddings.append([0.5, 0.5])
            return np.array(embeddings)
            
        instance = MagicMock()
        instance.encode.side_effect = fake_encode
        mock.return_value = instance
        yield VectorStore # We don't actually need to yield embedder class, just context

def test_vector_store_add_and_search(tmp_path):
    # Setup temporary index path
    index_path = str(tmp_path / "test_index")
    
    # 1. Embed documents (using mock logic locally for test stability)
    # We will simulate embeddings directly without calling the generic Embedder class to avoid downloading models
    embeddings = np.array([
        [1.0, 0.0], # Apple
        [0.0, 1.0], # Car
        [0.9, 0.1]  # Banana
    ]).astype('float32')
    
    store = VectorStore(index_path=index_path)
    store.add_documents(TEST_DOCS, embeddings)
    
    assert len(store.metadata) == 3
    
    # 2. Search
    # Query: "fruit" -> [1.0, 0.0]
    query_vec = np.array([1.0, 0.0]).astype('float32')
    results = store.search(query_vec, top_k=2)
    
    assert len(results) == 2
    assert results[0].content == "Apple is a fruit."
    assert results[1].content == "Banana is yellow." # Close to [1,0]
    
    # 3. Save and Load
    store.save()
    
    new_store = VectorStore(index_path=index_path)
    # Metadata should be loaded
    assert len(new_store.metadata) == 3
    
    results_loaded = new_store.search(query_vec, top_k=1)
    assert results_loaded[0].content == "Apple is a fruit."

def test_embedder_call():
    # Only test that wrapper calls the underlying library correctly
    with patch("src.kb.index.vector_store.SentenceTransformer") as mock_st:
        embedder = Embedder("fake_model")
        mock_st.assert_called_with("fake_model")
        
        embedder.embed_query("test")
        embedder.model.encode.assert_called()
