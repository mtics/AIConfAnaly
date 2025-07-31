"""
AAAI paper scraper
"""

from .base_scraper import BaseScraper
from typing import List, Dict
import re
import time
import random


class AAAIScraper(BaseScraper):
    def __init__(self):
        super().__init__("AAAI", "https://ojs.aaai.org/")
        # Enhanced headers to avoid 403 errors
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        })
        
        # Updated AAAI proceedings URLs - prefer OJS when available
        self.url_map = {
            2018: "https://dblp.org/db/conf/aaai/aaai2018.html",
            2019: "https://dblp.org/db/conf/aaai/aaai2019.html", 
            2020: "https://ojs.aaai.org/index.php/AAAI/issue/view/342",  # Updated to OJS
            2021: "https://ojs.aaai.org/index.php/AAAI/issue/view/370",  # Updated to OJS
            2022: "https://ojs.aaai.org/index.php/AAAI/issue/view/398",
            2023: "https://ojs.aaai.org/index.php/AAAI/issue/view/507",
            2024: "https://ojs.aaai.org/index.php/AAAI/issue/view/577"
        }
        
        # Backup URLs for DBLP when OJS fails
        self.dblp_backup = {
            2020: "https://dblp.org/db/conf/aaai/aaai2020.html",
            2021: "https://dblp.org/db/conf/aaai/aaai2021.html"
        }
        
        # DBLP XML data URLs for structured data
        self.dblp_xml_map = {
            2018: "https://dblp.org/rec/conf/aaai/2018.xml",
            2019: "https://dblp.org/rec/conf/aaai/2019.xml",
            2020: "https://dblp.org/rec/conf/aaai/2020.xml",
            2021: "https://dblp.org/rec/conf/aaai/2021.xml"
        }
    
    def get_papers_for_year(self, year: int) -> List[Dict]:
        """Extract AAAI papers for a specific year"""
        if year not in self.url_map:
            raise ValueError(f"URL mapping not found for year {year}")
        
        print(f"Scraping AAAI {year}...")
        
        # Use different methods for different year ranges
        if year <= 2019:
            return self._scrape_legacy_aaai(year)
        else:
            # Try OJS first, fallback to DBLP if needed
            papers = self._scrape_ojs_aaai(year)
            if len(papers) < 100 and year in self.dblp_backup:  # If too few papers, try DBLP backup
                print(f"OJS returned only {len(papers)} papers, trying DBLP backup...")
                dblp_papers = self._scrape_dblp_backup(year)
                if len(dblp_papers) > len(papers):
                    papers = dblp_papers
            return papers
    
    def _scrape_legacy_aaai(self, year: int) -> List[Dict]:
        """Scrape AAAI papers from DBLP (2018-2019)"""
        url = self.url_map[year]
        return self._scrape_legacy_aaai_from_url(year, url)
    
    def _scrape_ojs_aaai(self, year: int) -> List[Dict]:
        """Scrape AAAI papers from OJS format (2022+)"""
        url = self.url_map[year]
        papers = []
        
        try:
            soup = self.fetch_page(url, delay=1.0)
            if not soup:
                print(f"Could not fetch OJS page for AAAI {year}")
                return papers
            
            # Find all paper entries in OJS format - try multiple selectors
            article_summaries = []
            
            # Method 1: Standard OJS article summary
            summaries = soup.find_all('div', class_='obj_article_summary')
            if summaries:
                article_summaries.extend(summaries)
            
            # Method 2: Alternative article selector
            if not article_summaries:
                summaries = soup.find_all('article', class_='obj_article_summary')
                if summaries:
                    article_summaries.extend(summaries)
            
            # Method 3: Look for table of contents entries
            if not article_summaries:
                summaries = soup.find_all('div', class_='tocArticle')
                if summaries:
                    article_summaries.extend(summaries)
            
            # Method 4: Look for article links in table format
            if not article_summaries:
                # Some OJS sites use tables for article listings
                table = soup.find('table', class_='tocArticle')
                if table:
                    rows = table.find_all('tr')
                    for row in rows:
                        if row.find('a', href=True):
                            article_summaries.append(row)
            
            # Method 5: Generic approach - look for links to articles
            if not article_summaries:
                links = soup.find_all('a', href=re.compile(r'/article/view/'))
                for link in links:
                    # Find parent container that might have author info
                    parent = link.find_parent(['div', 'td', 'li'])
                    if parent and parent not in article_summaries:
                        article_summaries.append(parent)
            
            print(f"Found {len(article_summaries)} article entries for AAAI {year}")
            
            for i, summary in enumerate(article_summaries):
                try:
                    # Extract title - try multiple methods
                    title = ""
                    paper_url = ""
                    
                    # Method 1: Standard title in h3
                    title_elem = summary.find('h3', class_='title')
                    if not title_elem:
                        # Method 2: Alternative title selectors
                        title_elem = summary.find(['h1', 'h2', 'h3', 'h4'], class_=['title', 'article-title', 'tocTitle'])
                    
                    if not title_elem:
                        # Method 3: Look for any link that might be a title
                        title_link = summary.find('a', href=re.compile(r'/article/view/'))
                        if title_link:
                            title = title_link.get_text().strip()
                            paper_url = title_link.get('href', '')
                    
                    if title_elem:
                        title_link = title_elem.find('a')
                        if title_link:
                            title = title_link.get_text().strip()
                            paper_url = title_link.get('href', '')
                        else:
                            title = title_elem.get_text().strip()
                    
                    # Skip if no title found
                    if not title or len(title) < 5:
                        continue
                        
                    # Make URL absolute if relative
                    if paper_url.startswith('/'):
                        paper_url = "https://ojs.aaai.org" + paper_url
                    
                    # Extract authors - try multiple methods
                    authors = ""
                    
                    # Method 1: Standard meta section
                    meta_div = summary.find('div', class_='meta')
                    if meta_div:
                        authors_elem = meta_div.find('div', class_='authors')
                        if authors_elem:
                            authors = authors_elem.get_text().strip()
                        else:
                            # Try to find authors in different structure
                            authors_text = meta_div.get_text()
                            if 'by' in authors_text.lower():
                                authors = authors_text.strip()
                    
                    # Method 2: Look for authors class directly
                    if not authors:
                        authors_elem = summary.find(['div', 'span', 'p'], class_=['authors', 'author', 'tocAuthors'])
                        if authors_elem:
                            authors = authors_elem.get_text().strip()
                    
                    # Method 3: Look in table cells (for table-based layouts)
                    if not authors and summary.name == 'tr':
                        cells = summary.find_all('td')
                        for cell in cells:
                            cell_text = cell.get_text().strip()
                            # Authors are often in cells that don't contain the title
                            if cell_text and title not in cell_text and len(cell_text) > 5:
                                if any(indicator in cell_text.lower() for indicator in ['by', ',', 'author']):
                                    authors = cell_text
                                    break
                    
                    # Clean up authors text
                    if authors:
                        authors = re.sub(r'^(by|authors?:?)\s*', '', authors, flags=re.IGNORECASE)
                        authors = authors.strip()
                    
                    # Extract abstract - fetch for more papers but with rate limiting
                    abstract = ""
                    if paper_url and i < 50:  # Fetch abstracts for first 50 papers
                        try:
                            paper_soup = self.fetch_page(paper_url, delay=0.8)  # Slightly longer delay
                            if paper_soup:
                                # Try multiple abstract selectors
                                abstract_section = paper_soup.find('section', class_='item abstract')
                                if not abstract_section:
                                    abstract_section = paper_soup.find('div', class_='abstract')
                                if not abstract_section:
                                    abstract_section = paper_soup.find('div', id='abstract')
                                if not abstract_section:
                                    # Look for meta description
                                    meta_desc = paper_soup.find('meta', attrs={'name': 'description'})
                                    if meta_desc:
                                        abstract = meta_desc.get('content', '').strip()
                                
                                if abstract_section and not abstract:
                                    # Try to get text from section
                                    abstract_p = abstract_section.find('p')
                                    if abstract_p:
                                        abstract = abstract_p.get_text().strip()
                                    else:
                                        # Get all text from section, skip headers
                                        abstract = abstract_section.get_text().strip()
                                        # Remove common headers
                                        abstract = re.sub(r'^(abstract|summary):?\s*', '', abstract, flags=re.IGNORECASE)
                        except Exception as e:
                            print(f"Error fetching abstract for {title}: {e}")
                            pass
                    
                    paper = {
                        'title': title,
                        'authors': authors,
                        'abstract': abstract,
                        'year': year,
                        'conference': 'AAAI',
                        'url': paper_url
                    }
                    papers.append(paper)
                    
                    # Add progressive delay
                    if i > 0 and i % 10 == 0:
                        print(f"Processed {i} papers, taking a brief pause...")
                        time.sleep(random.uniform(1.0, 2.0))
                    elif i % 3 == 0:
                        time.sleep(random.uniform(0.2, 0.5))
                    
                except Exception as e:
                    print(f"Error processing OJS paper: {e}")
                    continue
        
        except Exception as e:
            print(f"Error scraping OJS AAAI {year}: {e}")
        
        return papers
    
    def _scrape_dblp_backup(self, year: int) -> List[Dict]:
        """Backup DBLP scraping for years with poor OJS results"""
        if year not in self.dblp_backup:
            return []
        
        url = self.dblp_backup[year]
        print(f"Using DBLP backup for AAAI {year}: {url}")
        return self._scrape_legacy_aaai_from_url(year, url)
    
    def _scrape_legacy_aaai_from_url(self, year: int, url: str) -> List[Dict]:
        """Extract papers from DBLP URL (extracted from _scrape_legacy_aaai)"""
        papers = []
        
        try:
            print(f"Fetching AAAI {year} data from DBLP...")
            soup = self.fetch_page(url, delay=1.0)
            
            if not soup:
                print(f"Could not fetch DBLP page for AAAI {year}")
                return papers
            
            # Use same logic as _scrape_legacy_aaai but as separate function
            citations = soup.find_all('cite', class_='data')
            
            for cite in citations:
                try:
                    title_elem = cite.find('span', class_='title')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text().strip()
                    if title.endswith('.'):
                        title = title[:-1]
                    
                    authors_list = []
                    for author_span in cite.find_all('span', itemprop='author'):
                        author_name = author_span.get_text().strip()
                        if author_name:
                            authors_list.append(author_name)
                    
                    authors = ', '.join(authors_list)
                    
                    paper_url = ""
                    doi_link = cite.find('a', href=re.compile(r'doi\.org|dx\.doi\.org'))
                    if doi_link:
                        paper_url = doi_link.get('href')
                    else:
                        for link in cite.find_all('a', href=True):
                            href = link.get('href')
                            if 'aaai.org' in href or 'ojs.aaai.org' in href:
                                paper_url = href
                                break
                    
                    if len(title) < 10 or any(skip in title.lower() for skip in 
                                            ['proceedings', 'conference', 'workshop', 'front matter', 'preface']):
                        continue
                    
                    paper = {
                        'title': title,
                        'authors': authors,
                        'abstract': "",
                        'year': year,
                        'conference': 'AAAI',
                        'url': paper_url
                    }
                    papers.append(paper)
                    
                except Exception as e:
                    print(f"Error processing DBLP entry: {e}")
                    continue
            
            # Try alternative structure if no citations found
            if not papers:
                print(f"No citations found, trying alternative DBLP structure...")
                
                for li in soup.find_all('li', class_='entry'):
                    try:
                        title_elem = li.find('span', class_='title')
                        if title_elem:
                            title = title_elem.get_text().strip()
                            if title.endswith('.'):
                                title = title[:-1]
                            
                            authors_list = []
                            for author in li.find_all('span', itemprop='author'):
                                authors_list.append(author.get_text().strip())
                            
                            authors = ', '.join(authors_list)
                            
                            paper = {
                                'title': title,
                                'authors': authors,
                                'abstract': "",
                                'year': year,
                                'conference': 'AAAI',
                                'url': ""
                            }
                            papers.append(paper)
                    except Exception as e:
                        continue
            
            print(f"Successfully extracted {len(papers)} papers from DBLP for AAAI {year}")
            
        except Exception as e:
            print(f"Error scraping DBLP AAAI {year}: {e}")
            import traceback
            traceback.print_exc()
        
        return papers