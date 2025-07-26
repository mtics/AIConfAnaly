"""
ICLR paper scraper using OpenReview API
"""

from .base_scraper import BaseScraper
from typing import List, Dict
import requests
import json


class ICLRScraper(BaseScraper):
    def __init__(self):
        super().__init__("ICLR", "https://api.openreview.net/")
        
        # ICLR venue IDs for each year
        self.venue_map = {
            2018: "ICLR.cc/2018/Conference",
            2019: "ICLR.cc/2019/Conference", 
            2020: "ICLR.cc/2020/Conference",
            2021: "ICLR.cc/2021/Conference",
            2022: "ICLR.cc/2022/Conference",
            2023: "ICLR.cc/2023/Conference",
            2024: "ICLR.cc/2024/Conference"
        }
    
    def get_papers_for_year(self, year: int) -> List[Dict]:
        """Extract ICLR papers for a specific year using OpenReview API"""
        if year not in self.venue_map:
            raise ValueError(f"Venue mapping not found for year {year}")
            
        venue_id = self.venue_map[year]
        
        # Query OpenReview API for accepted papers
        url = f"{self.base_url}notes"
        params = {
            'invitation': f'{venue_id}/-/Blind_Submission',
            'details': 'replyCount,invitation,forum',
            'limit': 1000,
            'offset': 0
        }
        
        papers = []
        offset = 0
        
        while True:
            params['offset'] = offset
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            notes = data.get('notes', [])
            
            if not notes:
                break
                
            for note in notes:
                try:
                    # Check if paper was accepted (has decision)
                    content = note.get('content', {})
                    
                    # Skip if not accepted or missing essential info
                    if not content.get('title') or not content.get('abstract'):
                        continue
                    
                    title = content['title']
                    abstract = content['abstract']
                    authors = ', '.join(content.get('authors', []))
                    
                    paper = {
                        'title': title,
                        'authors': authors,
                        'abstract': abstract,
                        'year': year,
                        'conference': 'ICLR',
                        'url': f"https://openreview.net/forum?id={note['id']}"
                    }
                    papers.append(paper)
                    
                except Exception as e:
                    print(f"Error processing paper: {e}")
                    continue
            
            offset += len(notes)
            if len(notes) < 1000:  # Last batch
                break
                
        return papers