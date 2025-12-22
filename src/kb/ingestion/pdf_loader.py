import os
from typing import List
from pypdf import PdfReader
from src.kb.schema import Document

class PDFLoader:
    """Loader for PDF documents."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

    def load(self) -> List[Document]:
        """Loads the PDF and returns a list of Documents (one per page)."""
        documents = []
        try:
            reader = PdfReader(self.file_path)
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text and text.strip():
                    # Basic cleaning: replace multiple spaces/newlines
                    cleaned_text = " ".join(text.split())
                    
                    metadata = {
                        "source": self.file_path,
                        "file_name": os.path.basename(self.file_path),
                        "page_number": i + 1,
                        "total_pages": len(reader.pages)
                    }
                    documents.append(Document(content=cleaned_text, metadata=metadata))
        except Exception as e:
            print(f"Error loading PDF {self.file_path}: {e}")
            
        return documents

def load_pdf(file_path: str) -> List[Document]:
    """Helper function to load a PDF."""
    loader = PDFLoader(file_path)
    return loader.load()
