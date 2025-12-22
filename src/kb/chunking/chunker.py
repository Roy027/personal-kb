import tiktoken
from typing import List, Optional
from src.kb.schema import Document

class text_splitter:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 100, separators: Optional[List[str]] = None):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", " ", ""]
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def _len(self, text: str) -> int:
        return len(self.tokenizer.encode(text))

    def split_text(self, text: str) -> List[str]:
        final_chunks = []
        
        # Determine the best separator to use
        separator = self.separators[-1]
        for sep in self.separators:
            if sep == "":
                separator = ""
                break
            if sep in text:
                separator = sep
                break
        
        # Split logic
        if separator:
            splits = text.split(separator)
        else:
            splits = list(text) # Split by character
            
        good_splits = []
        for s in splits:
             # Recursively split if still too big
            if self._len(s) > self.chunk_size:
                 # Find index of current separator
                 try:
                     index = self.separators.index(separator)
                     next_separators = self.separators[index+1:]
                 except ValueError:
                     next_separators = []
                 
                 if next_separators:
                     sub_splitter = text_splitter(self.chunk_size, self.chunk_overlap, next_separators)
                     good_splits.extend(sub_splitter.split_text(s))
                 else:
                     # If no more separators, just force split (not ideal but safe fallback)
                     good_splits.append(s) 
            else:
                good_splits.append(s)

        # Merge splits
        return self._merge_splits(good_splits, separator)

    def _merge_splits(self, splits: List[str], separator: str) -> List[str]:
        final_chunks = []
        current_chunk = []
        current_len = 0
        
        for split in splits:
            split_len = self._len(split)
            
            # If adding this split exceeds chunk size, save current and start new
            if current_len + split_len + (self._len(separator) if current_chunks else 0) > self.chunk_size:
                if current_chunk:
                    doc = separator.join(current_chunk)
                    final_chunks.append(doc)
                    
                    # Apply overlap: keep trailing chunks
                    # This is a simplified overlap; complex overlap logic requires deque
                    while current_len > self.chunk_overlap and current_chunk:
                         popped = current_chunk.pop(0)
                         current_len -= self._len(popped) + self._len(separator) # approx
                    
                
            current_chunk.append(split)
            current_len += split_len + (1 if separator else 0) # Rough adder for separator
            
        if current_chunk:
            final_chunks.append(separator.join(current_chunk))
            
        return final_chunks

class Chunker:
    """Chunks documents into smaller pieces."""
    
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.separators = ["\n\n", "\n", " ", ""]

    def _token_len(self, text: str) -> int:
        return len(self.tokenizer.encode(text))

    def split_documents(self, documents: List[Document]) -> List[Document]:
        chunked_docs = []
        
        for doc in documents:
            text = doc.content
            chunks = self._recursive_split(text, self.separators)
            
            for i, chunk in enumerate(chunks):
                new_meta = doc.metadata.copy()
                new_meta["chunk_index"] = i
                new_meta["chunk_id"] = f"{doc.metadata.get('file_name', 'unknown')}_{doc.metadata.get('page_number', 0)}_{i}"
                chunked_docs.append(Document(content=chunk, metadata=new_meta))
                
        return chunked_docs

    def _recursive_split(self, text: str, separators: List[str]) -> List[str]:
        """Recursively split text using the given separators."""
        final_chunks = []
        
        # 1. Find the appropriate separator
        separator = separators[-1]
        for sep in separators:
            if sep == "":
                separator = ""
                break
            if sep in text:
                separator = sep
                break
                
        # 2. Split text
        if separator:
            splits = text.split(separator)
        else:
            splits = list(text) # Character split
            
        # 3. Process splits
        new_splits = []
        for s in splits:
            if self._token_len(s) <= self.chunk_size:
                new_splits.append(s)
            else:
                # If a segment is too large, recurse with the next separator
                try:
                    idx = separators.index(separator)
                    if idx + 1 < len(separators):
                        sub_chunks = self._recursive_split(s, separators[idx+1:])
                        new_splits.extend(sub_chunks)
                    else:
                        # Fallback: keep even if too big (or we could force slice)
                        # For now, we'll just keep it to avoid data loss
                        new_splits.append(s) 
                except ValueError:
                     new_splits.append(s)

        # 4. Merge splits into chunks
        return self._merge_splits(new_splits, separator)

    def _merge_splits(self, splits: List[str], separator: str) -> List[str]:
        docs = []
        current_doc: List[str] = []
        total_len = 0
        separator_len = self._token_len(separator)

        for d in splits:
            _len = self._token_len(d)
            if total_len + _len + (separator_len if current_doc else 0) > self.chunk_size:
                if total_len > self.chunk_size:
                    # Single chunk is too big, add it anyway
                    if not current_doc:
                        docs.append(d)
                        continue
                
                if current_doc:
                    doc = separator.join(current_doc)
                    if doc.strip():
                        docs.append(doc)
                    
                    # Reset with overlap
                    # Simple overlap: keep the last 20% of items or similar
                    # Better overlap: keep items until overlap size is met
                    while total_len > self.chunk_overlap and current_doc:
                        removed = current_doc.pop(0)
                        total_len -= (self._token_len(removed) + separator_len)
            
            current_doc.append(d)
            total_len += _len + (separator_len if len(current_doc) > 1 else 0)

        if current_doc:
            doc = separator.join(current_doc)
            if doc.strip():
                docs.append(doc)
                
        return docs
