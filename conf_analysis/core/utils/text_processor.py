"""
Text Processing and Vectorization Pipeline
Combined text extraction from PDFs and vectorization pipeline for AI conference papers.
"""

import os
import json
import asyncio
import logging
import time
import re
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from tqdm import tqdm

# PDF processing
import PyPDF2
import fitz  # pymupdf - better PDF text extraction

# Text processing
import nltk
from sentence_transformers import SentenceTransformer

# Add project root to path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import *

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')


class TextExtractor:
    """Extract and process text from PDF files"""
    
    def __init__(self):
        self.extracted_count = 0
        self.failed_count = 0
        self.skipped_count = 0
        
        # Create directories
        os.makedirs(EXTRACTED_TEXT_DIR, exist_ok=True)
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers/footers (common patterns)
        text = re.sub(r'\n\d+\s*\n', '\n', text)
        text = re.sub(r'\nPage \d+\n', '\n', text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[.]{3,}', '...', text)
        text = re.sub(r'[-]{3,}', '---', text)
        
        # Normalize quotes
        text = re.sub(r'[""]', '"', text)
        text = re.sub(r'['']', "'", text)
        
        # Remove control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
        
        return text.strip()
    
    def extract_pdf_text_pymupdf(self, pdf_path: Path) -> str:
        """Extract text using PyMuPDF (better quality)"""
        try:
            doc = fitz.open(pdf_path)
            text_blocks = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                if text.strip():
                    text_blocks.append(text)
            
            doc.close()
            return '\n'.join(text_blocks)
            
        except Exception as e:
            logger.error(f"PyMuPDF extraction failed for {pdf_path}: {e}")
            return ""
    
    def extract_pdf_text_pypdf2(self, pdf_path: Path) -> str:
        """Extract text using PyPDF2 (fallback)"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_blocks = []
                
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text.strip():
                        text_blocks.append(text)
                
                return '\n'.join(text_blocks)
                
        except Exception as e:
            logger.error(f"PyPDF2 extraction failed for {pdf_path}: {e}")
            return ""
    
    def extract_text_from_pdf(self, pdf_path: Path) -> Dict[str, any]:
        """Extract text from PDF using multiple methods"""
        result = {
            'pdf_path': str(pdf_path),
            'filename': pdf_path.name,
            'text': '',
            'word_count': 0,
            'char_count': 0,
            'extraction_method': '',
            'success': False,
            'error': None
        }
        
        # Try PyMuPDF first (better quality)
        text = self.extract_pdf_text_pymupdf(pdf_path)
        if text and len(text.strip()) > 100:  # Minimum text threshold
            result['extraction_method'] = 'pymupdf'
        else:
            # Fallback to PyPDF2
            text = self.extract_pdf_text_pypdf2(pdf_path)
            if text and len(text.strip()) > 100:
                result['extraction_method'] = 'pypdf2'
            else:
                result['error'] = 'Insufficient text extracted'
                return result
        
        # Clean the text
        cleaned_text = self.clean_text(text)
        
        if len(cleaned_text) < 100:
            result['error'] = 'Text too short after cleaning'
            return result
        
        # Truncate if too long
        if len(cleaned_text) > MAX_TEXT_LENGTH:
            cleaned_text = cleaned_text[:MAX_TEXT_LENGTH]
            logger.warning(f"Text truncated for {pdf_path.name}")
        
        result['text'] = cleaned_text
        result['word_count'] = len(cleaned_text.split())
        result['char_count'] = len(cleaned_text)
        result['success'] = True
        
        return result
    
    def save_extracted_text(self, result: Dict, output_dir: Path):
        """Save extracted text to file"""
        if not result['success']:
            return
        
        # Create conference subdirectory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate text filename (same as PDF but .txt)
        pdf_name = Path(result['filename']).stem
        text_file = output_dir / f"{pdf_name}.txt"
        
        # Save text content
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(result['text'])
        
        # Save metadata
        metadata = {k: v for k, v in result.items() if k != 'text'}
        metadata_file = output_dir / f"{pdf_name}_metadata.json"
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def extract_conference_pdfs(self, conference: str) -> Dict:
        """Extract text from all PDFs for a specific conference"""
        pdf_dir = Path(PDF_DATA_DIR) / conference
        output_dir = Path(EXTRACTED_TEXT_DIR) / conference
        
        if not pdf_dir.exists():
            logger.warning(f"PDF directory not found: {pdf_dir}")
            return {'extracted': 0, 'failed': 0, 'skipped': 0}
        
        pdf_files = list(pdf_dir.glob("*.pdf"))
        if not pdf_files:
            logger.warning(f"No PDF files found in {pdf_dir}")
            return {'extracted': 0, 'failed': 0, 'skipped': 0}
        
        stats = {'extracted': 0, 'failed': 0, 'skipped': 0}
        
        for pdf_path in tqdm(pdf_files, desc=f"Extracting {conference}"):
            # Check if already extracted
            pdf_name = pdf_path.stem
            text_file = output_dir / f"{pdf_name}.txt"
            
            if text_file.exists():
                stats['skipped'] += 1
                continue
            
            # Extract text
            result = self.extract_text_from_pdf(pdf_path)
            
            if result['success']:
                self.save_extracted_text(result, output_dir)
                stats['extracted'] += 1
                self.extracted_count += 1
            else:
                logger.error(f"Failed to extract {pdf_path.name}: {result.get('error', 'Unknown error')}")
                stats['failed'] += 1
                self.failed_count += 1
        
        return stats
    
    def extract_all_conferences(self, conferences: List[str] = None) -> Dict:
        """Extract text from PDFs for all conferences"""
        pdf_base_dir = Path(PDF_DATA_DIR)
        
        if not pdf_base_dir.exists():
            logger.error(f"PDF base directory not found: {pdf_base_dir}")
            return {}
        
        # Get available conferences
        available_conferences = [d.name for d in pdf_base_dir.iterdir() if d.is_dir()]
        
        if conferences:
            available_conferences = [c for c in available_conferences if c in conferences]
        
        total_stats = {'extracted': 0, 'failed': 0, 'skipped': 0}
        conference_stats = {}
        
        for conference in available_conferences:
            logger.info(f"Processing {conference}...")
            stats = self.extract_conference_pdfs(conference)
            conference_stats[conference] = stats
            
            # Update totals
            for key in total_stats:
                total_stats[key] += stats[key]
            
            logger.info(f"Completed {conference}: {stats}")
        
        logger.info(f"Total extraction stats: {total_stats}")
        return {'total': total_stats, 'by_conference': conference_stats}


class TextChunker:
    """Split text into chunks for vectorization"""
    
    def __init__(self, chunk_size: int = CHUNK_SIZE_TEXT, chunk_overlap: int = CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split_text_into_chunks(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence ending within the last 200 characters
                sentence_end = text.rfind('.', end - 200, end)
                if sentence_end > start:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            if start <= 0:
                break
        
        return chunks
    
    def create_paper_chunks(self, text: str, paper_metadata: Dict) -> List[Dict]:
        """Create chunks with metadata for a paper"""
        chunks = self.split_text_into_chunks(text)
        
        paper_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_data = {
                'text': chunk,
                'chunk_id': i,
                'total_chunks': len(chunks),
                'paper_id': paper_metadata.get('paper_id', ''),
                'title': paper_metadata.get('title', ''),
                'conference': paper_metadata.get('conference', ''),
                'year': paper_metadata.get('year', ''),
                'authors': paper_metadata.get('authors', []),
                'abstract': paper_metadata.get('abstract', ''),
            }
            paper_chunks.append(chunk_data)
        
        return paper_chunks


class VectorizationPipeline:
    """Complete pipeline for text processing and vectorization"""
    
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        self.model_name = model_name
        self.model = None
        self.text_extractor = TextExtractor()
        self.text_chunker = TextChunker()
        
        # Statistics
        self.pipeline_stats = {
            'start_time': None,
            'end_time': None,
            'papers_processed': 0,
            'chunks_created': 0,
            'vectors_generated': 0,
            'errors': 0
        }
    
    def load_embedding_model(self):
        """Load the sentence transformer model"""
        if self.model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            try:
                self.model = SentenceTransformer(self.model_name)
                logger.info("Embedding model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise
    
    def generate_embeddings(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Generate embeddings for text chunks"""
        if not self.model:
            self.load_embedding_model()
        
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.model.encode(batch, show_progress_bar=False)
            embeddings.extend(batch_embeddings.tolist())
        
        return embeddings
    
    def process_extracted_texts(self, conference: str = None) -> Dict:
        """Process extracted text files and create vectors"""
        extracted_base_dir = Path(EXTRACTED_TEXT_DIR)
        
        if conference:
            conferences = [conference] if (extracted_base_dir / conference).exists() else []
        else:
            conferences = [d.name for d in extracted_base_dir.iterdir() if d.is_dir()]
        
        all_chunks = []
        processed_papers = 0
        
        for conf in conferences:
            conf_dir = extracted_base_dir / conf
            text_files = list(conf_dir.glob("*.txt"))
            
            logger.info(f"Processing {len(text_files)} text files for {conf}")
            
            for text_file in tqdm(text_files, desc=f"Processing {conf}"):
                try:
                    # Load text content
                    with open(text_file, 'r', encoding='utf-8') as f:
                        text = f.read()
                    
                    # Load metadata if available
                    metadata_file = text_file.parent / f"{text_file.stem}_metadata.json"
                    paper_metadata = {'conference': conf}
                    
                    if metadata_file.exists():
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            file_metadata = json.load(f)
                            paper_metadata.update(file_metadata)
                    
                    # Parse paper info from filename if metadata missing
                    if 'title' not in paper_metadata:
                        paper_metadata['title'] = text_file.stem
                    
                    # Create chunks
                    chunks = self.text_chunker.create_paper_chunks(text, paper_metadata)
                    all_chunks.extend(chunks)
                    processed_papers += 1
                    
                except Exception as e:
                    logger.error(f"Error processing {text_file}: {e}")
                    self.pipeline_stats['errors'] += 1
        
        # Generate embeddings
        if all_chunks:
            logger.info(f"Generating embeddings for {len(all_chunks)} chunks...")
            texts = [chunk['text'] for chunk in all_chunks]
            embeddings = self.generate_embeddings(texts)
            
            # Add embeddings to chunks
            for chunk, embedding in zip(all_chunks, embeddings):
                chunk['embedding'] = embedding
            
            self.pipeline_stats['vectors_generated'] = len(embeddings)
        
        self.pipeline_stats['papers_processed'] = processed_papers
        self.pipeline_stats['chunks_created'] = len(all_chunks)
        
        return {
            'chunks': all_chunks,
            'stats': self.pipeline_stats
        }
    
    def run_full_pipeline(self, conferences: List[str] = None, 
                         extract_text: bool = True, 
                         generate_vectors: bool = True) -> Dict:
        """Run the complete text processing pipeline"""
        self.pipeline_stats['start_time'] = datetime.now()
        
        results = {
            'extraction_stats': {},
            'vectorization_stats': {},
            'total_chunks': 0,
            'success': False
        }
        
        try:
            # Step 1: Extract text from PDFs
            if extract_text:
                logger.info("Starting text extraction phase...")
                extraction_results = self.text_extractor.extract_all_conferences(conferences)
                results['extraction_stats'] = extraction_results
                logger.info(f"Text extraction completed: {extraction_results.get('total', {})}")
            
            # Step 2: Process texts and generate vectors
            if generate_vectors:
                logger.info("Starting vectorization phase...")
                vector_results = self.process_extracted_texts()
                results['vectorization_stats'] = vector_results['stats']
                results['total_chunks'] = len(vector_results['chunks'])
                
                # Save vectorized data
                self.save_vectorized_data(vector_results['chunks'])
                
                logger.info(f"Vectorization completed: {vector_results['stats']}")
            
            results['success'] = True
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            results['error'] = str(e)
        
        finally:
            self.pipeline_stats['end_time'] = datetime.now()
            duration = self.pipeline_stats['end_time'] - self.pipeline_stats['start_time']
            logger.info(f"Pipeline completed in {duration}")
        
        return results
    
    def save_vectorized_data(self, chunks: List[Dict]):
        """Save vectorized chunks to files"""
        output_dir = Path(PROCESSED_DATA_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save chunks data
        chunks_file = output_dir / 'vectorized_chunks.json'
        
        # Remove embeddings for JSON serialization
        chunks_for_json = []
        for chunk in chunks:
            chunk_copy = chunk.copy()
            chunk_copy.pop('embedding', None)  # Remove embedding for JSON
            chunks_for_json.append(chunk_copy)
        
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(chunks_for_json, f, indent=2, ensure_ascii=False)
        
        # Save embeddings separately (numpy format would be better but keeping JSON for compatibility)
        embeddings_file = output_dir / 'embeddings.json'
        embeddings = [chunk['embedding'] for chunk in chunks if 'embedding' in chunk]
        
        with open(embeddings_file, 'w') as f:
            json.dump(embeddings, f)
        
        # Save pipeline statistics
        stats_file = output_dir / 'pipeline_stats.json'
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.pipeline_stats, f, indent=2, default=str, ensure_ascii=False)
        
        logger.info(f"Vectorized data saved to {output_dir}")


def main():
    """Main CLI interface for text processing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Text Processing and Vectorization Pipeline')
    parser.add_argument('action', choices=['extract', 'vectorize', 'pipeline'],
                       help='Action to perform')
    parser.add_argument('--conferences', nargs='+', 
                       choices=['ICML', 'NeuRIPS', 'ICLR', 'AAAI', 'IJCAI'],
                       help='Conferences to process')
    parser.add_argument('--no-extract', action='store_true',
                       help='Skip text extraction phase')
    parser.add_argument('--no-vectorize', action='store_true',
                       help='Skip vectorization phase')
    
    args = parser.parse_args()
    
    if args.action == 'extract':
        extractor = TextExtractor()
        results = extractor.extract_all_conferences(args.conferences)
        print(f"Extraction completed: {results}")
    
    elif args.action == 'vectorize':
        pipeline = VectorizationPipeline()
        results = pipeline.process_extracted_texts()
        print(f"Vectorization completed: {results['stats']}")
    
    elif args.action == 'pipeline':
        pipeline = VectorizationPipeline()
        results = pipeline.run_full_pipeline(
            conferences=args.conferences,
            extract_text=not args.no_extract,
            generate_vectors=not args.no_vectorize
        )
        print(f"Pipeline completed: {results}")


if __name__ == "__main__":
    main()