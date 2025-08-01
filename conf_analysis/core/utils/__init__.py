"""
Utils module for conference paper analysis
Consolidated utilities for configuration, PDF management, text processing, and vectorization
"""

from .config import *
from .pdf_manager import PDFDownloader, PDFManager
from .text_processor import TextExtractor, TextChunker, VectorizationPipeline
from .system_setup import *

__all__ = [
    # Configuration
    'CONFERENCES', 'DATA_DIR', 'RAW_DATA_DIR', 'PROCESSED_DATA_DIR',
    'PDF_DATA_DIR', 'EXTRACTED_TEXT_DIR', 'RESULTS_DIR', 'FIGURES_DIR',
    'DASHBOARD_DIR', 'OUTPUTS_DIR',
    
    # PDF Management
    'PDFDownloader', 'PDFManager',
    
    # Text Processing
    'TextExtractor', 'TextChunker', 'VectorizationPipeline',
]