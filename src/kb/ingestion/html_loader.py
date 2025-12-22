import os
from typing import List
from bs4 import BeautifulSoup
from src.kb.schema import Document

class HTMLLoader:
    """Loader for HTML documents."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

    def load(self) -> List[Document]:
        """Loads the HTML file and returns a list containing a single Document."""
        documents = []
        try:
            with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove script and style elements
            for script_or_style in soup(['script', 'style', 'nav', 'footer']):
                script_or_style.decompose()

            # Get text
            text = soup.get_text(separator='\n')
            
            # Clean text: remove extra whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            cleaned_text = '\n'.join(chunk for chunk in chunks if chunk)

            # Metadata
            title = soup.title.string if soup.title else "No Title"
            metadata = {
                "source": self.file_path,
                "file_name": os.path.basename(self.file_path),
                "title": title
            }
            
            documents.append(Document(content=cleaned_text, metadata=metadata))

        except Exception as e:
            print(f"Error loading HTML {self.file_path}: {e}")
            
        return documents

def load_html(file_path: str) -> List[Document]:
    """Helper function to load an HTML file."""
    loader = HTMLLoader(file_path)
    return loader.load()
