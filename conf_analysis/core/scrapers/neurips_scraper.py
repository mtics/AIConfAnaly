"""
NeuRIPS paper scraper
"""

from .base_scraper import BaseScraper
from typing import List, Dict
import re


class NeuRIPSScraper(BaseScraper):
    def __init__(self):
        super().__init__("NeuRIPS", "https://papers.nips.cc/")
    
    def get_papers_for_year(self, year: int) -> List[Dict]:
        """Extract NeuRIPS papers for a specific year"""
        url = f"{self.base_url}paper/{year}"
        
        soup = self.fetch_page(url)
        papers = []
        
        # Find all paper links
        paper_links = soup.find_all('a', href=re.compile(r'/paper/\d+/hash/.*'))
        
        for link in paper_links:
            try:
                paper_url = f"https://papers.nips.cc{link['href']}"
                
                # Fetch individual paper page
                paper_soup = self.fetch_page(paper_url, delay=0.5)
                
                # Extract title
                title_elem = paper_soup.find('h4')
                if not title_elem:
                    continue
                title = title_elem.get_text().strip()
                
                # Extract authors
                authors_elem = paper_soup.find('h4').find_next('p')
                authors = authors_elem.get_text().strip() if authors_elem else ""
                
                # Extract abstract
                abstract = ""
                abstract_elem = paper_soup.find('h4', string='Abstract')
                if abstract_elem:
                    abstract_p = abstract_elem.find_next('p')
                    if abstract_p:
                        abstract = abstract_p.get_text().strip()
                
                paper = {
                    'title': title,
                    'authors': authors,
                    'abstract': abstract,
                    'year': year,
                    'conference': 'NeuRIPS',
                    'url': paper_url
                }
                papers.append(paper)
                
            except Exception as e:
                print(f"Error processing paper: {e}")
                continue
                
        return papers