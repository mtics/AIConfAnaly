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
        
        # Updated AAAI proceedings URLs - prefer official archives
        self.url_map = {
            2018: "https://dblp.org/db/conf/aaai/aaai2018.html",
            2019: "https://dblp.org/db/conf/aaai/aaai2019.html", 
            2020: "https://ojs.aaai.org/index.php/AAAI/issue/view/342",  # Updated to OJS
            2021: "https://ojs.aaai.org/index.php/AAAI/issue/view/370",  # Updated to OJS
            2022: "https://ojs.aaai.org/index.php/AAAI/issue/view/398",
            2023: "https://ojs.aaai.org/index.php/AAAI/issue/view/507", 
            2024: "https://ojs.aaai.org/index.php/AAAI/issue/view/577",
            2025: "https://aaai.org/proceeding/aaai-39-2025/"
        }
        
        # Official AAAI archive URLs (direct proceedings)
        self.archive_urls = {
            2022: "https://aaai.org/proceeding/aaai-36-2022/",
            2023: "https://aaai.org/proceeding/aaai-37-2023/",
            2024: "https://aaai.org/proceeding/aaai-38-2024/",
            2025: "https://aaai.org/proceeding/aaai-39-2025/"
        }
        
        # Track-based OJS issue URLs for recent years (discovered from archive pages)
        self.track_urls = {
            2022: list(range(483, 497)),  # AAAI-36 tracks (14 tracks)
            2023: list(range(548, 561)),  # AAAI-37 tracks (13 tracks)
            2024: list(range(576, 597)),  # AAAI-38 tracks (21 tracks)
            2025: []  # Will be populated after analyzing the archive structure
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
            # For 2022-2024, use different approaches based on year
            papers = []
            if year == 2022:
                # Special handling for AAAI 2022 - direct archive parsing
                print(f"Using direct archive parsing for AAAI {year}...")
                papers = self._scrape_aaai_2022_archive()
            elif year == 2025:
                # Special handling for AAAI 2025 - use archive page parsing
                print(f"Using archive page parsing for AAAI {year}...")
                papers = self._scrape_aaai_2025_archive()
            elif year in self.track_urls and year >= 2023:
                print(f"Using track-based scraping for AAAI {year}...")
                papers = self._scrape_aaai_tracks(year)
            
            # If track-based approach didn't work, try single OJS page
            if len(papers) < 500:  # Expected at least 500+ papers for recent AAAI
                if papers:
                    print(f"Track-based scraping returned only {len(papers)} papers, trying single OJS...")
                else:
                    print(f"Track-based scraping failed, trying single OJS page...")
                papers_ojs = self._scrape_ojs_aaai(year)
                if len(papers_ojs) > len(papers):
                    papers = papers_ojs
                    
            # If still too few papers, try DBLP backup
            if len(papers) < 100 and year in self.dblp_backup:
                print(f"OJS returned only {len(papers)} papers, trying DBLP backup...")
                dblp_papers = self._scrape_dblp_backup(year)
                if len(dblp_papers) > len(papers):
                    papers = dblp_papers
                    
            return papers
    
    def _scrape_aaai_2022_archive(self) -> List[Dict]:
        """Special method for AAAI 2022 - parse archive page directly"""
        archive_url = "https://aaai.org/proceeding/aaai-36-2022/"
        all_papers = []
        
        try:
            print(f"   Fetching AAAI 2022 archive page...")
            soup = self.fetch_page(archive_url, delay=1.0, retries=3)
            if not soup:
                print(f"   Could not fetch AAAI 2022 archive page")
                return all_papers
            
            print(f"   Successfully fetched archive page, finding track links...")
            
            # Find all track links in the archive page
            track_links = []
            
            # Look for links that match AAAI 2022 track pattern
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                text = link.get_text().strip()
                
                # AAAI 2022 tracks follow pattern: /proceeding/XX-aaai-22-*
                if '/proceeding/' in href and 'aaai-22' in href and 'technical-track' in href.lower():
                    # Make absolute URL
                    if not href.startswith('http'):
                        href = f"https://aaai.org{href}"
                    
                    track_links.append({
                        'url': href,
                        'title': text
                    })
            
            print(f"   Found {len(track_links)} track links")
            
            # Scrape each track page
            for i, track_info in enumerate(track_links):
                track_url = track_info['url']
                track_title = track_info['title']
                
                print(f"   Track {i+1}/{len(track_links)}: {track_title}")
                
                try:
                    papers = self._scrape_aaai_2022_track_page(track_url)
                    
                    if papers:
                        all_papers.extend(papers)
                        print(f"      Found {len(papers)} papers in this track")
                    else:
                        print(f"      No papers found in this track")
                        
                    # Add delay between tracks
                    if i < len(track_links) - 1:
                        time.sleep(random.uniform(1.0, 2.0))
                        
                except Exception as e:
                    print(f"      Error scraping track {track_url}: {e}")
                    continue
            
            # Remove duplicates
            seen_titles = set()
            unique_papers = []
            for paper in all_papers:
                title = paper.get('title', '').strip()
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    unique_papers.append(paper)
            
            print(f"   Total unique papers from AAAI 2022 archive: {len(unique_papers)}")
            return unique_papers
            
        except Exception as e:
            print(f"   Error scraping AAAI 2022 archive: {e}")
            import traceback
            traceback.print_exc()
            return all_papers
    
    def _scrape_aaai_2022_track_page(self, track_url: str) -> List[Dict]:
        """Scrape individual AAAI 2022 track page"""
        papers = []
        
        try:
            soup = self.fetch_page(track_url, delay=1.0, retries=2)
            if not soup:
                return papers
            
            # AAAI 2022 track pages have papers listed in a specific format
            # Look for paper entries - they typically have title links and author info
            
            # Method 1: Look for paper titles as links
            paper_links = []
            
            # Find all links that could be paper titles (longer text, not navigation)
            for link in soup.find_all('a', href=True):
                text = link.get_text().strip()
                href = link.get('href', '')
                
                # Filter for paper-like links (long titles, avoid navigation)
                if (len(text) > 20 and 
                    not any(skip in text.lower() for skip in 
                           ['home', 'back', 'next', 'previous', 'search', 'proceedings', 'track',
                            'officers', 'committees', 'award', 'about', 'contact', 'menu']) and
                    not href.startswith('#') and
                    not 'aaai.org/about' in href and
                    not '/awards/' in href and
                    not '/committees/' in href):
                    
                    paper_links.append({
                        'title': text,
                        'url': href if href.startswith('http') else f"https://aaai.org{href}"
                    })
            
            # Method 2: Look for structured paper listings (tables, lists, etc.)
            # Sometimes papers are in table format
            for table in soup.find_all('table'):
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:  # Title and authors columns
                        title_cell = cells[0]
                        title_link = title_cell.find('a')
                        
                        if title_link:
                            title = title_link.get_text().strip()
                            url = title_link.get('href', '')
                            
                            if len(title) > 20:
                                if not url.startswith('http'):
                                    url = f"https://aaai.org{url}"
                                
                                paper_links.append({
                                    'title': title,
                                    'url': url
                                })
            
            # Method 3: Look for div/section based paper listings
            for section in soup.find_all(['div', 'section']):
                # Look for sections that might contain paper listings
                section_links = section.find_all('a', href=True)
                
                for link in section_links:
                    text = link.get_text().strip()
                    href = link.get('href', '')
                    
                    if (len(text) > 20 and 
                        'pdf' not in href.lower() and
                        not any(skip in text.lower() for skip in ['download', 'view', 'full text',
                                                                  'officers', 'committees', 'award', 'about']) and
                        not 'aaai.org/about' in href and
                        not '/awards/' in href):
                        
                        paper_links.append({
                            'title': text,
                            'url': href if href.startswith('http') else f"https://aaai.org{href}"
                        })
            
            # Extract paper information
            for paper_info in paper_links:
                title = paper_info['title']
                url = paper_info['url']
                
                # Try to extract authors from the same page section
                authors = ""
                # This would need more specific parsing based on the actual page structure
                
                paper = {
                    'title': title,
                    'authors': authors,
                    'abstract': "",  # Abstract would need separate fetching
                    'year': 2022,
                    'conference': 'AAAI',
                    'url': url
                }
                papers.append(paper)
            
        except Exception as e:
            print(f"      Error parsing track page: {e}")
        
        return papers
    
    def _scrape_aaai_tracks(self, year: int) -> List[Dict]:
        """Scrape AAAI papers from multiple track URLs"""
        if year not in self.track_urls:
            return []
        
        all_papers = []
        track_numbers = self.track_urls[year]
        
        print(f"   Scraping {len(track_numbers)} tracks for AAAI {year}")
        
        for i, track_num in enumerate(track_numbers):
            track_url = f"https://ojs.aaai.org/index.php/AAAI/issue/view/{track_num}"
            print(f"   Track {i+1}/{len(track_numbers)}: Issue {track_num}")
            
            try:
                # Use the existing OJS scraping logic for each track
                papers = self._scrape_ojs_track(track_url, year)
                
                if papers:
                    all_papers.extend(papers)
                    print(f"      Found {len(papers)} papers in this track")
                else:
                    print(f"      No papers found in this track")
                    
                # Add delay between tracks to avoid overloading
                if i < len(track_numbers) - 1:
                    time.sleep(random.uniform(1.0, 2.0))
                    
            except Exception as e:
                print(f"      Error scraping track {track_num}: {e}")
                continue
        
        # Remove duplicates based on title
        seen_titles = set()
        unique_papers = []
        for paper in all_papers:
            title = paper.get('title', '').strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_papers.append(paper)
        
        print(f"   Total unique papers from all tracks: {len(unique_papers)}")
        return unique_papers
    
    def _scrape_ojs_track(self, url: str, year: int) -> List[Dict]:
        """Scrape a single OJS track/issue page"""
        papers = []
        
        try:
            soup = self.fetch_page(url, delay=1.0, retries=2)
            if not soup:
                return papers
            
            # Use similar logic to _scrape_ojs_aaai but simplified
            article_summaries = []
            
            # Find all article entries
            summaries = soup.find_all('div', class_='obj_article_summary')
            if summaries:
                article_summaries.extend(summaries)
            
            # Alternative selectors
            if not article_summaries:
                summaries = soup.find_all('article', class_='obj_article_summary')
                if summaries:
                    article_summaries.extend(summaries)
            
            # Look for table of contents entries
            if not article_summaries:
                summaries = soup.find_all('div', class_='tocArticle')
                if summaries:
                    article_summaries.extend(summaries)
            
            for summary in article_summaries:
                try:
                    # Extract title
                    title = ""
                    paper_url = ""
                    
                    title_elem = summary.find('h3', class_='title')
                    if not title_elem:
                        title_elem = summary.find(['h1', 'h2', 'h3', 'h4'], class_=['title', 'article-title'])
                    
                    if not title_elem:
                        title_link = summary.find('a', href=re.compile(r'/article/view/'))
                        if title_link:
                            title = title_link.get_text().strip()
                            paper_url = title_link.get('href', '')
                    else:
                        title_link = title_elem.find('a')
                        if title_link:
                            title = title_link.get_text().strip()
                            paper_url = title_link.get('href', '')
                        else:
                            title = title_elem.get_text().strip()
                    
                    if not title or len(title) < 5:
                        continue
                    
                    # Make URL absolute
                    if paper_url.startswith('/'):
                        paper_url = "https://ojs.aaai.org" + paper_url
                    
                    # Extract authors
                    authors = ""
                    meta_div = summary.find('div', class_='meta')
                    if meta_div:
                        authors_elem = meta_div.find('div', class_='authors')
                        if authors_elem:
                            authors = authors_elem.get_text().strip()
                    
                    if not authors:
                        authors_elem = summary.find(['div', 'span', 'p'], class_=['authors', 'author'])
                        if authors_elem:
                            authors = authors_elem.get_text().strip()
                    
                    # Clean up authors text
                    if authors:
                        authors = re.sub(r'^(by|authors?:?)\\s*', '', authors, flags=re.IGNORECASE)
                        authors = authors.strip()
                    
                    paper = {
                        'title': title,
                        'authors': authors,
                        'abstract': "",  # Skip abstract fetching for track-based scraping
                        'year': year,
                        'conference': 'AAAI',
                        'url': paper_url
                    }
                    papers.append(paper)
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"      Error scraping track page: {e}")
        
        return papers
    
    def _scrape_legacy_aaai(self, year: int) -> List[Dict]:
        """Scrape AAAI papers from DBLP (2018-2019)"""
        url = self.url_map[year]
        return self._scrape_legacy_aaai_from_url(year, url)
    
    def _scrape_ojs_aaai(self, year: int) -> List[Dict]:
        """Scrape AAAI papers from OJS format (2022+) - Enhanced version"""
        url = self.url_map[year]
        papers = []
        
        try:
            # Use longer delay and retry mechanism for these years
            soup = self.fetch_page(url, delay=2.0, retries=3)
            if not soup:
                print(f"Could not fetch OJS page for AAAI {year}")
                return papers
            
            print(f"Successfully fetched AAAI {year} page, analyzing structure...")
            
            # Find all paper entries in OJS format - comprehensive approach
            article_summaries = []
            
            # Method 1: Standard OJS article summary
            summaries = soup.find_all('div', class_='obj_article_summary')
            if summaries:
                article_summaries.extend(summaries)
                print(f"   Found {len(summaries)} obj_article_summary entries")
            
            # Method 2: Alternative article selector
            if not article_summaries:
                summaries = soup.find_all('article', class_='obj_article_summary')
                if summaries:
                    article_summaries.extend(summaries)
                    print(f"   Found {len(summaries)} article.obj_article_summary entries")
            
            # Method 3: Look for table of contents entries
            if not article_summaries:
                summaries = soup.find_all('div', class_='tocArticle')
                if summaries:
                    article_summaries.extend(summaries)
                    print(f"   Found {len(summaries)} tocArticle entries")
            
            # Method 4: Look for any div containing article links
            if not article_summaries:
                # Look for divs that contain article/view links
                all_divs = soup.find_all('div')
                for div in all_divs:
                    article_link = div.find('a', href=re.compile(r'/article/view/'))
                    if article_link and div not in article_summaries:
                        article_summaries.append(div)
                print(f"   Found {len(article_summaries)} divs with article links")
            
            # Method 5: Table-based layout (some AAAI years use tables)
            if not article_summaries:
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        if row.find('a', href=re.compile(r'/article/view/')):
                            article_summaries.append(row)
                print(f"   Found {len(article_summaries)} table rows with article links")
            
            # Method 6: Direct link approach - find all article links and work backwards
            if not article_summaries:
                article_links = soup.find_all('a', href=re.compile(r'/article/view/'))
                print(f"   Found {len(article_links)} direct article links")
                
                for link in article_links:
                    # Find the most appropriate parent container
                    parent = link.find_parent(['div', 'td', 'li', 'article'])
                    while parent and parent.name in ['span', 'strong', 'em']:
                        parent = parent.find_parent(['div', 'td', 'li', 'article'])
                    
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
    
    def _scrape_aaai_archive(self, year: int) -> List[Dict]:
        """Scrape AAAI papers from official archive page"""
        if year not in self.archive_urls:
            return []
        
        url = self.archive_urls[year]
        papers = []
        
        try:
            print(f"   Fetching AAAI archive page: {url}")
            soup = self.fetch_page(url, delay=1.0, retries=3)
            if not soup:
                print(f"   Could not fetch AAAI archive page")
                return papers
            
            print(f"   Successfully fetched archive page, analyzing...")
            
            # Look for AAAI year-specific links or sections
            year_str = str(year)
            
            # Method 1: Look for direct links to proceedings
            proceedings_links = []
            
            # Look for links containing the year
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href', '')
                text = link.get_text().strip()
                
                # Check if link is related to our target year
                if year_str in href or year_str in text:
                    if any(term in href.lower() or term in text.lower() 
                          for term in ['proceedings', 'papers', 'aaai', 'conference']):
                        proceedings_links.append({
                            'url': href,
                            'text': text,
                            'link_elem': link
                        })
            
            print(f"   Found {len(proceedings_links)} potential proceedings links for {year}")
            
            # Method 2: Look for specific year sections
            year_sections = []
            for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'strong']):
                if year_str in heading.get_text():
                    year_sections.append(heading)
            
            print(f"   Found {len(year_sections)} year-specific sections")
            
            # Try to find the most relevant proceedings link
            best_link = None
            for link_info in proceedings_links:
                text = link_info['text'].lower()
                href = link_info['url'].lower()
                
                # Prioritize direct proceedings links
                if ('proceedings' in text or 'proceedings' in href) and year_str in (text + href):
                    best_link = link_info
                    break
                elif 'aaai' in href and year_str in href:
                    best_link = link_info
            
            if best_link:
                proceedings_url = best_link['url']
                if not proceedings_url.startswith('http'):
                    # Make absolute URL
                    from urllib.parse import urljoin
                    proceedings_url = urljoin(url, proceedings_url)
                
                print(f"   Found proceedings URL: {proceedings_url}")
                print(f"   Link text: {best_link['text']}")
                
                # If it's an OJS link, use existing OJS scraper
                if 'ojs.aaai.org' in proceedings_url:
                    # Update URL map temporarily and use OJS scraper
                    original_url = self.url_map.get(year)
                    self.url_map[year] = proceedings_url
                    papers = self._scrape_ojs_aaai(year)
                    if original_url:
                        self.url_map[year] = original_url
                else:
                    # Try to scrape the proceedings page directly
                    papers = self._scrape_proceedings_page(proceedings_url, year)
            
            # Method 3: If no direct link found, look for embedded paper listings
            if not papers and year_sections:
                print(f"   Trying to extract papers from year sections...")
                for section in year_sections:
                    # Look for paper listings near this section
                    parent = section.find_parent(['div', 'section', 'article'])
                    if parent:
                        paper_links = parent.find_all('a', href=True)
                        for link in paper_links:
                            href = link.get('href', '')
                            text = link.get_text().strip()
                            
                            # Check if this looks like a paper link
                            if len(text) > 20 and any(term in href.lower() 
                                                    for term in ['paper', 'pdf', 'article']):
                                paper = {
                                    'title': text,
                                    'authors': '',
                                    'abstract': '',
                                    'year': year,
                                    'conference': 'AAAI',
                                    'url': href if href.startswith('http') else f"https://aaai.org{href}"
                                }
                                papers.append(paper)
            
            print(f"   Archive scraping found {len(papers)} papers")
            
        except Exception as e:
            print(f"   Archive scraping failed: {e}")
            import traceback
            traceback.print_exc()
        
        return papers
    
    def _scrape_proceedings_page(self, url: str, year: int) -> List[Dict]:
        """Scrape a specific proceedings page"""
        papers = []
        
        try:
            print(f"   Scraping proceedings page: {url}")
            soup = self.fetch_page(url, delay=1.0, retries=3)
            if not soup:
                return papers
            
            # Look for paper listings
            paper_elements = []
            
            # Method 1: Look for links to individual papers
            paper_links = soup.find_all('a', href=True)
            for link in paper_links:
                text = link.get_text().strip()
                href = link.get('href', '')
                
                # Filter for actual paper titles (longer text, not navigation links)
                if len(text) > 20 and not any(skip in text.lower() 
                    for skip in ['home', 'back', 'next', 'previous', 'search', 'download all']):
                    
                    paper = {
                        'title': text,
                        'authors': '',
                        'abstract': '',
                        'year': year,
                        'conference': 'AAAI',
                        'url': href if href.startswith('http') else f"https://aaai.org{href}"
                    }
                    papers.append(paper)
            
            # Method 2: Look for structured lists
            for list_elem in soup.find_all(['ul', 'ol']):
                items = list_elem.find_all('li')
                for item in items:
                    text = item.get_text().strip()
                    link = item.find('a', href=True)
                    
                    if len(text) > 20 and link:
                        paper = {
                            'title': text,
                            'authors': '',
                            'abstract': '',
                            'year': year,
                            'conference': 'AAAI',
                            'url': link.get('href', '')
                        }
                        papers.append(paper)
            
            print(f"   Proceedings page yielded {len(papers)} papers")
            
        except Exception as e:
            print(f"   Proceedings page scraping failed: {e}")
        
        return papers
    
    def _scrape_aaai_2025_archive(self) -> List[Dict]:
        """Special method for AAAI 2025 - parse archive page and extract tracks"""
        archive_url = "https://aaai.org/proceeding/aaai-39-2025/"
        all_papers = []
        
        try:
            print(f"   Fetching AAAI 2025 archive page...")
            soup = self.fetch_page(archive_url, delay=1.0, retries=3)
            if not soup:
                print(f"   Could not fetch AAAI 2025 archive page")
                return all_papers
            
            # Look for track links similar to other AAAI years
            track_links = soup.find_all('a', href=lambda x: x and 'ojs.aaai.org' in str(x))
            
            if not track_links:
                # Alternative: look for any OJS links
                track_links = soup.find_all('a', href=re.compile(r'ojs\.aaai\.org.*issue/view/\d+'))
            
            print(f"   Found {len(track_links)} potential track links")
            
            if track_links:
                # Extract track IDs and scrape each track
                track_ids = []
                for link in track_links:
                    href = link.get('href', '')
                    # Extract issue ID from URL like https://ojs.aaai.org/index.php/AAAI/issue/view/###
                    match = re.search(r'issue/view/(\d+)', href)
                    if match:
                        track_ids.append(int(match.group(1)))
                
                track_ids = list(set(track_ids))  # Remove duplicates
                print(f"   Extracted {len(track_ids)} unique track IDs: {track_ids}")
                
                # Update the track_urls for 2025
                self.track_urls[2025] = track_ids
                
                # Now scrape using the track-based method
                all_papers = self._scrape_aaai_tracks(2025)
            
            else:
                # Fallback: try to scrape papers directly from archive page
                print(f"   No track links found, trying direct paper extraction...")
                
                # Look for paper titles in the archive page
                paper_elements = soup.find_all(['a', 'h3', 'h4'], string=re.compile(r'.{15,}'))
                
                for elem in paper_elements:
                    title = elem.get_text().strip()
                    # Filter out non-paper titles
                    if (len(title) > 15 and len(title) < 200 and 
                        not any(skip in title.lower() for skip in 
                               ['proceeding', 'track', 'issue', 'volume', 'table of contents'])):
                        
                        # Get URL if it's a link
                        url = ""
                        if elem.name == 'a':
                            url = elem.get('href', '')
                            if url and not url.startswith('http'):
                                url = 'https://aaai.org' + url
                        
                        paper = {
                            'title': title,
                            'authors': '',
                            'abstract': '',
                            'year': 2025,
                            'conference': 'AAAI',
                            'url': url
                        }
                        all_papers.append(paper)
                
                print(f"   Direct extraction yielded {len(all_papers)} papers")
            
        except Exception as e:
            print(f"   AAAI 2025 archive scraping failed: {e}")
            import traceback
            traceback.print_exc()
        
        return all_papers