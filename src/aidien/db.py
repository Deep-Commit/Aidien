import logging
from typing import Dict, Any, List
import psycopg2
from psycopg2 import pool
import torch

class DatabaseManager:
    def __init__(self, database_url: str):
        """
        Initialize database connection pool and manager.
        
        Args:
            database_url: PostgreSQL connection string
        """
        self.logger = logging.getLogger(__name__)
        try:
            self.pool = pool.SimpleConnectionPool(1, 10, dsn=database_url)
            if self.pool:
                self.logger.info("Database connection pool created successfully.")
        except Exception as e:
            self.logger.exception("Error creating connection pool.")
            raise e

    def create_tables(self) -> None:
        """Create necessary tables and extensions if they don't exist."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS code_embeddings (
            id SERIAL PRIMARY KEY,
            filename TEXT,
            start_idx INT,
            end_idx INT,
            embedding vector(4096),
            code TEXT
        );
        """
        conn = self.pool.getconn()
        try:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                cur.execute(create_table_sql)
            self.logger.info("pgvector table verified/created.")
        except Exception as e:
            self.logger.exception("Error creating pgvector table.")
            raise e
        finally:
            self.pool.putconn(conn)

    def insert_chunk(self, chunk: Dict[str, Any], embedding_tensor: torch.Tensor) -> None:
        """
        Insert a code chunk and its embedding into the database.
        
        Args:
            chunk: Dictionary containing chunk information
            embedding_tensor: Tensor containing the embedding
        """
        embedding_str = '[' + ','.join(f"{float(x):.6f}" for x in embedding_tensor[0]) + ']'
        insert_sql = """
        INSERT INTO code_embeddings (filename, start_idx, end_idx, embedding, code)
        VALUES (%s, %s, %s, %s, %s);
        """
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute(insert_sql, (
                    chunk["filename"],
                    chunk["start_idx"],
                    chunk["end_idx"],
                    embedding_str,
                    chunk["code"]
                ))
            conn.commit()
            self.logger.info(
                f"Inserted embedding for {chunk['filename']} words {chunk['start_idx']}-{chunk['end_idx']}"
            )
        except Exception as e:
            self.logger.exception("Error inserting code chunk into DB.")
        finally:
            self.pool.putconn(conn)

    def get_similar_chunks(self, query_embedding: torch.Tensor, limit: int = 10) -> List[tuple]:
        """
        Get the most similar chunks to the query embedding.
        
        Args:
            query_embedding: Tensor containing the query embedding
            limit: Maximum number of results to return
            
        Returns:
            List of tuples (filename, start_idx, end_idx, code)
        """
        embedding_str = '[' + ','.join(f"{float(x):.6f}" for x in query_embedding[0]) + ']'
        select_sql = """
        SELECT filename, start_idx, end_idx, code
        FROM code_embeddings
        ORDER BY embedding <-> %s
        LIMIT %s;
        """
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute(select_sql, (embedding_str, limit))
                rows = cur.fetchall()
            return rows
        except Exception as e:
            self.logger.exception("Error fetching similar chunks")
            return []
        finally:
            self.pool.putconn(conn) 