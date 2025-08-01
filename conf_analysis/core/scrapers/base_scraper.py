"""
Base scraper class for conference paper extraction
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
from abc import ABC, abstractmethod
from typing import List, Dict
import json


class BaseScraper(ABC):
    def __init__(self, conference_name: str, base_url: str):
        self.conference_name = conference_name
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def fetch_page(self, url: str, delay: float = 1.0, retries: int = 3) -> BeautifulSoup:
        """Fetch and parse a web page with retry mechanism"""
        time.sleep(delay)  # Rate limiting
        
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
                
            except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
                if attempt < retries - 1:
                    wait_time = delay * (2 ** attempt)  # Exponential backoff
                    print(f"   Retry {attempt + 1}/{retries} in {wait_time:.1f}s due to: {e}")
                    time.sleep(wait_time)
                else:
                    print(f"   Failed after {retries} attempts: {e}")
                    raise
        
        return None
    
    @abstractmethod
    def get_papers_for_year(self, year: int) -> List[Dict]:
        """Extract papers for a specific year"""
        pass
    
    def save_papers(self, papers: List[Dict], filename: str):
        """Save papers to JSON file"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(papers, f, ensure_ascii=False, indent=2)
    
    def scrape_all_years(self, years: List[int]) -> Dict[int, List[Dict]]:
        """Scrape papers for all specified years"""
        all_papers = {}
        for year in years:
            print(f"Scraping {self.conference_name} {year}...")
            try:
                papers = self.get_papers_for_year(year)
                all_papers[year] = papers
                
                # Save year data
                filename = f"outputs/data/raw/{self.conference_name}_{year}.json"
                self.save_papers(papers, filename)
                print(f"Saved {len(papers)} papers for {self.conference_name} {year}")
                
            except Exception as e:
                print(f"Error scraping {self.conference_name} {year}: {e}")
                all_papers[year] = []
                
        return all_papers