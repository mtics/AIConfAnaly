"""
ICML paper scraper
"""

from .base_scraper import BaseScraper
from typing import List, Dict
import re
import requests


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
        
        # OpenReview venues for ICML
        self.openreview_venues = {
            2025: "ICML.cc/2025/Conference"
        }
        
        # OpenReview API endpoint
        self.openreview_api = "https://api2.openreview.net/"
    
    def get_papers_for_year(self, year: int) -> List[Dict]:
        """Extract ICML papers for a specific year"""
        # Check if it's an OpenReview year
        if year in self.openreview_venues:
            return self._scrape_from_openreview(year)
        
        # Traditional volume-based scraping for older years
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
    
    def _scrape_from_openreview(self, year: int) -> List[Dict]:
        """Scrape ICML papers from OpenReview API"""
        venue_id = self.openreview_venues[year]
        print(f"  🌐 Scraping ICML {year} from OpenReview API with venue: {venue_id}")
        
        papers = []
        
        try:
            # Use OpenReview API V2
            url = f"{self.openreview_api}notes"
            
            # Query parameters for API V2
            params = {
                'content.venueid': venue_id,
                'details': 'replyCount,invitation,original',
                'limit': 1000,
                'offset': 0,
                'sort': 'cdate:desc'
            }
            
            offset = 0
            max_requests = 20
            request_count = 0
            
            print(f"     Querying OpenReview API V2...")
            
            while request_count < max_requests:
                params['offset'] = offset
                
                try:
                    response = self.session.get(url, params=params, timeout=30)
                    response.raise_for_status()
                    
                    data = response.json()
                    notes = data.get('notes', [])
                    
                    if not notes:
                        break
                    
                    print(f"     Batch {request_count + 1}: {len(notes)} notes")
                    
                    for note in notes:
                        try:
                            content = note.get('content', {})
                            
                            # Handle title field (may be dict in V2)
                            title_raw = content.get('title', '')
                            if isinstance(title_raw, dict):
                                title = title_raw.get('value', '')
                            elif isinstance(title_raw, str):
                                title = title_raw
                            else:
                                title = str(title_raw) if title_raw else ''
                            
                            title = title.strip()
                            if not title or len(title) < 5:
                                continue
                            
                            # Check if this is a valid paper
                            invitation = note.get('invitation', '')
                            if any(term in invitation.lower() for term in ['review', 'comment', 'meta_review', 'decision', 'withdrawal']):
                                continue
                            
                            # Extract authors
                            authors_raw = content.get('authors', [])
                            if isinstance(authors_raw, list):
                                authors = ', '.join(str(author) for author in authors_raw)
                            elif isinstance(authors_raw, dict):
                                authors = authors_raw.get('value', '')
                            elif isinstance(authors_raw, str):
                                authors = authors_raw
                            else:
                                authors = ''
                            
                            # Extract abstract
                            abstract_raw = content.get('abstract', '')
                            if isinstance(abstract_raw, dict):
                                abstract = abstract_raw.get('value', '')
                            elif isinstance(abstract_raw, str):
                                abstract = abstract_raw
                            else:
                                abstract = str(abstract_raw) if abstract_raw else ''
                            
                            paper = {
                                'title': title,
                                'authors': authors,
                                'abstract': abstract.strip(),
                                'year': year,
                                'conference': 'ICML',
                                'url': f"https://openreview.net/forum?id={note.get('id', '')}"
                            }
                            papers.append(paper)
                            
                        except Exception as e:
                            continue
                    
                    offset += len(notes)
                    request_count += 1
                    
                    if len(notes) < 1000:  # Last batch
                        break
                        
                except Exception as e:
                    print(f"     ❌ API request failed: {e}")
                    break
            
            print(f"     ✅ Successfully extracted {len(papers)} papers from ICML {year}")
            return papers
            
        except Exception as e:
            print(f"     ❌ Failed to scrape ICML {year} from OpenReview: {e}")
            return []
    
    def _extract_paper_details(self, paper_url: str, title: str, year: int) -> Dict:
        """Extract detailed paper information from individual paper page"""
        try:
            # Limit requests to avoid overwhelming the server
            response = self.session.get(paper_url, timeout=10)
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for authors
            authors = ""
            author_elements = soup.find_all(['span', 'div', 'p'], class_=re.compile(r'author', re.I))
            if author_elements:
                authors = ', '.join([elem.get_text().strip() for elem in author_elements])
            
            # Look for abstract
            abstract = ""
            abstract_element = soup.find(['div', 'p'], class_=re.compile(r'abstract', re.I))
            if abstract_element:
                abstract = abstract_element.get_text().strip()
            
            return {
                'title': title,
                'authors': authors,
                'abstract': abstract,
                'year': year,
                'conference': 'ICML',
                'url': paper_url
            }
            
        except Exception as e:
            # Return None if we can't get details, caller will handle fallback
            return None