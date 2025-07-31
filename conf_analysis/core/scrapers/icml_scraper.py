"""
ICML paper scraper
"""

from .base_scraper import BaseScraper
from typing import List, Dict
import re


class ICMLScraper(BaseScraper):
    def __init__(self):
        super().__init__("ICML", "https://proceedings.mlr.press/")
        
        # Volume mappings for ICML
        self.volume_map = {
            2018: 'v80',
            2019: 'v97',
            2020: 'v119',
            2021: 'v139',
            2022: 'v162',
            2023: 'v202',
            2024: 'v235'
        }
    
    def get_papers_for_year(self, year: int) -> List[Dict]:
        """Extract ICML papers for a specific year"""
        if year not in self.volume_map:
            raise ValueError(f"Volume mapping not found for year {year}")
            
        volume = self.volume_map[year]
        url = f"{self.base_url}{volume}/"
        
        soup = self.fetch_page(url)
        papers = []
        
        # Find all paper entries
        paper_divs = soup.find_all('div', class_='paper')
        
        for paper_div in paper_divs:
            try:
                # Extract title
                title_elem = paper_div.find('p', class_='title')
                if not title_elem:
                    continue
                    
                title = title_elem.get_text().strip()
                
                # Extract authors
                authors_elem = paper_div.find('p', class_='details')
                authors = authors_elem.get_text().strip() if authors_elem else ""
                
                # Extract abstract (try to find abstract link and fetch it)
                abstract = ""
                abstract_link = paper_div.find('a', href=re.compile(r'.*\.html$'))
                abstract_url = ""
                if abstract_link:
                    try:
                        # Fix URL construction - avoid double base URL
                        href = abstract_link['href']
                        if href.startswith('http'):
                            abstract_url = href
                        else:
                            abstract_url = self.base_url + volume + '/' + href
                        
                        abstract_soup = self.fetch_page(abstract_url, delay=0.5)
                        abstract_div = abstract_soup.find('div', id='abstract')
                        if abstract_div:
                            abstract = abstract_div.get_text().strip()
                    except:
                        pass
                
                paper = {
                    'title': title,
                    'authors': authors,
                    'abstract': abstract,
                    'year': year,
                    'conference': 'ICML',
                    'url': abstract_url if abstract_link else ""
                }
                papers.append(paper)
                
            except Exception as e:
                print(f"Error processing paper: {e}")
                continue
                
        return papers