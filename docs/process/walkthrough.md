# Walkthrough - Issue #2: PDF Text Extraction

I have completed the implementation of the PDF text extraction module. This module is the first step in the ingestion pipeline, responsible for converting PDF files into a standardized `Document` format.

## Changes Made

### 1. Document Schema
Created [schema.py](file:///c:/Users/ruoyu.dai/OneDrive%20-%20%E5%A4%A9%E5%90%88%E5%85%89%E8%83%BD%E8%82%A1%E4%BB%BD%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8/Work/03_Projects/17_RAG_%E7%9F%A5%E8%AF%86%E5%BA%93/personal-kb/src/kb/schema.py) to unify data handling across different loaders.

```python
@dataclass
class Document:
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### 2. PDF Loader
Implemented [pdf_loader.py](file:///c:/Users/ruoyu.dai/OneDrive%20-%20%E5%A4%A9%E5%90%88%E5%85%89%E8%83%BD%E8%82%A1%E4%BB%BD%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8/Work/03_Projects/17_RAG_%E7%9F%A5%E8%AF%86%E5%BA%93/personal-kb/src/kb/ingestion/pdf_loader.py) using `pypdf`.
- **Page-by-page extraction**: Each page becomes a separate `Document` object initially.
- **Metadata**: Includes `source`, `page_number`, and `total_pages`.
- **Cleaning**: Basic whitespace normalization.

### 3. Git Maintenance
- Added `.gitignore` to exclude `__pycache__` and data contents.
- Ensured empty directories are tracked using `.gitkeep`.
- Pushed all changes to the remote repository.

---

## Verification Results

### Automated Tests
I ran unit tests with mocked PDF data to verify extraction logic.

```bash
python -m pytest tests/test_pdf_loader.py
```

**Output:**
```
tests\test_pdf_loader.py ...                                             [100%]
============================== 3 passed in 0.18s ==============================
```

The tests covered:
- [x] Basic text extraction correctness.
- [x] Handling of empty/whitespace-only pages (skipped).
- [x] Error handling for missing files.

# Walkthrough - Issue #3: HTML Content Extraction

I have completed the implementation of the HTML content extraction module.

## Changes Made

### 1. HTML Loader
Implemented `src/kb/ingestion/html_loader.py` using `BeautifulSoup`.
- **Text Extraction**: Extracts clean text while removing scripts, styles, nav, and footer elements.
- **Metadata**: Captures `title` and `source`.
- **Return Format**: Currently returns a single `Document` per file (chunking will fail later if too large, but compliant with current scope).

### 2. Dependencies
- Installed `beautifulsoup4` and `requests`.

## Verification Results

### Automated Tests
I implemented `tests/test_html_loader.py` and ran it.

```bash
python -m pytest tests/
```

**Output:**
```
tests\test_html_loader.py ..                                             [ 40%]
tests\test_pdf_loader.py ...                                             [100%]
============================== 5 passed in 0.29s ==============================
```

The tests covered:
- [x] Basic HTML tag stripping (h1, p, div).
- [x] Removal of unwanted tags (script, style).
- [x] Metadata extraction verification.

# Walkthrough - Issue #4: Chunk Strategy

I have implemented the Chunking strategy to split large documents into token-limited segments suitable for embedding.

## Changes Made

### 1. Chunker Implementation
Created `src/kb/chunking/chunker.py`.
- **Algorithm**: Recursive Character split optimized for tokens.
- **Tokenizer**: Uses `tiktoken` (cl100k_base) for accurate token counting.
- **Strategy**:
    1. Split by `\n\n` (Paragraphs) first.
    2. Split by `\n` (Lines) if needed.
    3. Split by ` ` (Words) if needed.
    4. Recursively merges chunks to fit `chunk_size` (default 800) with `chunk_overlap` (default 100).
- **Metadata**: Preserves original metadata and adds `chunk_index` and `chunk_id`.

## Verification Results

### Automated Tests
Created and ran `tests/test_chunking.py`.

```bash
python -m pytest tests/test_chunking.py
```

**Output:**
```
tests\test_chunking.py ....                                              [100%]
============================== 4 passed in 0.20s ==============================
```

The tests covered:
- [x] Small documents remaining intact.
- [x] Large documents being split correctly.
- [x] Overlap logic functioning (content duplication at boundaries).
- [x] Paragraph preservation preference.

# Walkthrough - Issue #5: Embedding + Vector Store

I have implemented the generic Embedding interface and FAISS-based Vector Store.

## Changes Made

### 1. Dependencies
Installed `faiss-cpu`, `sentence-transformers`, `numpy`, and `pandas`.

### 2. Implementation
Created `src/kb/index/vector_store.py`.
- **Embedder**: Wrapper around `SentenceTransformer` (defaults to `BAAI/bge-m3`).
- **VectorStore**:
    - Uses `faiss.IndexFlatIP` (Inner Product) for fast cosine similarity search (assuming normalized embeddings).
    - Persists metadata alongside index using `pickle`.
    - Supports `save()`, `load()`, `add_documents()`, and `search()`.

## Verification Results

### Automated Tests
Created `tests/test_vector_store.py` with mocked embeddings to avoid large model downloads during CI/test.

```bash
python -m pytest tests/test_vector_store.py
```

**Output:**
```
tests\test_vector_store.py ..                                            [100%]
======================= 2 passed, 3 warnings in 10.18s ========================
```

The tests covered:
- [x] Index creation and metadata storage.
- [x] Adding documents to FAISS.
- [x] Searching and retrieving correct metadata.
- [x] Persistence (Safe/Load) correctness.

# Walkthrough - Issue #6: CLI Scripts (Ingest & Query)

I have implemented the CLI scripts to allow manual ingestion and querying of the knowledge base.

## Changes Made

### 1. Ingestion Script (`scripts/ingest.py`)
- Walks through `data/raw`.
- Detects file type and selects appropriate loader (PDF/HTML).
- Chunks documents.
- Generates embeddings.
- Saves index to `data/index`.

### 2. Query Script (`scripts/query.py`)
- Loads index from `data/index`.
- Embeds user query.
- Performs vector search.
- Prints top-k results with metadata and content preview.

## Verification Results
Performed an end-to-end manual test with a dummy PDF.
1. Created `data/raw/test.pdf`.
2. Ran `python scripts/ingest.py --reset`.
3. Ran `python scripts/query.py "personal knowledge base"`.

**Result:**
```
Query: personal knowledge base

--- Result 1 ---
Source: test.pdf
Page/Chunk: 1 / 0
Content:
This is a test PDF for the Personal Knowledge Base....
```
- [x] System correctly ingested PDF.
- [x] System correctly retrieved content based on semantic similarity.

# Walkthrough - Issue #7: Retrieval + Rerank Pipeline

I have implemented a hybrid retrieval pipeline that combines vector similarity with cross-encoder reranking.

## Changes Made

### 1. Reranker Implementation
- Created `Reranker` class in `src/kb/retrieve/retriever.py`.
- Uses `BAAI/bge-reranker-large` to score Query-Document pairs.
- Sorts results by relevance score and keeps the top-N.

### 2. Retriever Orchestration
- Created `Retriever` class as a single interface.
- **Workflow**:
    1. Initial Recall: FAISS search retrieves Top-K (e.g., 10) results.
    2. Precision Reranking: Cross-Encoder scores the 10 results.
    3. Final Selection: Returns top-N (e.g., 3) highest scoring chunks.

## Verification Results

### Automated Tests
Ran `tests/test_retriever.py` with mocked models.

```bash
conda run -n personal-kb python -m pytest tests/test_retriever.py
```

**Output:**
```
tests\test_retriever.py ..                                               [100%]
======================= 2 passed, 3 warnings in 17.40s ========================
```
- [x] Vector search integrates correctly with reranking steps.
- [x] Reranker correctly sorts documents by mock scores.
- [x] Hybrid pipeline returns the most relevant document (even if it wasn't the top 1 in vector search).

# Walkthrough - Infrastructure: Environment Migration

I have migrated the project from using the global Miniforge `base` environment to a dedicated, isolated Conda environment.

## Changes Made

### 1. Environment Creation
Created a new Conda environment named `personal-kb` with **Python 3.11**.
- **Reasoning**: To ensure dependency isolation and avoid corrupting the system's base environment.

### 2. Dependency Management
- All project dependencies (Streamlit, FAISS, PyTorch, etc.) were installed into the `personal-kb` environment.
- Cleaned up the `base` environment by removing the libraries mistakenly installed there earlier.
- Re-stabilized the `base` environment by ensuring essential libraries like `requests` were re-installed.

### 3. Usage Pattern
From now on, all project commands should be run using:
```bash
conda run -n personal-kb <command>
```
