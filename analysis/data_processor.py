"""
Data processing module for conference papers
"""

import pandas as pd
import json
import os
import re
from typing import List, Dict, Tuple
import nltk
from collections import Counter
import string


class DataProcessor:
    def __init__(self):
        self.setup_nltk()
        
    def setup_nltk(self):
        """Download required NLTK data"""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
            
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
            
        try:
            nltk.data.find('taggers/averaged_perceptron_tagger')
        except LookupError:
            nltk.download('averaged_perceptron_tagger')
    
    def load_raw_data(self, data_dir: str = 'outputs/data/raw') -> pd.DataFrame:
        """Load all raw JSON files and combine into DataFrame"""
        all_papers = []
        
        for filename in os.listdir(data_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(data_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        papers = json.load(f)
                        all_papers.extend(papers)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
        
        df = pd.DataFrame(all_papers)
        return df
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not isinstance(text, str):
            return ""
            
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep letters, numbers, and basic punctuation
        text = re.sub(r'[^\w\s\-.,;:!?()]', ' ', text)
        
        # Remove numbers standalone
        text = re.sub(r'\b\d+\b', '', text)
        
        return text.strip()
    
    def extract_keywords_from_text(self, text: str, min_length: int = 3) -> List[str]:
        """Extract keywords from text using NLTK"""
        from nltk.corpus import stopwords
        from nltk.tokenize import word_tokenize
        from nltk.tag import pos_tag
        
        if not text:
            return []
            
        # Clean text
        text = self.clean_text(text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and short words
        stop_words = set(stopwords.words('english'))
        # Add custom stopwords for ML conferences
        custom_stops = {
            'learning', 'neural', 'network', 'networks', 'model', 'models',
            'method', 'methods', 'approach', 'approaches', 'algorithm', 'algorithms',
            'based', 'using', 'via', 'toward', 'towards', 'paper', 'study',
            'propose', 'proposed', 'show', 'shows', 'present', 'presented',
            'new', 'novel', 'existing', 'previous', 'recent', 'current'
        }
        stop_words.update(custom_stops)
        
        # Filter tokens
        keywords = []
        for token in tokens:
            if (len(token) >= min_length and 
                token not in stop_words and 
                token not in string.punctuation and
                not token.isdigit()):
                keywords.append(token)
        
        # POS tagging to keep only nouns, adjectives, and verbs
        pos_tags = pos_tag(keywords)
        filtered_keywords = []
        for word, pos in pos_tags:
            if pos.startswith(('NN', 'JJ', 'VB')):  # Nouns, adjectives, verbs
                filtered_keywords.append(word)
        
        return filtered_keywords
    
    def extract_ngrams(self, text: str, n: int = 2) -> List[str]:
        """Extract n-grams from text"""
        from nltk.util import ngrams
        from nltk.tokenize import word_tokenize
        
        if not text:
            return []
            
        text = self.clean_text(text)
        tokens = word_tokenize(text)
        
        # Filter short tokens
        tokens = [t for t in tokens if len(t) >= 3]
        
        if len(tokens) < n:
            return []
            
        n_grams = list(ngrams(tokens, n))
        return [' '.join(gram) for gram in n_grams]
    
    def process_papers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process papers DataFrame and extract features"""
        processed_df = df.copy()
        
        # Clean title and abstract
        processed_df['title_clean'] = df['title'].apply(self.clean_text)
        processed_df['abstract_clean'] = df['abstract'].apply(self.clean_text)
        
        # Extract keywords from title and abstract
        processed_df['title_keywords'] = df['title'].apply(
            lambda x: self.extract_keywords_from_text(x)
        )
        processed_df['abstract_keywords'] = df['abstract'].apply(
            lambda x: self.extract_keywords_from_text(x)
        )
        
        # Combine all keywords
        processed_df['all_keywords'] = (
            processed_df['title_keywords'] + processed_df['abstract_keywords']
        )
        
        # Extract bigrams from title and abstract
        processed_df['title_bigrams'] = df['title'].apply(
            lambda x: self.extract_ngrams(x, 2)
        )
        processed_df['abstract_bigrams'] = df['abstract'].apply(
            lambda x: self.extract_ngrams(x, 2)
        )
        
        # Calculate text statistics
        processed_df['title_length'] = df['title'].str.len().fillna(0)
        processed_df['abstract_length'] = df['abstract'].str.len().fillna(0)
        processed_df['abstract_word_count'] = df['abstract'].apply(
            lambda x: len(str(x).split()) if pd.notna(x) else 0
        )
        
        return processed_df
    
    def get_keyword_frequencies(self, df: pd.DataFrame, 
                              min_freq: int = 3) -> Dict[str, int]:
        """Get keyword frequencies across all papers"""
        all_keywords = []
        for keywords_list in df['all_keywords']:
            if isinstance(keywords_list, list):
                all_keywords.extend(keywords_list)
        
        keyword_freq = Counter(all_keywords)
        
        # Filter by minimum frequency
        filtered_freq = {k: v for k, v in keyword_freq.items() if v >= min_freq}
        
        return dict(sorted(filtered_freq.items(), key=lambda x: x[1], reverse=True))
    
    def get_bigram_frequencies(self, df: pd.DataFrame, 
                             min_freq: int = 2) -> Dict[str, int]:
        """Get bigram frequencies across all papers"""
        all_bigrams = []
        for bigrams_list in df['title_bigrams']:
            if isinstance(bigrams_list, list):
                all_bigrams.extend(bigrams_list)
        for bigrams_list in df['abstract_bigrams']:
            if isinstance(bigrams_list, list):
                all_bigrams.extend(bigrams_list)
        
        bigram_freq = Counter(all_bigrams)
        
        # Filter by minimum frequency
        filtered_freq = {k: v for k, v in bigram_freq.items() if v >= min_freq}
        
        return dict(sorted(filtered_freq.items(), key=lambda x: x[1], reverse=True))
    
    def save_processed_data(self, df: pd.DataFrame, filename: str):
        """Save processed data to CSV"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Saved processed data to {filename}")
    
    def get_conference_statistics(self, df: pd.DataFrame) -> Dict:
        """Get basic statistics by conference and year"""
        stats = {}
        
        # Papers by conference
        conf_counts = df['conference'].value_counts().to_dict()
        stats['papers_by_conference'] = conf_counts
        
        # Papers by year
        year_counts = df['year'].value_counts().sort_index().to_dict()
        stats['papers_by_year'] = year_counts
        
        # Papers by conference and year
        conf_year = df.groupby(['conference', 'year']).size().unstack(fill_value=0)
        stats['papers_by_conference_year'] = conf_year.to_dict()
        
        # Average abstract length by conference
        avg_abstract_len = df.groupby('conference')['abstract_length'].mean().to_dict()
        stats['avg_abstract_length'] = avg_abstract_len
        
        return stats