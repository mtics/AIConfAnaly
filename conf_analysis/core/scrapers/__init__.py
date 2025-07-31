"""
Conference paper scrapers
"""

from .icml_scraper import ICMLScraper
from .neurips_scraper import NeuRIPSScraper
from .iclr_scraper import ICLRScraper
from .aaai_scraper import AAAIScraper
from .ijcai_scraper import IJCAIScraper

__all__ = [
    'ICMLScraper',
    'NeuRIPSScraper', 
    'ICLRScraper',
    'AAAIScraper',
    'IJCAIScraper'
]