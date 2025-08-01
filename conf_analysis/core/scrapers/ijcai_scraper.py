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
        
        # Special URLs for accepted papers lists
        self.accepted_papers_urls = {
            2025: "https://2025.ijcai.org/montreal-main-track-accepted-papers/"
        }
    
    def get_papers_for_year(self, year: int) -> List[Dict]:
        """Extract IJCAI papers for a specific year"""
        # Check if it's a special year with accepted papers list
        if year in self.accepted_papers_urls:
            return self._scrape_accepted_papers(year)
        
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
    
    def _scrape_accepted_papers(self, year: int) -> List[Dict]:
        """Scrape IJCAI accepted papers from special accepted papers page"""
        url = self.accepted_papers_urls[year]
        print(f"  🌐 Scraping IJCAI {year} accepted papers from: {url}")
        
        try:
            # Get the page content
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
            content = response.text
            
            print(f"     Fetched page content: {len(content)} characters")
            
            # Parse with BeautifulSoup
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            papers = []
            
            # Method 1: Look for papers in divs with class "paper"
            paper_divs = soup.find_all('div', class_='paper')
            
            if paper_divs:
                print(f"     Found {len(paper_divs)} paper divs")
                print(f"     Debug: Checking structure of first paper div...")
                if paper_divs:
                    first_div = paper_divs[0]
                    print(f"     Classes: {first_div.get('class', [])}")
                    print(f"     Text preview: {first_div.get_text()[:200].strip()}...")
                
                for paper_div in paper_divs:
                    try:
                        # Try multiple ways to extract title
                        title = ""
                        
                        # Get all text from the paper div
                        full_text = paper_div.get_text().strip()
                        if not full_text:
                            continue
                        
                        # Parse the IJCAI 2025 format: "ID: Title\nAuthors: Names\nLocation: ..."
                        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
                        
                        if lines:
                            # First line should be "ID: Title"
                            first_line = lines[0]
                            if ':' in first_line:
                                # Extract title after the ID number
                                parts = first_line.split(':', 1)
                                if len(parts) == 2:
                                    title = parts[1].strip()
                            else:
                                title = first_line
                        
                        # Skip if no valid title found
                        if not title or len(title) < 10:
                            continue
                        
                        # Extract authors from the lines
                        authors = ""
                        for line in lines[1:]:
                            if line.startswith('Authors:'):
                                authors = line.replace('Authors:', '').strip()
                                break
                            elif 'Authors:' in line:
                                parts = line.split('Authors:', 1)
                                if len(parts) == 2:
                                    authors = parts[1].strip()
                                    break
                        
                        # Extract abstract if available
                        abstract = ""
                        abstract_elem = paper_div.find(class_='paper-abstract') or paper_div.find(class_='abstract')
                        if abstract_elem:
                            abstract = abstract_elem.get_text().strip()
                        
                        paper = {
                            'title': title,
                            'authors': authors,
                            'abstract': abstract,
                            'year': year,
                            'conference': 'IJCAI',
                            'url': url
                        }
                        papers.append(paper)
                        
                        # Debug: print first few papers
                        if len(papers) <= 3:
                            print(f"     Paper {len(papers)}: {title[:80]}...")
                        
                    except Exception as e:
                        print(f"     Error processing paper div: {e}")
                        continue
            
            # Method 2: If no paper divs found, try alternative selectors
            if not papers:
                print(f"     No paper divs found, trying alternative selectors...")
                
                # Look for any structured list items or paragraphs that might contain papers
                potential_papers = soup.find_all(['li', 'p', 'div'], string=re.compile(r'.{20,}'))
                
                for elem in potential_papers:
                    text = elem.get_text().strip()
                    # Filter for paper-like titles (reasonable length, not too short/long)
                    if 20 <= len(text) <= 200:
                        # Try to separate title and authors if in same element
                        parts = text.split(' - ')
                        if len(parts) >= 2:
                            title = parts[0].strip()
                            authors = parts[1].strip()
                        else:
                            title = text
                            authors = ""
                        
                        # Skip obvious non-papers
                        if any(skip in title.lower() for skip in 
                               ['accepted papers', 'track', 'session', 'proceedings', 'schedule']):
                            continue
                        
                        paper = {
                            'title': title,
                            'authors': authors,
                            'abstract': '',
                            'year': year,
                            'conference': 'IJCAI',
                            'url': url
                        }
                        papers.append(paper)
                        
                        # Limit to prevent too many false positives
                        if len(papers) >= 1000:  # Reasonable limit for IJCAI
                            break
            
            # Method 3: Try to find any JavaScript data or hidden content
            if not papers:
                print(f"     No papers found with standard methods, searching for JavaScript data...")
                
                # Look for JSON data in script tags
                script_tags = soup.find_all('script')
                for script in script_tags:
                    script_text = script.string or ''
                    if 'title' in script_text.lower() and len(script_text) > 100:
                        # Try to extract paper information from JavaScript
                        try:
                            import json
                            # Look for JSON-like structures
                            json_matches = re.findall(r'\{[^{}]*"title"[^{}]*\}', script_text)
                            for match in json_matches[:100]:  # Limit to avoid processing too much
                                try:
                                    data = json.loads(match)
                                    if 'title' in data:
                                        paper = {
                                            'title': data.get('title', '').strip(),
                                            'authors': data.get('authors', ''),
                                            'abstract': data.get('abstract', ''),
                                            'year': year,
                                            'conference': 'IJCAI',
                                            'url': url
                                        }
                                        if paper['title'] and len(paper['title']) > 10:
                                            papers.append(paper)
                                except json.JSONDecodeError:
                                    continue
                        except Exception as e:
                            continue
            
            print(f"     ✅ Successfully extracted {len(papers)} papers from IJCAI {year}")
            return papers
            
        except Exception as e:
            print(f"     ❌ Failed to scrape IJCAI {year} accepted papers: {e}")
            import traceback
            traceback.print_exc()
            return []