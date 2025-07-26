"""
Milvus Vector Database Integration
Handles embedding generation and vector storage/retrieval
"""

import os
import json
import logging
from typing import List, Dict, Optional, Tuple, Any
import numpy as np
from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType, utility
from sentence_transformers import SentenceTransformer
import torch
from tqdm import tqdm
import time
from .config import *

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorDatabase:
    def __init__(self):
        self.collection = None
        self.embedding_model = None
        self.connected = False
        
        # Initialize embedding model
        self.load_embedding_model()
    
    def load_embedding_model(self):
        """Load sentence transformer model for embeddings"""
        try:
            logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
            self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
            
            # Test embedding
            test_text = "This is a test sentence for embedding."
            test_embedding = self.embedding_model.encode([test_text])
            logger.info(f"Model loaded successfully. Embedding dimension: {test_embedding.shape[1]}")
            
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def connect_to_milvus(self):
        """Connect to Milvus server"""
        try:
            connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)
            self.connected = True
            logger.info(f"Connected to Milvus at {MILVUS_HOST}:{MILVUS_PORT}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            raise
    
    def create_collection(self, drop_existing: bool = False):
        """Create Milvus collection for paper embeddings"""
        if not self.connected:
            self.connect_to_milvus()
        
        # Drop existing collection if requested
        if drop_existing and utility.has_collection(MILVUS_COLLECTION_NAME):
            utility.drop_collection(MILVUS_COLLECTION_NAME)
            logger.info(f"Dropped existing collection: {MILVUS_COLLECTION_NAME}")
        
        # Check if collection already exists
        if utility.has_collection(MILVUS_COLLECTION_NAME):
            self.collection = Collection(MILVUS_COLLECTION_NAME)
            logger.info(f"Using existing collection: {MILVUS_COLLECTION_NAME}")
            return
        
        # Define collection schema
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="paper_id", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="chunk_id", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="conference", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="year", dtype=DataType.INT64),
            FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=1000),
            FieldSchema(name="authors", dtype=DataType.VARCHAR, max_length=2000),
            FieldSchema(name="abstract", dtype=DataType.VARCHAR, max_length=5000),
            FieldSchema(name="chunk_text", dtype=DataType.VARCHAR, max_length=5000),
            FieldSchema(name="chunk_index", dtype=DataType.INT64),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=VECTOR_DIMENSION),
            FieldSchema(name="pdf_path", dtype=DataType.VARCHAR, max_length=500),
            FieldSchema(name="url", dtype=DataType.VARCHAR, max_length=500),
            FieldSchema(name="word_count", dtype=DataType.INT64),
            FieldSchema(name="page_count", dtype=DataType.INT64),
            FieldSchema(name="file_size", dtype=DataType.INT64)
        ]
        
        schema = CollectionSchema(fields, f"AI Conference Papers - {MILVUS_COLLECTION_NAME}")
        
        # Create collection
        self.collection = Collection(MILVUS_COLLECTION_NAME, schema)
        logger.info(f"Created collection: {MILVUS_COLLECTION_NAME}")
    
    def create_index(self):
        """Create index for vector similarity search"""
        if not self.collection:
            raise ValueError("Collection not initialized")
        
        index_params = {
            "metric_type": MILVUS_METRIC_TYPE,
            "index_type": MILVUS_INDEX_TYPE,
            "params": {"nlist": 1024}
        }
        
        # Create index on embedding field
        self.collection.create_index("embedding", index_params)
        logger.info(f"Created index on embedding field with {MILVUS_INDEX_TYPE}")
    
    def generate_embeddings(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Generate embeddings for text chunks"""
        if not texts:
            return np.array([])
        
        # Filter out empty texts
        valid_texts = [text if text else "empty" for text in texts]
        
        # Generate embeddings in batches
        embeddings = []
        for i in tqdm(range(0, len(valid_texts), batch_size), desc="Generating embeddings"):
            batch_texts = valid_texts[i:i + batch_size]
            batch_embeddings = self.embedding_model.encode(batch_texts, show_progress_bar=False)
            embeddings.append(batch_embeddings)
        
        return np.vstack(embeddings)
    
    def prepare_paper_data(self, text_data: Dict) -> List[Dict]:
        """Prepare paper data for insertion into Milvus"""
        paper_info = text_data.get('paper_info', {})
        chunks = text_data.get('chunks', [])
        metadata = text_data.get('metadata', {})
        
        if not chunks:
            return []
        
        # Generate embeddings for all chunks
        chunk_texts = [chunk.get('text', '') for chunk in chunks]
        embeddings = self.generate_embeddings(chunk_texts)
        
        # Prepare records
        records = []
        for i, chunk in enumerate(chunks):
            record = {
                'paper_id': self.generate_paper_id(paper_info),
                'chunk_id': chunk.get('chunk_id', f"chunk_{i}"),
                'conference': paper_info.get('conference', 'unknown'),
                'year': int(paper_info.get('year', 0)),
                'title': paper_info.get('title', '')[:1000],  # Truncate if too long
                'authors': paper_info.get('authors', '')[:2000],
                'abstract': paper_info.get('abstract', '')[:5000],
                'chunk_text': chunk.get('text', '')[:5000],
                'chunk_index': chunk.get('chunk_index', i),
                'embedding': embeddings[i].tolist(),
                'pdf_path': text_data.get('pdf_path', '')[:500],
                'url': paper_info.get('url', '')[:500],
                'word_count': chunk.get('word_count', 0),
                'page_count': metadata.get('page_count', 0),
                'file_size': metadata.get('file_size', 0)
            }
            records.append(record)
        
        return records
    
    def generate_paper_id(self, paper_info: Dict) -> str:
        """Generate unique paper ID"""
        conference = paper_info.get('conference', 'unknown')
        year = paper_info.get('year', 0)
        title = paper_info.get('title', 'untitled')
        
        # Create hash from title and URL
        import hashlib
        text_to_hash = f"{conference}_{year}_{title}_{paper_info.get('url', '')}"
        paper_id = hashlib.md5(text_to_hash.encode()).hexdigest()[:12]
        
        return f"{conference}_{year}_{paper_id}"
    
    def insert_paper_data(self, records: List[Dict]) -> bool:
        """Insert paper data into Milvus collection"""
        if not records:
            return False
        
        try:
            # Prepare data for insertion
            insert_data = []
            for field_name in ["paper_id", "chunk_id", "conference", "year", "title", 
                             "authors", "abstract", "chunk_text", "chunk_index", 
                             "embedding", "pdf_path", "url", "word_count", 
                             "page_count", "file_size"]:
                field_data = [record[field_name] for record in records]
                insert_data.append(field_data)
            
            # Insert data
            mr = self.collection.insert(insert_data)
            
            # Flush to ensure data is written
            self.collection.flush()
            
            logger.info(f"Inserted {len(records)} records")
            return True
            
        except Exception as e:
            logger.error(f"Failed to insert data: {e}")
            return False
    
    def load_collection(self):
        """Load collection into memory for search"""
        if not self.collection:
            raise ValueError("Collection not initialized")
        
        self.collection.load()
        logger.info("Collection loaded into memory")
    
    def search_similar_papers(self, query_text: str, top_k: int = 10, 
                            conference_filter: Optional[str] = None,
                            year_filter: Optional[int] = None) -> List[Dict]:
        """Search for similar papers using vector similarity"""
        if not self.collection:
            raise ValueError("Collection not initialized")
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query_text])
        
        # Prepare search parameters
        search_params = {"metric_type": MILVUS_METRIC_TYPE, "params": {"nprobe": 10}}
        
        # Build filter expression
        filter_expr = []
        if conference_filter:
            filter_expr.append(f'conference == "{conference_filter}"')
        if year_filter:
            filter_expr.append(f'year == {year_filter}')
        
        expr = " && ".join(filter_expr) if filter_expr else None
        
        # Perform search
        results = self.collection.search(
            data=query_embedding,
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            expr=expr,
            output_fields=["paper_id", "title", "authors", "conference", "year", 
                          "chunk_text", "chunk_index", "url"]
        )
        
        # Format results
        formatted_results = []
        for hits in results:
            for hit in hits:
                result = {
                    'score': float(hit.score),
                    'distance': float(hit.distance),
                    'paper_id': hit.entity.get('paper_id'),
                    'title': hit.entity.get('title'),
                    'authors': hit.entity.get('authors'),
                    'conference': hit.entity.get('conference'),
                    'year': hit.entity.get('year'),
                    'chunk_text': hit.entity.get('chunk_text'),
                    'chunk_index': hit.entity.get('chunk_index'),
                    'url': hit.entity.get('url')
                }
                formatted_results.append(result)
        
        return formatted_results
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection"""
        if not self.collection:
            return {}
        
        stats = {
            'name': self.collection.name,
            'num_entities': self.collection.num_entities,
            'schema': str(self.collection.schema),
            'indexes': [str(index) for index in self.collection.indexes]
        }
        
        return stats
    
    def process_all_extracted_texts(self, limit: Optional[int] = None) -> Dict:
        """Process all extracted text files and insert into Milvus"""
        logger.info("Processing extracted text files...")
        
        # Find all extracted text files
        text_files = []
        for conf_dir in os.listdir(EXTRACTED_TEXT_DIR):
            conf_path = os.path.join(EXTRACTED_TEXT_DIR, conf_dir)
            if os.path.isdir(conf_path):
                for text_file in os.listdir(conf_path):
                    if text_file.endswith('.json'):
                        text_files.append(os.path.join(conf_path, text_file))
        
        if limit:
            text_files = text_files[:limit]
        
        logger.info(f"Found {len(text_files)} text files to process")
        
        # Process files
        total_records = 0
        successful_files = 0
        failed_files = 0
        
        for text_file in tqdm(text_files, desc="Processing text files"):
            try:
                with open(text_file, 'r', encoding='utf-8') as f:
                    text_data = json.load(f)
                
                # Prepare data for Milvus
                records = self.prepare_paper_data(text_data)
                
                if records:
                    # Insert into Milvus
                    if self.insert_paper_data(records):
                        total_records += len(records)
                        successful_files += 1
                    else:
                        failed_files += 1
                else:
                    failed_files += 1
                    
            except Exception as e:
                logger.error(f"Error processing {text_file}: {e}")
                failed_files += 1
        
        return {
            'total_files': len(text_files),
            'successful_files': successful_files,
            'failed_files': failed_files,
            'total_records': total_records
        }


def main():
    """Main function to set up vector database"""
    print("Setting up Milvus Vector Database...")
    
    try:
        # Initialize vector database
        vdb = VectorDatabase()
        
        # Connect to Milvus
        vdb.connect_to_milvus()
        
        # Create collection
        vdb.create_collection(drop_existing=True)
        
        # Create index
        vdb.create_index()
        
        # Process extracted texts (limit to 5 for testing)
        stats = vdb.process_all_extracted_texts(limit=5)
        
        print("\n" + "="*60)
        print("VECTOR DATABASE SETUP SUMMARY")
        print("="*60)
        print(f"Total files processed: {stats['total_files']}")
        print(f"Successful: {stats['successful_files']}")
        print(f"Failed: {stats['failed_files']}")
        print(f"Total records inserted: {stats['total_records']}")
        
        # Load collection for search
        vdb.load_collection()
        
        # Test search
        print("\nTesting search functionality...")
        results = vdb.search_similar_papers("neural networks deep learning", top_k=3)
        
        print(f"Found {len(results)} similar papers:")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title'][:60]}... (Score: {result['score']:.3f})")
        
        # Save stats
        stats_file = os.path.join(RESULTS_DIR, 'vector_database_stats.json')
        os.makedirs(RESULTS_DIR, exist_ok=True)
        
        collection_stats = vdb.get_collection_stats()
        all_stats = {**stats, 'collection_stats': collection_stats}
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(all_stats, f, indent=2)
        
        print(f"\nStats saved to: {stats_file}")
        
    except Exception as e:
        logger.error(f"Error in main process: {e}")
        raise


if __name__ == "__main__":
    main()