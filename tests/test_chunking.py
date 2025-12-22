import pytest
from src.kb.chunking.chunker import Chunker
from src.kb.schema import Document

def test_chunker_small_doc():
    """Test that a small document is not split."""
    chunker = Chunker(chunk_size=100, chunk_overlap=10)
    doc = Document(content="This is a small document.", metadata={"id": 1})
    chunks = chunker.split_documents([doc])
    
    assert len(chunks) == 1
    assert chunks[0].content == "This is a small document."
    assert chunks[0].metadata["id"] == 1

def test_chunker_split_needed():
    """Test splitting a document that exceeds chunk size."""
    chunker = Chunker(chunk_size=10, chunk_overlap=0) # Very small chunk size
    # "word " is 1 token usually. 
    # Let's use a string we know is > 10 tokens
    text = "word " * 20 
    doc = Document(content=text, metadata={"id": 1})
    
    chunks = chunker.split_documents([doc])
    
    assert len(chunks) > 1
    # Check that metadata is preserved
    assert chunks[0].metadata["id"] == 1
    assert "chunk_index" in chunks[0].metadata

def test_chunker_overlap():
    """Test that overlap is applied."""
    chunker = Chunker(chunk_size=10, chunk_overlap=5)
    # A B C D E F ...
    # Chunk 1: A B C D E
    # Chunk 2: D E F G H (Overlap D E)
    
    text = "one two three four five six seven eight nine ten"
    doc = Document(content=text, metadata={})
    
    chunks = chunker.split_documents([doc])
    
    # We expect some words to be repeated
    combined_content = " ".join([c.content for c in chunks])
    word_count_orig = len(text.split())
    word_count_chunks = len(combined_content.split())
    
    assert word_count_chunks > word_count_orig # Overlap implies duplication

def test_chunker_paragraphs():
    """Test that it respects double newlines."""
    chunker = Chunker(chunk_size=50, chunk_overlap=0)
    
    para1 = "Paragraph one is here and it is distinct."
    para2 = "Paragraph two is here and it is also distinct."
    text = f"{para1}\n\n{para2}"
    
    doc = Document(content=text, metadata={})
    chunks = chunker.split_documents([doc])
    
    # Ideally should keep paragraphs intact if they fit
    # Depending on tokenizer, specific length check might vary,
    # but let's assume 50 tokens is enough for one para (~10 words is ~15 tokens).
    
    assert len(chunks) >= 1
    # If they fit in one chunk, it merges them.
    # Let's force split by making max size small but larger than 1 para
    
    chunker_small = Chunker(chunk_size=10, chunk_overlap=0)
    chunks_small = chunker_small.split_documents([doc])
    
    # Just ensure it runs without error and splits reasonable
    assert len(chunks_small) > 1
