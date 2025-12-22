from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class Document:
    """Standard representation of a document chunk."""
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        # Ensure essential metadata keys exist if not provided
        if "source" not in self.metadata:
            self.metadata["source"] = "unknown"
