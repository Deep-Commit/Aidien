import os
import logging
from typing import List, Dict, Any
from pathlib import Path

class FileProcessor:
    # Mapping of file extensions to language names
    SUPPORTED_LANGUAGES = {
        "py": "python",
        "js": "javascript",
        "ts": "typescript",
        "java": "java",
        "cpp": "cpp",
        "c": "c",
        "cs": "csharp",
        "go": "go",
        "rs": "rust",
        "swift": "swift",
        "php": "php",
        "rb": "ruby",
        "html": "html",
        "css": "css",
        "scss": "scss",
        "json": "json",
        "yaml": "yaml",
        "toml": "toml",
        "sql": "sql"
    }

    def __init__(
        self,
        chunk_min_words: int = 500,
        chunk_max_words: int = 1000,
        chunk_overlap_words: int = 200
    ):
        """
        Initialize the file processor with chunking parameters.
        
        Args:
            chunk_min_words: Minimum words per chunk
            chunk_max_words: Maximum words per chunk
            chunk_overlap_words: Number of words to overlap between chunks
        """
        self.chunk_min_words = chunk_min_words
        self.chunk_max_words = chunk_max_words
        self.chunk_overlap_words = chunk_overlap_words
        self.logger = logging.getLogger(__name__)

    def get_supported_files(self, directory: str) -> List[str]:
        """
        Recursively scan directory for supported file types.
        
        Args:
            directory: Directory path to scan
            
        Returns:
            List of supported file paths
        """
        supported_files = []
        directory_path = Path(directory)
        
        for file_path in directory_path.rglob("*"):
            if file_path.is_file():
                ext = file_path.suffix.lstrip(".")
                if ext in self.SUPPORTED_LANGUAGES:
                    supported_files.append(str(file_path))
        
        self.logger.info(f"Found {len(supported_files)} supported files")
        return supported_files

    def chunk_file(self, filename: str) -> List[Dict[str, Any]]:
        """
        Read a file and split it into overlapping chunks.
        
        Args:
            filename: Path to the file to chunk
            
        Returns:
            List of chunk dictionaries containing filename, indices, and code
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()

            words = content.split()
            chunks = []
            start_idx = 0
            total_words = len(words)

            while start_idx < total_words:
                end_idx = min(start_idx + self.chunk_max_words, total_words)
                chunk_words = words[start_idx:end_idx]
                
                if len(chunk_words) < self.chunk_min_words and start_idx > 0:
                    # If chunk is too small and not the first chunk, merge with previous
                    break
                    
                chunk_code = " ".join(chunk_words)
                chunk_info = {
                    "filename": filename,
                    "start_idx": start_idx + 1,  # human-friendly indexing
                    "end_idx": end_idx,
                    "code": chunk_code
                }
                chunks.append(chunk_info)
                
                # Move start index forward by chunk size minus overlap
                step = max(self.chunk_max_words - self.chunk_overlap_words, 1)
                start_idx += step
                
                if start_idx >= total_words:
                    break

            self.logger.info(f"Split {filename} into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            self.logger.exception(f"Error processing file {filename}")
            raise e 