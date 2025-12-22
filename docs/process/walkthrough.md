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
