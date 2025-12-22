# Issue #2: PDF Text Extraction Module

## Goal
Implement a robust PDF text extraction module that reads PDF files and converts them into a unified `Document` format for the knowledge base.

## Proposed Changes

### 1. Document Schema
Create `src/kb/schema.py` to define the unified data structure.
- `Document`: Represents a file or a part of a file.
    - `content`: (str) The text content.
    - `metadata`: (dict) source, page_number, file_path, etc.

### 2. PDF Loader
Create `src/kb/ingestion/pdf_loader.py`.
- Function/Class to load PDF.
- Use `pypdf` as per dependencies.
- Extract text page by page to preserve page numbers in metadata.
- Clean text (remove excessive whitespace).

### 3. Testing
Create `tests/test_pdf_loader.py`.
- Generate a sample PDF on the fly or use a mock.
- Verify text extraction and metadata correctness.

## Verification Plan
### Automated Tests
- Run `pytest tests/test_pdf_loader.py` covering:
    - Single page extraction
    - Multi-page extraction
    - Metadata verification (page numbers, source path)
