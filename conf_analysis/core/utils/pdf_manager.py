#!/usr/bin/env python3
"""
PDF Manager for Conference Papers  
Combined PDF downloading and management utilities for AI conference papers.
Supports downloading, status checking, and management operations.
"""

import os
import json
import asyncio
import aiohttp
import aiofiles
import argparse
import sys
from pathlib import Path
from urllib.parse import urlparse, urljoin
import time
import hashlib
from typing import List, Dict, Optional, Tuple
import logging
from tqdm.asyncio import tqdm
import re
from bs4 import BeautifulSoup

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import *

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFDownloader:
    def __init__(self, force_download_blocked=False):
        self.session = None
        self.downloaded_count = 0
        self.failed_count = 0
        self.skipped_count = 0
        self.force_download_blocked = force_download_blocked  # Allow forcing downloads even from blocked domains
        self.session_timeout = aiohttp.ClientTimeout(total=PDF_DOWNLOAD_TIMEOUT)
        
        # Enhanced headers to better mimic modern browsers and avoid bot detection
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Cache-Control': 'max-age=0',
        }

    async def __aenter__(self):
        """Async context manager entry"""
        # Create cookie jar for session persistence
        jar = aiohttp.CookieJar(unsafe=True)
        connector = aiohttp.TCPConnector(
            limit=MAX_CONCURRENT_DOWNLOADS,
            limit_per_host=1,  # Only 1 connection per host to be more polite
            ttl_dns_cache=300,
            use_dns_cache=True
        )
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=self.session_timeout,
            headers=self.headers,
            cookie_jar=jar
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    def generate_filename(self, title: str, conference: str, year: int, paper_id: str = None) -> str:
        """Generate a safe filename for the PDF"""
        # Clean the title
        safe_title = re.sub(r'[^\w\s-]', '', title.strip())
        safe_title = re.sub(r'[-\s]+', '_', safe_title)
        
        # Truncate if too long
        if len(safe_title) > 100:
            safe_title = safe_title[:100]
        
        # Generate a hash for uniqueness
        if paper_id:
            file_hash = paper_id[:8]
        else:
            hash_input = f"{title}_{conference}_{year}".encode('utf-8')
            file_hash = hashlib.md5(hash_input).hexdigest()[:8]
        
        return f"{safe_title}_{year}_{file_hash}.pdf"

    async def extract_pdf_links_from_html(self, url: str, base_url: str = None) -> List[str]:
        """Extract PDF download links from HTML page"""
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    return []
                
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')
                
                pdf_links = []
                base_url = base_url or url
                
                # Common PDF link patterns
                pdf_patterns = [
                    r'\.pdf$',
                    r'download.*pdf',
                    r'pdf.*download',
                    r'\.pdf\?',
                ]
                
                # Look for direct PDF links
                for link in soup.find_all('a', href=True):
                    href = link.get('href')
                    text = link.get_text().strip().lower()
                    
                    # Check if link points to PDF
                    if any(re.search(pattern, href, re.IGNORECASE) for pattern in pdf_patterns):
                        # Make URL absolute
                        if href.startswith('http'):
                            pdf_links.append(href)
                        else:
                            pdf_links.append(urljoin(base_url, href))
                    
                    # Check if link text indicates PDF
                    elif 'pdf' in text and ('download' in text or 'full text' in text):
                        if href.startswith('http'):
                            pdf_links.append(href)
                        else:
                            pdf_links.append(urljoin(base_url, href))
                
                # AAAI specific: look for PDF links in multiple patterns
                if 'ojs.aaai.org' in base_url:
                    for link in soup.find_all('a', href=True):
                        href = link.get('href')
                        text = link.get_text().strip().lower()
                        
                        # Look for various AAAI PDF patterns
                        if ('pdf' in text or 'download' in text) and (
                            '/download/' in href or 
                            '/view/' in href or
                            'pdf' in href.lower()
                        ):
                            # Make URL absolute
                            if href.startswith('/'):
                                pdf_url = 'https://ojs.aaai.org' + href
                                pdf_links.append(pdf_url)
                            elif href.startswith('http'):
                                pdf_links.append(href)
                    
                    # Also try common AAAI PDF URL patterns by ID extraction
                    if '/article/view/' in base_url:
                        match = re.search(r'/article/view/(\d+)', base_url)
                        if match:
                            article_id = match.group(1)
                            # Try common PDF download patterns
                            potential_urls = [
                                f'https://ojs.aaai.org/index.php/AAAI/article/download/{article_id}',
                                f'https://ojs.aaai.org/index.php/AAAI/article/viewFile/{article_id}',
                            ]
                            pdf_links.extend(potential_urls)
                
                return list(set(pdf_links))  # Remove duplicates
                
        except Exception as e:
            logger.error(f"Error extracting PDF links from {url}: {e}")
            return []

    def get_direct_pdf_url(self, url: str) -> str:
        """Convert paper page URL to direct PDF URL for known conferences"""
        if 'ojs.aaai.org' in url and '/article/view/' in url:
            # For AAAI, try multiple PDF URL patterns
            # Pattern: https://ojs.aaai.org/index.php/AAAI/article/view/27749
            # Common patterns:
            # 1. /download/ID/pdf-file-id  
            # 2. /download/ID
            # For now, try the HTML parsing approach instead
            return url
        elif 'aaai.org/papers/' in url:
            # For new AAAI paper format, try direct PDF patterns
            # Pattern: https://aaai.org/papers/00003-title/
            # Try: https://aaai.org/papers/00003-title/pdf or https://aaai.org/papers/00003-title.pdf
            if not url.endswith('/'):
                url += '/'
            potential_urls = [
                url + 'pdf',
                url.rstrip('/') + '.pdf',
                url + 'download'
            ]
            # Return the first potential URL for now
            return potential_urls[0]
        elif 'openreview.net/forum' in url:
            # For ICLR (OpenReview), try to get PDF
            # Pattern: https://openreview.net/forum?id=rhgIgTSSxW
            # To: https://openreview.net/pdf?id=rhgIgTSSxW
            pdf_url = url.replace('/forum?', '/pdf?')
            return pdf_url
        elif 'proceedings.mlr.press' in url:
            # For ICML, try to get PDF
            # Pattern: https://proceedings.mlr.press/v235/abad-rocamora24a.html
            # To: https://proceedings.mlr.press/v235/abad-rocamora24a/abad-rocamora24a.pdf
            if url.endswith('.html'):
                # Handle malformed URLs with duplicate paths
                if url.count('https://proceedings.mlr.press') > 1:
                    # Extract the correct URL part
                    parts = url.split('https://proceedings.mlr.press')
                    if len(parts) > 2:
                        url = 'https://proceedings.mlr.press' + parts[-1]
                
                base_url = url[:-5]  # Remove .html
                paper_name = base_url.split('/')[-1]
                pdf_url = f"{base_url}/{paper_name}.pdf"
                return pdf_url
        elif 'papers.nips.cc' in url:
            # For NeurIPS, extract PDF URL
            # Pattern: https://papers.nips.cc/paper_files/paper/2024/hash/000f947dcaff8fbffcc3f53a1314f358-Abstract-Conference.html
            # To: https://papers.nips.cc/paper_files/paper/2024/file/000f947dcaff8fbffcc3f53a1314f358-Paper-Conference.pdf
            if '-Abstract-Conference.html' in url:
                pdf_url = url.replace('-Abstract-Conference.html', '-Paper-Conference.pdf').replace('/hash/', '/file/')
                return pdf_url
        
        # Return original URL if no conversion pattern matches
        return url

    def get_domain_specific_delay(self, url: str) -> float:
        """Get appropriate delay for specific domains"""
        if 'aaai.org' in url:
            return PDF_DOWNLOAD_DELAY * 2  # Double delay for AAAI (Cloudflare protected)
        elif 'openreview.net' in url:
            return PDF_DOWNLOAD_DELAY * 0.5  # Faster for OpenReview
        else:
            return PDF_DOWNLOAD_DELAY

    async def download_pdf(self, url: str, filepath: Path, semaphore: asyncio.Semaphore, 
                          max_retries: int = MAX_RETRIES) -> bool:
        """Download a single PDF with retry logic"""
        async with semaphore:
            # Try direct PDF URL conversion first
            direct_pdf_url = self.get_direct_pdf_url(url)
            if direct_pdf_url != url:
                logger.info(f"Converted URL: {url} -> {direct_pdf_url}")
                url = direct_pdf_url
            
            # Get domain-specific delay
            domain_delay = self.get_domain_specific_delay(url)
            
            for attempt in range(max_retries):
                try:
                    # Add delay between requests (use domain-specific delay)
                    if attempt > 0:
                        await asyncio.sleep(domain_delay * (attempt + 1))
                    else:
                        # Even first attempt should have some delay for AAAI
                        if 'aaai.org' in url:
                            await asyncio.sleep(domain_delay)
                    
                    async with self.session.get(url) as response:
                        if response.status == 200:
                            # Check if this is a Cloudflare challenge page
                            content_type = response.headers.get('content-type', '').lower()
                            if 'text/html' in content_type:
                                text_sample = await response.text()
                                if any(indicator in text_sample.lower() for indicator in [
                                    'just a moment', 'checking your browser', 'cloudflare', 
                                    'challenge', 'verify you are human'
                                ]):
                                    logger.warning(f"Cloudflare challenge detected for {url}")
                                    # Wait longer and try again on next retry
                                    await asyncio.sleep(5)
                                    continue
                            
                            # Check if content is actually a PDF
                            if 'pdf' not in content_type and 'application/octet-stream' not in content_type:
                                # Try to extract PDF links from HTML page
                                pdf_links = await self.extract_pdf_links_from_html(url)
                                if pdf_links:
                                    # Try the first PDF link found
                                    return await self.download_pdf(pdf_links[0], filepath, semaphore, max_retries=1)
                                else:
                                    logger.warning(f"No PDF found at {url}, content-type: {content_type}")
                                    return False
                            
                            # Create directory if it doesn't exist
                            filepath.parent.mkdir(parents=True, exist_ok=True)
                            
                            # Download the file
                            async with aiofiles.open(filepath, 'wb') as f:
                                async for chunk in response.content.iter_chunked(CHUNK_SIZE):
                                    await f.write(chunk)
                            
                            # Verify the file was downloaded and has content
                            if filepath.exists() and filepath.stat().st_size > 1000:  # At least 1KB
                                self.downloaded_count += 1
                                logger.info(f"Downloaded: {filepath.name}")
                                return True
                            else:
                                # Remove invalid file
                                if filepath.exists():
                                    filepath.unlink()
                                logger.warning(f"Downloaded file is too small or empty: {url}")
                                return False
                        
                        elif response.status == 404:
                            logger.warning(f"PDF not found (404): {url}")
                            return False
                        else:
                            logger.warning(f"HTTP {response.status} for {url}")
                            
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout downloading {url} (attempt {attempt + 1})")
                except Exception as e:
                    logger.error(f"Error downloading {url} (attempt {attempt + 1}): {e}")
                
                # Wait before retry (use domain-specific delay)
                if attempt < max_retries - 1:
                    await asyncio.sleep(domain_delay * 2)
            
            self.failed_count += 1
            logger.error(f"Failed to download after {max_retries} attempts: {url}")
            return False

    async def download_papers_batch(self, papers: List[Dict], output_dir: Path, 
                                  conference: str, year: int) -> Dict:
        """Download a batch of papers concurrently"""
        if not papers:
            return {'downloaded': 0, 'failed': 0, 'skipped': 0}
        
        # Check if this conference has known blocking issues
        if not self.force_download_blocked and conference == 'AAAI' and any('aaai.org/papers/' in paper.get('url', '') for paper in papers):
            logger.warning(f"AAAI {year} papers are protected by Cloudflare. Skipping batch to avoid 403 errors.")
            logger.info(f"Consider downloading AAAI papers manually or using a different method.")
            logger.info(f"To force download attempt, set force_download_blocked=True when creating PDFDownloader")
            return {'downloaded': 0, 'failed': 0, 'skipped': len(papers)}
        
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)
        tasks = []
        
        for paper in papers:
            pdf_url = paper.get('pdf_url') or paper.get('url')
            title = paper.get('title', 'Unknown')
            
            if not pdf_url:
                continue
            
            filename = self.generate_filename(title, conference, year, paper.get('id'))
            filepath = output_dir / conference / filename
            
            # Skip if file already exists and is not empty
            if filepath.exists() and filepath.stat().st_size > 1000:
                self.skipped_count += 1
                continue
            
            task = self.download_pdf(pdf_url, filepath, semaphore)
            tasks.append(task)
        
        if tasks:
            # Use tqdm for progress bar
            results = await tqdm.gather(*tasks, desc=f"Downloading {conference} {year}")
            successful = sum(results)
            logger.info(f"Downloaded {successful}/{len(tasks)} PDFs for {conference} {year}")
        
        return {
            'downloaded': self.downloaded_count,
            'failed': self.failed_count,
            'skipped': self.skipped_count
        }

    def load_papers_data(self, data_dir: Path = None) -> Dict[str, Dict[int, List[Dict]]]:
        """Load papers data from JSON files"""
        if data_dir is None:
            data_dir = Path(RAW_DATA_DIR)
        
        papers_data = {}
        
        for json_file in data_dir.glob("*.json"):
            try:
                # Parse filename to get conference and year
                filename = json_file.stem
                parts = filename.split('_')
                if len(parts) >= 2:
                    conference = parts[0]
                    year = int(parts[1])
                    
                    with open(json_file, 'r', encoding='utf-8') as f:
                        papers = json.load(f)
                    
                    if conference not in papers_data:
                        papers_data[conference] = {}
                    papers_data[conference][year] = papers
                    
                    logger.info(f"Loaded {len(papers)} papers for {conference} {year}")
                    
            except Exception as e:
                logger.error(f"Error loading {json_file}: {e}")
        
        return papers_data

    async def download_all_papers(self, conferences: List[str] = None, 
                                years: List[int] = None) -> Dict:
        """Download all papers for specified conferences and years"""
        papers_data = self.load_papers_data()
        
        total_stats = {'downloaded': 0, 'failed': 0, 'skipped': 0}
        output_dir = Path(PDF_DATA_DIR)
        
        for conference, years_data in papers_data.items():
            if conferences and conference not in conferences:
                continue
                
            for year, papers in years_data.items():
                if years and year not in years:
                    continue
                
                logger.info(f"Starting download for {conference} {year} ({len(papers)} papers)")
                
                # Reset counters for this batch
                self.downloaded_count = 0
                self.failed_count = 0
                self.skipped_count = 0
                
                stats = await self.download_papers_batch(papers, output_dir, conference, year)
                
                # Update total stats
                for key in total_stats:
                    total_stats[key] += stats[key]
                
                logger.info(f"Completed {conference} {year}: {stats}")
        
        return total_stats


class PDFManager:
    """PDF Management utilities for checking status and managing downloads"""
    
    def __init__(self):
        self.pdf_dir = Path(PDF_DATA_DIR)
        self.results_dir = Path(RESULTS_DIR)
    
    def create_directory_structure(self):
        """Create and display directory structure preview"""
        print("📁 PDF存储目录结构:")
        print(f"   {self.pdf_dir}/")
        
        if self.pdf_dir.exists():
            for conf_dir in sorted(os.listdir(self.pdf_dir)):
                conf_path = self.pdf_dir / conf_dir
                if conf_path.is_dir():
                    print(f"   ├── {conf_dir}/")
                    
                    # Count PDFs in each conference directory
                    pdf_count = len(list(conf_path.glob("*.pdf")))
                    if pdf_count > 0:
                        print(f"   │   └── {pdf_count} PDF files")
        
        print(f"\n📊 统计结果目录: {self.results_dir}/")
    
    def get_download_status(self) -> Dict:
        """Get comprehensive download status"""
        status = {
            'conferences': {},
            'total_pdfs': 0,
            'total_papers': 0,
            'download_rate': 0.0
        }
        
        # Load papers data to compare with downloaded PDFs
        data_dir = Path(RAW_DATA_DIR)
        
        for json_file in data_dir.glob("*.json"):
            try:
                # Parse filename
                filename = json_file.stem
                parts = filename.split('_')
                if len(parts) >= 2:
                    conference = parts[0]
                    year = int(parts[1])
                    
                    # Load paper data
                    with open(json_file, 'r', encoding='utf-8') as f:
                        papers = json.load(f)
                    
                    # Count downloaded PDFs
                    pdf_dir = self.pdf_dir / conference
                    downloaded_pdfs = 0
                    if pdf_dir.exists():
                        downloaded_pdfs = len(list(pdf_dir.glob("*.pdf")))
                    
                    # Store conference status
                    if conference not in status['conferences']:
                        status['conferences'][conference] = {}
                    
                    status['conferences'][conference][year] = {
                        'total_papers': len(papers),
                        'downloaded_pdfs': downloaded_pdfs,
                        'download_rate': downloaded_pdfs / len(papers) if papers else 0
                    }
                    
                    # Update totals
                    status['total_papers'] += len(papers)
                    status['total_pdfs'] += downloaded_pdfs
                    
            except Exception as e:
                logger.error(f"Error processing {json_file}: {e}")
        
        # Calculate overall download rate
        if status['total_papers'] > 0:
            status['download_rate'] = status['total_pdfs'] / status['total_papers']
        
        return status
    
    def print_status_report(self):
        """Print comprehensive status report"""
        status = self.get_download_status()
        
        print("\n" + "="*80)
        print("📋 PDF DOWNLOAD STATUS REPORT")
        print("="*80)
        
        print(f"📊 Overall Statistics:")
        print(f"   Total Papers: {status['total_papers']:,}")
        print(f"   Downloaded PDFs: {status['total_pdfs']:,}")
        print(f"   Overall Download Rate: {status['download_rate']:.1%}")
        
        print(f"\n📚 By Conference:")
        for conference, years_data in status['conferences'].items():
            conf_total_papers = sum(data['total_papers'] for data in years_data.values())
            conf_total_pdfs = sum(data['downloaded_pdfs'] for data in years_data.values())
            conf_rate = conf_total_pdfs / conf_total_papers if conf_total_papers > 0 else 0
            
            print(f"   {conference}: {conf_total_pdfs:,}/{conf_total_papers:,} ({conf_rate:.1%})")
            
            for year, data in sorted(years_data.items()):
                print(f"     {year}: {data['downloaded_pdfs']:,}/{data['total_papers']:,} ({data['download_rate']:.1%})")
        
        print("\n" + "="*80)
    
    def save_status_json(self):
        """Save download status to JSON file"""
        status = self.get_download_status()
        
        # Ensure results directory exists
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        status_file = self.results_dir / 'pdf_download_status.json'
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Status saved to: {status_file}")
    
    async def download_missing_papers(self, conferences: List[str] = None, 
                                    years: List[int] = None):
        """Download only missing papers (incremental download)"""
        print("🔄 Starting incremental download for missing papers...")
        
        async with PDFDownloader() as downloader:
            stats = await downloader.download_all_papers(conferences, years)
        
        print(f"\n✅ Download completed!")
        print(f"   Downloaded: {stats['downloaded']}")
        print(f"   Failed: {stats['failed']}")
        print(f"   Skipped (already exist): {stats['skipped']}")
        
        # Update status
        self.save_status_json()
        self.print_status_report()


def main():
    """Main CLI interface for PDF management"""
    parser = argparse.ArgumentParser(description='PDF Download Management Tool')
    parser.add_argument('action', choices=['status', 'download', 'missing', 'check'],
                       help='Action to perform')
    parser.add_argument('--conferences', nargs='+', 
                       choices=['ICML', 'NeuRIPS', 'ICLR', 'AAAI', 'IJCAI'],
                       help='Conferences to process')
    parser.add_argument('--years', nargs='+', type=int,
                       help='Years to process')
    
    args = parser.parse_args()
    
    manager = PDFManager()
    
    if args.action == 'status':
        manager.print_status_report()
        manager.save_status_json()
    
    elif args.action == 'check':
        manager.create_directory_structure()
        manager.print_status_report()
    
    elif args.action == 'download':
        async def download_all():
            async with PDFDownloader() as downloader:
                stats = await downloader.download_all_papers(args.conferences, args.years)
                print(f"Download completed: {stats}")
        
        asyncio.run(download_all())
        manager.save_status_json()
    
    elif args.action == 'missing':
        asyncio.run(manager.download_missing_papers(args.conferences, args.years))


if __name__ == "__main__":
    main()