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
        
        # Updated AAAI proceedings URLs - using DBLP for early years
        self.url_map = {
            2018: "https://dblp.org/db/conf/aaai/aaai2018.html",
            2019: "https://dblp.org/db/conf/aaai/aaai2019.html", 
            2020: "https://dblp.org/db/conf/aaai/aaai2020.html",
            2021: "https://dblp.org/db/conf/aaai/aaai2021.html",
            2022: "https://ojs.aaai.org/index.php/AAAI/issue/view/398",
            2023: "https://ojs.aaai.org/index.php/AAAI/issue/view/507",
            2024: "https://ojs.aaai.org/index.php/AAAI/issue/view/577"
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
        if year <= 2021:
            return self._scrape_legacy_aaai(year)
        else:
            return self._scrape_ojs_aaai(year)
    
    def _scrape_legacy_aaai(self, year: int) -> List[Dict]:
        """Scrape AAAI papers from DBLP (2018-2021)"""
        url = self.url_map[year]
        papers = []
        
        try:
            print(f"Fetching AAAI {year} data from DBLP...")
            soup = self.fetch_page(url, delay=1.0)
            
            if not soup:
                print(f"Could not fetch DBLP page for AAAI {year}")
                return papers
            
            # DBLP uses structured format with specific classes
            paper_entries = []
            
            # Method 1: Look for paper entries in DBLP format
            # DBLP uses <cite class="data"> for paper entries
            citations = soup.find_all('cite', class_='data')
            
            for cite in citations:
                try:
                    # Extract title - usually in <span class="title">
                    title_elem = cite.find('span', class_='title')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text().strip()
                    # Remove trailing period if present
                    if title.endswith('.'):
                        title = title[:-1]
                    
                    # Extract authors - usually before the title
                    authors_list = []
                    for author_span in cite.find_all('span', itemprop='author'):
                        author_name = author_span.get_text().strip()
                        if author_name:
                            authors_list.append(author_name)
                    
                    authors = ', '.join(authors_list)
                    
                    # Look for DOI or paper URL
                    paper_url = ""
                    doi_link = cite.find('a', href=re.compile(r'doi\.org|dx\.doi\.org'))
                    if doi_link:
                        paper_url = doi_link.get('href')
                    else:
                        # Look for other paper links
                        for link in cite.find_all('a', href=True):
                            href = link.get('href')
                            if 'aaai.org' in href or 'ojs.aaai.org' in href:
                                paper_url = href
                                break
                    
                    # Skip entries that don't look like papers
                    if len(title) < 10 or any(skip in title.lower() for skip in 
                                            ['proceedings', 'conference', 'workshop', 'front matter', 'preface']):
                        continue
                    
                    paper = {
                        'title': title,
                        'authors': authors,
                        'abstract': "",  # DBLP doesn't typically have abstracts
                        'year': year,
                        'conference': 'AAAI',
                        'url': paper_url
                    }
                    papers.append(paper)
                    
                except Exception as e:
                    print(f"Error processing DBLP entry: {e}")
                    continue
            
            # Method 2: If no citations found, try alternative structure
            if not papers:
                print(f"No citations found, trying alternative DBLP structure...")
                
                # Look for entries in <li> tags
                for li in soup.find_all('li', class_='entry'):
                    try:
                        title_elem = li.find('span', class_='title')
                        if title_elem:
                            title = title_elem.get_text().strip()
                            if title.endswith('.'):
                                title = title[:-1]
                            
                            # Extract authors
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
    
    def _scrape_ojs_aaai(self, year: int) -> List[Dict]:
        """Scrape AAAI papers from OJS format (2022+)"""
        url = self.url_map[year]
        papers = []
        
        try:
            soup = self.fetch_page(url, delay=1.0)
            if not soup:
                print(f"Could not fetch OJS page for AAAI {year}")
                return papers
            
            # Find all paper entries in OJS format
            article_summaries = soup.find_all('div', class_='obj_article_summary')
            
            if not article_summaries:
                # Try alternative selectors
                article_summaries = soup.find_all('article', class_='obj_article_summary')
            
            if not article_summaries:
                # Try even more generic approach
                article_summaries = soup.find_all('div', class_=['article-summary', 'paper-entry'])
            
            print(f"Found {len(article_summaries)} article summaries for AAAI {year}")
            
            for i, summary in enumerate(article_summaries):
                try:
                    # Extract title
                    title_elem = summary.find('h3', class_='title')
                    if not title_elem:
                        # Try alternative title selectors
                        title_elem = summary.find(['h2', 'h3', 'h4'], class_=['title', 'article-title'])
                    
                    if not title_elem:
                        continue
                        
                    title_link = title_elem.find('a')
                    if not title_link:
                        title = title_elem.get_text().strip()
                        paper_url = ""
                    else:
                        title = title_link.get_text().strip()
                        paper_url = title_link.get('href', '')
                        
                        # Make URL absolute if relative
                        if paper_url.startswith('/'):
                            paper_url = "https://ojs.aaai.org" + paper_url
                    
                    # Extract authors from meta section
                    meta_div = summary.find('div', class_='meta')
                    authors = ""
                    if meta_div:
                        authors_elem = meta_div.find('div', class_='authors')
                        if authors_elem:
                            authors = authors_elem.get_text().strip()
                        else:
                            # Try to find authors in different structure
                            authors_text = meta_div.get_text()
                            if 'by' in authors_text.lower():
                                authors = authors_text.strip()
                    
                    # Try to extract abstract - but avoid too many requests
                    abstract = ""
                    if paper_url and i < 10:  # Only fetch abstracts for first 10 papers as example
                        try:
                            paper_soup = self.fetch_page(paper_url, delay=0.5)
                            if paper_soup:
                                abstract_section = paper_soup.find('section', class_='item abstract')
                                if not abstract_section:
                                    abstract_section = paper_soup.find('div', class_='abstract')
                                
                                if abstract_section:
                                    abstract_p = abstract_section.find('p')
                                    if abstract_p:
                                        abstract = abstract_p.get_text().strip()
                        except:
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
                    
                    # Add delay every few papers
                    if i % 5 == 0:
                        time.sleep(random.uniform(0.3, 0.7))
                    
                except Exception as e:
                    print(f"Error processing OJS paper: {e}")
                    continue
        
        except Exception as e:
            print(f"Error scraping OJS AAAI {year}: {e}")
        
        return papers