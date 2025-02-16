from typing import Optional, List
import logging
from pathlib import Path
from dotenv import load_dotenv
import os

from .db import DatabaseManager
from .embedder import Embedder
from .file_processor import FileProcessor
from .query_processor import QueryProcessor

class Aidien:
    def __init__(
        self,
        env_path: Optional[str] = None,
        target_directory: Optional[str] = None,
        database_url: Optional[str] = None,
        embed_model_name: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        openai_model: Optional[str] = None,
        chunk_min_words: int = 500,
        chunk_max_words: int = 1000,
        chunk_overlap_words: int = 200
    ):
        """
        Initialize Aidien with configuration either from .env file or direct parameters.
        
        Args:
            env_path: Path to .env file (optional)
            target_directory: Directory to scan for code files
            database_url: PostgreSQL connection string
            embed_model_name: Name of the embedding model to use
            openai_api_key: OpenAI API key
            openai_model: OpenAI model to use for query processing
            chunk_min_words: Minimum words per chunk
            chunk_max_words: Maximum words per chunk
            chunk_overlap_words: Number of words to overlap between chunks
        """
        # Load environment variables if env_path is provided
        if env_path:
            load_dotenv(env_path, override=True)
        
        # Set configuration (parameters override env variables)
        self.target_directory = target_directory or os.getenv("TARGET_DIRECTORY", "./")
        self.database_url = database_url or os.getenv("DATABASE_URL")
        self.embed_model_name = embed_model_name or os.getenv("EMBED_MODEL_NAME")
        
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key
        
        # Add this line after loading env variables
        self.openai_model = openai_model or os.getenv("OPENAI_MODEL", "gpt-4")
        
        # Initialize components
        self.db = DatabaseManager(self.database_url)
        self.embedder = Embedder(self.embed_model_name)
        self.file_processor = FileProcessor(
            chunk_min_words=chunk_min_words,
            chunk_max_words=chunk_max_words,
            chunk_overlap_words=chunk_overlap_words
        )
        self.query_processor = QueryProcessor(openai_model=self.openai_model)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def embed_directory(self, directory: Optional[str] = None) -> None:
        """
        Embed all supported files in the specified directory or the default target directory.
        
        Args:
            directory: Optional directory path to override the default
        """
        target_dir = directory or self.target_directory
        self.logger.info(f"Embedding files in directory: {target_dir}")
        
        # Ensure database is ready
        self.db.create_tables()
        
        # Get and process files
        files = self.file_processor.get_supported_files(target_dir)
        self.logger.info(f"Found {len(files)} supported files.")
        
        for file in files:
            self.embed_file(file)

    def embed_file(self, filename: str) -> None:
        """
        Embed a single file into the database.
        
        Args:
            filename: Path to the file to embed
        """
        self.logger.info(f"Embedding file: {filename}")
        chunks = self.file_processor.chunk_file(filename)
        
        for chunk in chunks:
            embedding = self.embedder.compute_embedding(chunk["code"])
            self.db.insert_chunk(chunk, embedding)

    def process_query(self, query: str) -> None:
        """
        Process a natural language query against the embedded codebase.
        
        Args:
            query: The natural language query to process
        """
        print(f"Processing query: {query} with model: {self.openai_model}")
        self.logger.info(f"Processing query: {query} with model: {self.openai_model}")
        self.query_processor.process(query, self.embedder, self.db) 