# Walkthrough - Issue #2: PDF Text Extraction

I have completed the implementation of the PDF text extraction module. This module is the first step in the ingestion pipeline, responsible for converting PDF files into a standardized `Document` format.

## Changes Made

### 1. Document Schema
Created `src/kb/schema.py` to unify data handling across different loaders.

```python
@dataclass
class Document:
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### 2. PDF Loader
Implemented `src/kb/ingestion/pdf_loader.py` using `pypdf`.
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
    4. **File Filtering** (New): Added support for `file_filters` argument to only retrieve documents from specific files.

## Verification Results

### Automated Tests
Ran `tests/test_retriever.py` with mocked models.

```bash
conda run -n local-kb python -m pytest tests/test_retriever.py
```

**Output:**
```
tests\test_retriever.py ..                                               [100%]
======================= 2 passed, 3 warnings in 17.40s ========================
```
- [x] Vector search integrates correctly with reranking steps.
- [x] Reranker correctly sorts documents by mock scores.
- [x] Hybrid pipeline returns the most relevant document.

# Walkthrough - Issue #8 & #9: Local LLM + RAG Pipeline

I have integrated the local LLM (Ollama) and built strict RAG prompting logic.

## Changes Made

### 1. Local LLM Integration
- Implemented `src/kb/rag/llm.py` wrapping `ollama` Python client.
- Defaults to model `qwen3:8b` (or `qwen2.5:14b`).
- Includes a simple `generate()` method adhering to system prompts.

### 2. RAG Prompt Engineering
- Created `src/kb/rag/prompt.py`.
- **System Prompt**: Enforces STRICT citation rules and refusal to hallucinate.
- **Context Format**: `[Document N] (Source: filename, Page: X, Chunk: Y)` for precise location tracking.
- **Validation**: Added logic to prefer the user's language (e.g., Chinese query -> Chinese answer).

### 3. Answer Engine
- Created `src/kb/rag/answer.py`.
- Connects Retriever and LLM.
- **Flow**: Query -> Retrieve (w/ Filter) -> Build Prompt -> LLM Generation -> Answer + Sources.

## Verification Results
- Ran `scripts/ask.py "What is the secret code?"`.
- System successfully retrieved the snippet from HTML test data.
- Generated answer: "... is Project-Blue-Sky..." with correct citation `[Source: rag_test.html]`.

# Walkthrough - Issue #11: Streamlit UI (Web Interface)

I have built a complete web-based user interface using Streamlit.

## Changes Made

### 1. UI Structure (`src/kb/ui/app.py`)
- **Dual Tab Design**: 
    - `💬 智能问答` (Chat): Main interface for Q&A.
    - `🗃️ 知识库管理` (Knowledge Base): Manage files, view stats, and upload new documents.
- **Sidebar Settings**: 
    - Model selection (Qwen/Llama).
    - Retrieval parameters (Top-K / Top-N).
    - **Dynamic File Filter**: A table in the sidebar to tick/untick specific documents for search scope.

### 2. Features
- **File Upload**: Direct drag-and-drop ingestion of PDF/HTML files via the web UI.
- **Progress Tracking**: Real-time progress bars for ingestion steps (Loading -> Chunking -> Embedding).
- **Interactive Citations**: Chat responses include expandable "Looks Sources" section showing exact text matches and relevance scores.
- **Localization**: Full Chinese UI support.

## Verification Results
- Launched via `streamlit run src/kb/ui/app.py`.
- Successfully uploaded a new PDF via browser.
- Successfully filtered search scope to a specific document.
- Verified Chinese Q&A and Citations are rendered correctly.

# Walkthrough - Feature: Dynamic File Filtering (v0.3.0)

I have implemented a dynamic document filtering system allowing users to select/deselect specific files for retrieval directly from the UI.

## Changes Made

### 1. Vector Store
- Updated `src/kb/index/vector_store.py`:
    - Added `get_indexed_files()` method to return a summary of indexed documents (filename and chunk count).

### 2. Retrieval Pipeline
- Updated `src/kb/retrieve/retriever.py`:
    - Added `file_filters` argument to `retrieve()` method.
    - Implemented post-retrieval filtering logic: If filters are applied, initial search candidates are expanded (5x Top-K), then filtered by filename, then trimmed back to Top-K.
- Updated `src/kb/rag/answer.py`: passed `file_filters` from `answer()` down to `retrieve()`.

### 3. UI Implementation
- Updated `src/kb/ui/app.py`:
    - Added a **Knowledge Base Scope** section in the sidebar.
    - Uses `st.data_editor` to show a list of files with checkboxes (default checked).
    - Preserves selection state across reruns using `st.session_state`.
    - Passes the selected file list to the RAG engine for every query.
    - Added `sys.path` modification to resolve module import issues when running via `streamlit run`.

## Verification Results
- Verified that unchecking a file in the sidebar excludes its content from RAG answers.
- Verified that "Select All" (default) works as expected.
- Verified file stats (chunk counts) are displayed correctly in the selector.
