"""
NeuRIPS paper scraper
"""

from .base_scraper import BaseScraper
from typing import List, Dict
import re
import requests


class NeuRIPSScraper(BaseScraper):
    def __init__(self):
        super().__init__("NeuRIPS", "https://papers.nips.cc/")
        
        # OpenReview venues for NeurIPS
        self.openreview_venues = {
            2025: "NeurIPS.cc/2025/Conference"
        }
        
        # OpenReview API endpoint
        self.openreview_api = "https://api2.openreview.net/"
    
    def get_papers_for_year(self, year: int) -> List[Dict]:
        """Extract NeuRIPS papers for a specific year"""
        # Check if it's an OpenReview year
        if year in self.openreview_venues:
            return self._scrape_from_openreview(year)
        
        # Traditional scraping for older years
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
    
    def _scrape_from_openreview(self, year: int) -> List[Dict]:
        """Scrape NeurIPS papers from OpenReview API"""
        venue_id = self.openreview_venues[year]
        print(f"  🌐 Scraping NeurIPS {year} from OpenReview API with venue: {venue_id}")
        
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
                        print(f"     No papers found for NeurIPS {year} (conference may not have started yet)")
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
                                'conference': 'NeuRIPS',
                                'url': f"https://openreview.net/forum?id={note.get('id', '')}"
                            }
                            papers.append(paper)
                            
                        except Exception as e:
                            continue
                    
                    offset += len(notes)
                    request_count += 1
                    
                    if len(notes) < 1000:  # Last batch
                        break
                        
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 404:
                        print(f"     ℹ️ NeurIPS {year} data not found (conference may not have started yet)")
                        return []
                    else:
                        print(f"     ❌ API request failed: {e}")
                        break
                except Exception as e:
                    print(f"     ❌ API request failed: {e}")
                    break
            
            if papers:
                print(f"     ✅ Successfully extracted {len(papers)} papers from NeurIPS {year}")
            else:
                print(f"     ℹ️ No papers found for NeurIPS {year}")
            
            return papers
            
        except Exception as e:
            print(f"     ❌ Failed to scrape NeurIPS {year} from OpenReview: {e}")
            return []