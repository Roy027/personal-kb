import pytest
import os
from unittest.mock import patch, mock_open
from src.kb.ingestion.html_loader import HTMLLoader

TEST_HTML_CONTENT = """
<html>
    <head><title>Test Page</title></head>
    <body>
        <h1>Main Header</h1>
        <p>This is a test paragraph.</p>
        <script>console.log('remove this');</script>
        <style>body { color: red; }</style>
        <div>
            Another div with text.
        </div>
    </body>
</html>
"""

@patch("os.path.exists")
@patch("builtins.open", new_callable=mock_open, read_data=TEST_HTML_CONTENT)
def test_html_loader_basic(mock_file, mock_exists):
    mock_exists.return_value = True
    
    loader = HTMLLoader("test.html")
    docs = loader.load()
    
    assert len(docs) == 1
    content = docs[0].content
    metadata = docs[0].metadata
    
    # Assertions
    assert "Main Header" in content
    assert "This is a test paragraph." in content
    assert "Another div with text." in content
    assert "remove this" not in content  # script should be removed
    assert "body { color: red; }" not in content # style should be removed
    
    assert metadata["title"] == "Test Page"
    assert metadata["source"] == "test.html"

@patch("os.path.exists")
def test_html_loader_file_not_found(mock_exists):
    mock_exists.return_value = False
    with pytest.raises(FileNotFoundError):
        HTMLLoader("non_existent.html")
