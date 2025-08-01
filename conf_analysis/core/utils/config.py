"""
Configuration file for conference paper analysis project
"""

# Conference URLs and patterns
CONFERENCES = {
    'ICML': {
        'base_url': 'https://proceedings.mlr.press/',
        'years': [2020, 2021, 2022, 2023, 2024, 2025]
    },
    'NeuRIPS': {
        'base_url': 'https://papers.nips.cc/',
        'years': [2020, 2021, 2022, 2023, 2024, 2025]
    },
    'ICLR': {
        'base_url': 'https://openreview.net/',
        'years': [2020, 2021, 2022, 2023, 2024, 2025]
    },
    'AAAI': {
        'base_url': 'https://aaai.org/',
        'years': [2020, 2021, 2022, 2023, 2024, 2025]
    },
    'IJCAI': {
        'base_url': 'https://www.ijcai.org/',
        'years': [2020, 2021, 2022, 2023, 2024, 2025]
    }
}

# Data storage paths
OUTPUTS_DIR = 'outputs'
DATA_DIR = f'{OUTPUTS_DIR}/data'
RAW_DATA_DIR = f'{DATA_DIR}/raw'
PROCESSED_DATA_DIR = f'{DATA_DIR}/processed'
PDF_DATA_DIR = f'{DATA_DIR}/pdfs'
EXTRACTED_TEXT_DIR = f'{DATA_DIR}/extracted_text'
RESULTS_DIR = f'{OUTPUTS_DIR}/results'
FIGURES_DIR = f'{RESULTS_DIR}/figures'
DASHBOARD_DIR = f'{OUTPUTS_DIR}/dashboard'

# Analysis parameters
MIN_KEYWORD_FREQ = 3
TOP_KEYWORDS_COUNT = 50
STOPWORDS_CUSTOM = [
    'learning', 'neural', 'network', 'networks', 'model', 'models',
    'method', 'methods', 'approach', 'approaches', 'algorithm', 'algorithms',
    'based', 'using', 'via', 'toward', 'towards', 'paper', 'study'
]

# Visualization settings
FIGURE_SIZE = (12, 8)
DPI = 300
COLOR_PALETTE = 'viridis'

# PDF Download settings
PDF_DOWNLOAD_DELAY = 2.0  # Delay between downloads in seconds (increased for better politeness)
MAX_CONCURRENT_DOWNLOADS = 2  # Reduced concurrency to avoid triggering bot detection
PDF_DOWNLOAD_TIMEOUT = 45  # Increased timeout for Cloudflare challenges
MAX_RETRIES = 3
CHUNK_SIZE = 8192

# Vector Database settings (Milvus)
MILVUS_HOST = 'localhost'
MILVUS_PORT = 19530
MILVUS_COLLECTION_NAME = 'ai_papers'
VECTOR_DIMENSION = 384  # For sentence-transformers/all-MiniLM-L6-v2
MILVUS_INDEX_TYPE = 'IVF_FLAT'
MILVUS_METRIC_TYPE = 'L2'

# Text processing settings
MAX_TEXT_LENGTH = 50000  # Maximum characters to process per paper
CHUNK_SIZE_TEXT = 1000   # Text chunk size for embedding
CHUNK_OVERLAP = 200      # Overlap between chunks
EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'

# Supported file formats
SUPPORTED_PDF_EXTENSIONS = ['.pdf']
SUPPORTED_TEXT_EXTENSIONS = ['.txt', '.md']