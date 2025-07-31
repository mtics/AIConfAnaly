"""
IJCAI paper scraper
"""

from .base_scraper import BaseScraper
from typing import List, Dict
import re


class IJCAIScraper(BaseScraper):
    def __init__(self):
        super().__init__("IJCAI", "https://www.ijcai.org/")
        
        # IJCAI proceedings URLs for each year
        self.url_map = {
            2018: "https://www.ijcai.org/proceedings/2018/",
            2019: "https://www.ijcai.org/proceedings/2019/",
            2020: "https://www.ijcai.org/proceedings/2020/",
            2021: "https://www.ijcai.org/proceedings/2021/",
            2022: "https://www.ijcai.org/proceedings/2022/",
            2023: "https://www.ijcai.org/proceedings/2023/",
            2024: "https://www.ijcai.org/proceedings/2024/"
        }
    
    def get_papers_for_year(self, year: int) -> List[Dict]:
        """Extract IJCAI papers for a specific year"""
        if year not in self.url_map:
            raise ValueError(f"URL mapping not found for year {year}")
            
        url = self.url_map[year]
        soup = self.fetch_page(url)
        papers = []
        
        # Find all paper entries
        paper_elements = soup.find_all('div', class_='paper_wrapper')
        
        for element in paper_elements:
            try:
                # Extract title from title div
                title_div = element.find('div', class_='title')
                if not title_div:
                    continue
                
                title = title_div.get_text().strip()
                if not title or len(title) < 10:  # Skip if title too short
                    continue
                
                # Extract authors from authors div
                authors = ""
                authors_div = element.find('div', class_='authors')
                if authors_div:
                    authors = authors_div.get_text().strip()
                
                # Extract PDF URL from details section
                paper_url = ""
                details_div = element.find('div', class_='details')
                if details_div:
                    pdf_link = details_div.find('a', href=re.compile(r'.*\.pdf$'))
                    if pdf_link:
                        paper_url = pdf_link['href']
                        if paper_url.startswith('/') or not paper_url.startswith('http'):
                            paper_url = url.rstrip('/') + '/' + paper_url.lstrip('/')
                
                # For IJCAI, abstracts are usually not available on listing page
                abstract = ""
                
                paper = {
                    'title': title,
                    'authors': authors,
                    'abstract': abstract,
                    'year': year,
                    'conference': 'IJCAI',
                    'url': paper_url
                }
                papers.append(paper)
                
            except Exception as e:
                print(f"Error processing paper: {e}")
                continue
                
        return papers