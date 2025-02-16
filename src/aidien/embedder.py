import logging
import torch
import torch.nn.functional as F
from transformers import AutoModel
from typing import Optional

class Embedder:
    def __init__(self, model_name: str, max_length: int = 512):
        """
        Initialize the embedding model.
        
        Args:
            model_name: Name of the HuggingFace model to use
            max_length: Maximum sequence length for the model
        """
        self.logger = logging.getLogger(__name__)
        self.max_length = max_length
        
        self.logger.info(f"Loading embedding model: {model_name}")
        try:
            self.model = AutoModel.from_pretrained(model_name, trust_remote_code=True)
            self.model.eval()  # Set to evaluation mode
        except Exception as e:
            self.logger.exception(f"Error loading model {model_name}")
            raise e

    def compute_embedding(self, text: str, instruction: Optional[str] = None) -> torch.Tensor:
        """
        Compute a normalized embedding for the given text.
        
        Args:
            text: Text to embed
            instruction: Optional instruction prefix for the embedding
            
        Returns:
            Normalized embedding tensor
        """
        try:
            if instruction:
                text = f"{instruction}\n{text}"
            
            # Encode and normalize
            with torch.no_grad():
                embedding = self.model.encode(
                    [text], 
                    max_length=self.max_length
                )
                embedding = F.normalize(embedding, p=2, dim=1)
            return embedding
            
        except Exception as e:
            self.logger.exception("Error computing embedding")
            raise e 