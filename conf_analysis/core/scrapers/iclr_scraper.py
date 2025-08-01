"""
ICLR paper scraper using OpenReview API
"""

from .base_scraper import BaseScraper
from typing import List, Dict
import requests
import json


class ICLRScraper(BaseScraper):
    def __init__(self):
        super().__init__("ICLR", "https://api2.openreview.net/")
        
        # ICLR venue IDs for each year
        self.venue_map = {
            2018: "ICLR.cc/2018/Conference",
            2019: "ICLR.cc/2019/Conference", 
            2020: "ICLR.cc/2020/Conference",
            2021: "ICLR.cc/2021/Conference",
            2022: "ICLR.cc/2022/Conference",
            2023: "ICLR.cc/2023/Conference",
            2024: "ICLR.cc/2024/Conference",
            2025: "ICLR.cc/2025/Conference"
        }
        
        # API V2 uses different endpoints and parameters
        self.api_version = "v2"
        
        # Backup URLs for years where API might not work
        self.backup_urls = {
            2024: "https://openreview.net/group?id=ICLR.cc/2024/Conference"
        }
        
        # Direct paper listing URLs (more reliable for recent years)
        self.direct_urls = {
            2024: "https://iclr.cc/virtual/2024/papers.html",
            2025: "https://iclr.cc/virtual/2025/papers.html"
        }
    
    def get_papers_for_year(self, year: int) -> List[Dict]:
        """Extract ICLR papers for a specific year using OpenReview API with fallbacks"""
        if year not in self.venue_map:
            raise ValueError(f"Venue mapping not found for year {year}")
            
        venue_id = self.venue_map[year]
        print(f"Scraping ICLR {year} using venue: {venue_id}")
        
        # Try direct paper listing first (most reliable for 2024)
        papers = []
        if year in self.direct_urls:
            print(f"Trying direct paper listing for ICLR {year}...")
            papers = self._scrape_direct_listing(year)
        
        # If no direct listing, try multiple API approaches
        if not papers:
            papers = self._try_api_approaches(venue_id, year)
        
        # If API fails and we have a backup URL, try web scraping
        if not papers and year in self.backup_urls:
            print(f"API returned no results, trying backup web scraping for {year}...")
            papers = self._scrape_from_web(year)
        
        # If still no papers and it's 2024, it might be that the data isn't available yet
        if not papers and year == 2024:
            print(f"⚠️ ICLR 2024 data may not be publicly available yet through API")
            print("   This is normal if the conference hasn't concluded or papers aren't finalized")
        
        return papers
    
    def _try_api_approaches(self, venue_id: str, year: int) -> List[Dict]:
        """Try multiple API V2 approaches to get papers"""
        papers = []
        
        # API V2 uses different query methods
        print(f"   Using OpenReview API V2 for {year}")
        
        # Method 1: Direct venue query (V2 style)
        papers = self._fetch_papers_by_venue_v2(venue_id, year)
        if papers:
            print(f"   ✅ Found {len(papers)} papers via venue query")
            return papers
        
        # Method 2: Try different invitation patterns (V2 compatible)
        invitation_patterns = [
            f'{venue_id}/-/Blind_Submission',
            f'{venue_id}/-/Submission', 
            f'{venue_id}/-/Decision',
            f'{venue_id}/-/Accept',
            f'{venue_id}/-/Acceptance_Decision',
            f'{venue_id}/-/Paper_Submission'
        ]
        
        for i, invitation in enumerate(invitation_patterns):
            print(f"   Trying V2 invitation pattern {i+1}/{len(invitation_patterns)}: {invitation}")
            
            try:
                batch_papers = self._fetch_papers_by_invitation_v2(invitation, year)
                if batch_papers:
                    papers.extend(batch_papers)
                    print(f"   ✅ Found {len(batch_papers)} papers with this pattern")
                    break  # Found papers, no need to try other patterns
                else:
                    print(f"   ❌ No papers found with this pattern")
                    
            except Exception as e:
                print(f"   ❌ Error with pattern: {e}")
                continue
        
        return papers
    
    def _fetch_papers_by_venue_v2(self, venue_id: str, year: int) -> List[Dict]:
        """Fetch papers using API V2 venue query"""
        url = f"{self.base_url}notes"
        
        # API V2 supports more flexible queries
        params = {
            'content.venueid': venue_id,
            'details': 'replyCount,invitation,original',
            'limit': 1000,
            'offset': 0,
            'sort': 'cdate:desc'  # Sort by creation date
        }
        
        papers = []
        offset = 0
        max_requests = 20  # Increased for V2
        request_count = 0
        
        print(f"      Querying V2 API with venue: {venue_id}")
        
        while request_count < max_requests:
            params['offset'] = offset
            
            try:
                response = self.session.get(url, params=params, timeout=20)
                response.raise_for_status()
                
                data = response.json()
                notes = data.get('notes', [])
                
                if not notes:
                    break
                
                print(f"      Batch {request_count + 1}: {len(notes)} notes")
                
                for note in notes:
                    try:
                        content = note.get('content', {})
                        
                        # More flexible filtering for V2
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
                        
                        # Check if this is actually a paper (not a review/comment)
                        if self._is_valid_paper_v2(note):
                            authors_raw = content.get('authors', [])
                            if isinstance(authors_raw, list):
                                authors = ', '.join(str(author) for author in authors_raw)
                            elif isinstance(authors_raw, dict):
                                authors = authors_raw.get('value', '')
                            elif isinstance(authors_raw, str):
                                authors = authors_raw
                            else:
                                authors = ''
                            
                            # Handle abstract field properly
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
                                'conference': 'ICLR',
                                'url': f"https://openreview.net/forum?id={note.get('id', '')}"
                            }
                            papers.append(paper)
                            
                    except Exception as e:
                        print(f"         Error processing note: {e}")
                        continue
                
                offset += len(notes)
                request_count += 1
                
                if len(notes) < 1000:  # Last batch
                    break
                    
            except Exception as e:
                print(f"      V2 API request failed: {e}")
                break
        
        return papers
    
    def _fetch_papers_by_invitation_v2(self, invitation: str, year: int) -> List[Dict]:
        """Fetch papers using API V2 invitation query"""
        url = f"{self.base_url}notes"
        
        # V2 API parameters
        params = {
            'invitation': invitation,
            'details': 'replyCount,invitation,original,forum',
            'limit': 1000,
            'offset': 0,
            'sort': 'tmdate:desc'  # Sort by modification date
        }
        
        papers = []
        offset = 0
        max_requests = 15
        request_count = 0
        
        while request_count < max_requests:
            params['offset'] = offset
            
            try:
                response = self.session.get(url, params=params, timeout=20)
                response.raise_for_status()
                
                data = response.json()
                notes = data.get('notes', [])
                
                if not notes:
                    break
                
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
                        
                        # V2 API validation
                        if self._is_valid_paper_v2(note):
                            authors_raw = content.get('authors', [])
                            if isinstance(authors_raw, list):
                                authors = ', '.join(str(author) for author in authors_raw)
                            elif isinstance(authors_raw, dict):
                                authors = authors_raw.get('value', '')
                            elif isinstance(authors_raw, str):
                                authors = authors_raw
                            else:
                                authors = ''
                            
                            # Handle abstract field
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
                                'conference': 'ICLR',
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
                print(f"      V2 invitation query failed: {e}")
                break
        
        return papers
    
    def _is_valid_paper_v2(self, note: Dict) -> bool:
        """Check if a note is a valid paper (not review/comment) in V2 API"""
        # Check invitation type
        invitation = note.get('invitation', '')
        
        # Skip reviews, comments, decisions
        if any(term in invitation.lower() for term in 
               ['review', 'comment', 'meta_review', 'decision', 'withdrawal']):
            return False
        
        # Check content structure
        content = note.get('content', {})
        
        # Must have title and some substantial content
        title_raw = content.get('title', '')
        if isinstance(title_raw, dict):
            title = title_raw.get('value', '')
        elif isinstance(title_raw, str):
            title = title_raw
        else:
            title = str(title_raw) if title_raw else ''
            
        if not title or len(title) < 10:
            return False
        
        # Should have abstract or other paper-like content
        has_paper_content = False
        for field in ['abstract', 'keywords', 'TLDR', 'summary']:
            field_data = content.get(field)
            if field_data:
                if isinstance(field_data, dict):
                    if field_data.get('value', '').strip():
                        has_paper_content = True
                        break
                elif isinstance(field_data, str):
                    if field_data.strip():
                        has_paper_content = True
                        break
                else:
                    if str(field_data).strip():
                        has_paper_content = True
                        break
        
        if not has_paper_content:
            return False
        
        # Check if it's a submission (positive indicator)
        if any(term in invitation.lower() for term in 
               ['submission', 'paper', 'blind_submission']):
            return True
        
        return True
    
    def _fetch_papers_by_invitation(self, invitation: str, year: int) -> List[Dict]:
        """Fetch papers using a specific invitation pattern"""
        url = f"{self.base_url}notes"
        params = {
            'invitation': invitation,
            'details': 'replyCount,invitation,forum',
            'limit': 1000,
            'offset': 0
        }
        
        papers = []
        offset = 0
        max_requests = 10  # Prevent infinite loops
        request_count = 0
        
        while request_count < max_requests:
            params['offset'] = offset
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            notes = data.get('notes', [])
            
            if not notes:
                break
                
            for note in notes:
                try:
                    content = note.get('content', {})
                    
                    # More flexible filtering - accept papers with title
                    title = content.get('title', '').strip()
                    if not title or len(title) < 5:
                        continue
                    
                    abstract = content.get('abstract', '').strip()
                    authors = content.get('authors', [])
                    if isinstance(authors, list):
                        authors = ', '.join(authors)
                    elif not isinstance(authors, str):
                        authors = ''
                    
                    paper = {
                        'title': title,
                        'authors': authors,
                        'abstract': abstract,
                        'year': year,
                        'conference': 'ICLR',
                        'url': f"https://openreview.net/forum?id={note.get('id', '')}"
                    }
                    papers.append(paper)
                    
                except Exception as e:
                    print(f"      Error processing individual paper: {e}")
                    continue
            
            offset += len(notes)
            request_count += 1
            
            if len(notes) < 1000:  # Last batch
                break
                
        return papers
    
    def _scrape_from_web(self, year: int) -> List[Dict]:
        """Fallback: scrape from OpenReview web page"""
        if year not in self.backup_urls:
            return []
        
        url = self.backup_urls[year]
        papers = []
        
        try:
            # Use requests directly since we're not using BeautifulSoup parsing
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            content = response.text
            print(f"   Fetched web page, length: {len(content)} characters")
            
            # Look for JSON data embedded in the page or paper links
            import re
            
            # Try to find paper IDs in the HTML
            paper_ids = re.findall(r'forum\?id=([A-Za-z0-9_-]+)', content)
            paper_ids = list(set(paper_ids))  # Remove duplicates
            
            print(f"   Found {len(paper_ids)} potential paper IDs")
            
            # For each paper ID, try to fetch details via API
            for paper_id in paper_ids[:50]:  # Limit to first 50 to avoid timeout
                try:
                    paper_data = self._fetch_paper_by_id(paper_id)
                    if paper_data:
                        papers.append(paper_data)
                except Exception as e:
                    continue
            
            print(f"   Successfully retrieved {len(papers)} papers via web scraping")
            
        except Exception as e:
            print(f"   Web scraping failed: {e}")
            
        return papers
    
    def _fetch_paper_by_id(self, paper_id: str) -> Dict:
        """Fetch individual paper details by ID"""
        url = f"{self.base_url}notes"
        params = {'id': paper_id}
        
        response = self.session.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        notes = data.get('notes', [])
        
        if not notes:
            return None
            
        note = notes[0]
        content = note.get('content', {})
        
        title = content.get('title', '').strip()
        if not title:
            return None
            
        authors = content.get('authors', [])
        if isinstance(authors, list):
            authors = ', '.join(authors)
        
        return {
            'title': title,
            'authors': authors,
            'abstract': content.get('abstract', '').strip(),
            'year': 2024,  # Assuming this is for recent years
            'conference': 'ICLR',
            'url': f"https://openreview.net/forum?id={paper_id}"
        }
    
    def _scrape_direct_listing(self, year: int) -> List[Dict]:
        """Scrape from direct paper listing page (like ICLR 2024 virtual site)"""
        if year not in self.direct_urls:
            return []
        
        url = self.direct_urls[year]
        papers = []
        
        try:
            print(f"   Fetching direct listing from: {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            content = response.text
            print(f"   Fetched page, length: {len(content)} characters")
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            # Look for paper entries in the ICLR virtual site
            # The site typically has paper titles as links or in specific containers
            paper_elements = []
            
            # Method 1: Look for paper title links
            paper_links = soup.find_all('a', href=lambda x: x and ('paper' in x.lower() or 'forum' in x.lower()))
            
            # Method 2: Look for specific classes that might contain papers
            paper_divs = soup.find_all('div', class_=lambda x: x and any(
                term in x.lower() for term in ['paper', 'title', 'abstract', 'author']
            ))
            
            # Method 3: Look for OpenReview forum links
            import re
            openreview_links = soup.find_all('a', href=re.compile(r'openreview\.net/forum'))
            
            print(f"   Found {len(paper_links)} paper links, {len(paper_divs)} paper divs, {len(openreview_links)} OpenReview links")
            
            # Process OpenReview links (most reliable)
            processed_ids = set()
            for link in openreview_links:
                href = link.get('href', '')
                # Extract paper ID from OpenReview URL
                id_match = re.search(r'forum\?id=([A-Za-z0-9_-]+)', href)
                if id_match:
                    paper_id = id_match.group(1)
                    if paper_id not in processed_ids:
                        processed_ids.add(paper_id)
                        
                        # Get title from link text or nearby elements
                        title = link.get_text().strip()
                        if not title or len(title) < 10:
                            # Look for title in parent or sibling elements
                            parent = link.find_parent(['div', 'td', 'li'])
                            if parent:
                                title_elem = parent.find(['h1', 'h2', 'h3', 'h4', 'strong'])
                                if title_elem:
                                    title = title_elem.get_text().strip()
                        
                        if title and len(title) > 10:
                            paper = {
                                'title': title,
                                'authors': '',  # Will be filled by API call if needed
                                'abstract': '',  # Will be filled by API call if needed  
                                'year': year,
                                'conference': 'ICLR',
                                'url': href if href.startswith('http') else f"https://openreview.net{href}"
                            }
                            papers.append(paper)
            
            # If we have paper IDs but limited info, try to fetch details from API
            if papers and len(papers) > 10:  # Only if we have a reasonable number
                print(f"   Found {len(papers)} papers, fetching additional details...")
                
                enhanced_papers = []
                for i, paper in enumerate(papers[:200]):  # Limit to avoid timeout
                    try:
                        # Extract paper ID from URL
                        id_match = re.search(r'forum\?id=([A-Za-z0-9_-]+)', paper['url'])
                        if id_match:
                            paper_id = id_match.group(1)
                            detailed_paper = self._fetch_paper_by_id(paper_id)
                            if detailed_paper:
                                enhanced_papers.append(detailed_paper)
                            else:
                                enhanced_papers.append(paper)  # Keep original if API fails
                        else:
                            enhanced_papers.append(paper)
                        
                        if (i + 1) % 50 == 0:
                            print(f"   Enhanced {i + 1}/{len(papers)} papers...")
                            
                    except Exception as e:
                        enhanced_papers.append(paper)  # Keep original on error
                        continue
                
                papers = enhanced_papers
            
            print(f"   Successfully extracted {len(papers)} papers from direct listing")
            
        except Exception as e:
            print(f"   Direct listing scraping failed: {e}")
            import traceback
            traceback.print_exc()
            
        return papers