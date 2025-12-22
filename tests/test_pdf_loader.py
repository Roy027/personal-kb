import pytest
from unittest.mock import MagicMock, patch
from src.kb.ingestion.pdf_loader import PDFLoader
from src.kb.schema import Document

@patch("src.kb.ingestion.pdf_loader.PdfReader")
@patch("os.path.exists")
def test_pdf_loader_basic(mock_exists, mock_pdf_reader):
    # Setup
    mock_exists.return_value = True
    
    # Mocking PdfReader and pages
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Hello World"
    
    mock_reader_inst = MagicMock()
    mock_reader_inst.pages = [mock_page]
    mock_pdf_reader.return_value = mock_reader_inst
    
    # Execution
    loader = PDFLoader("fake_path.pdf")
    docs = loader.load()
    
    # Assertions
    assert len(docs) == 1
    assert docs[0].content == "Hello World"
    assert docs[0].metadata["page_number"] == 1
    assert docs[0].metadata["source"] == "fake_path.pdf"

@patch("src.kb.ingestion.pdf_loader.PdfReader")
@patch("os.path.exists")
def test_pdf_loader_empty_page(mock_exists, mock_pdf_reader):
    # Setup
    mock_exists.return_value = True
    
    # Mocking an empty page
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "   "
    
    mock_reader_inst = MagicMock()
    mock_reader_inst.pages = [mock_page]
    mock_pdf_reader.return_value = mock_reader_inst
    
    # Execution
    loader = PDFLoader("empty.pdf")
    docs = loader.load()
    
    # Assertions: Should ignore empty/whitespace pages
    assert len(docs) == 0

@patch("os.path.exists")
def test_pdf_loader_file_not_found(mock_exists):
    mock_exists.return_value = False
    with pytest.raises(FileNotFoundError):
        PDFLoader("non_existent.pdf")
