"""
Paper Search Interface
Provides an easy-to-use interface for searching AI conference papers
"""

import os
import json
import argparse
from typing import List, Dict, Optional
from utils.vector_database import VectorDatabase
from utils.config import *
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PaperSearchInterface:
    def __init__(self):
        self.vdb = None
        self.connected = False
        
    def connect(self):
        """Connect to the vector database"""
        try:
            self.vdb = VectorDatabase()
            self.vdb.connect_to_milvus()
            self.vdb.collection = self.vdb.collection or self.vdb.Collection(MILVUS_COLLECTION_NAME)
            self.vdb.load_collection()
            self.connected = True
            logger.info("Connected to vector database successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to vector database: {e}")
            return False
    
    def search_papers(self, query: str, top_k: int = 10, 
                     conference: Optional[str] = None,
                     year: Optional[int] = None,
                     year_range: Optional[tuple] = None) -> List[Dict]:
        """Search for papers using semantic similarity"""
        if not self.connected:
            if not self.connect():
                return []
        
        try:
            # Handle year range filter
            if year_range and len(year_range) == 2:
                # For year range, we need to modify the search to use expression
                results = []
                for y in range(year_range[0], year_range[1] + 1):
                    year_results = self.vdb.search_similar_papers(
                        query, top_k=top_k//((year_range[1]-year_range[0]+1)), 
                        conference_filter=conference, year_filter=y
                    )
                    results.extend(year_results)
                
                # Sort by score and limit
                results = sorted(results, key=lambda x: x['score'], reverse=True)[:top_k]
            else:
                results = self.vdb.search_similar_papers(
                    query, top_k=top_k, 
                    conference_filter=conference, year_filter=year
                )
            
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def get_paper_by_id(self, paper_id: str) -> List[Dict]:
        """Get all chunks of a specific paper"""
        if not self.connected:
            if not self.connect():
                return []
        
        try:
            results = self.vdb.collection.query(
                expr=f'paper_id == "{paper_id}"',
                output_fields=["paper_id", "title", "authors", "conference", "year", 
                              "chunk_text", "chunk_index", "url", "abstract"]
            )
            return results
        except Exception as e:
            logger.error(f"Failed to get paper {paper_id}: {e}")
            return []
    
    def get_conference_stats(self) -> Dict:
        """Get statistics about papers in the database"""
        if not self.connected:
            if not self.connect():
                return {}
        
        try:
            # Get total count
            total_count = self.vdb.collection.num_entities
            
            # Get counts by conference
            conferences = ['ICML', 'NeuRIPS', 'ICLR', 'AAAI', 'IJCAI']
            conf_stats = {}
            
            for conf in conferences:
                try:
                    results = self.vdb.collection.query(
                        expr=f'conference == "{conf}"',
                        output_fields=["paper_id", "year"]
                    )
                    
                    # Count unique papers
                    unique_papers = len(set(r['paper_id'] for r in results))
                    
                    # Count by year
                    years = {}
                    for r in results:
                        year = r['year']
                        if year not in years:
                            years[year] = set()
                        years[year].add(r['paper_id'])
                    
                    year_counts = {year: len(papers) for year, papers in years.items()}
                    
                    conf_stats[conf] = {
                        'total_chunks': len(results),
                        'unique_papers': unique_papers,
                        'by_year': year_counts
                    }
                except:
                    conf_stats[conf] = {'total_chunks': 0, 'unique_papers': 0, 'by_year': {}}
            
            return {
                'total_chunks': total_count,
                'by_conference': conf_stats
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}
    
    def search_by_author(self, author_name: str, top_k: int = 10) -> List[Dict]:
        """Search papers by author name"""
        if not self.connected:
            if not self.connect():
                return []
        
        try:
            results = self.vdb.collection.query(
                expr=f'authors like "%{author_name}%"',
                output_fields=["paper_id", "title", "authors", "conference", "year", "url"],
                limit=top_k
            )
            
            # Remove duplicates by paper_id
            unique_results = {}
            for result in results:
                paper_id = result['paper_id']
                if paper_id not in unique_results:
                    unique_results[paper_id] = result
            
            return list(unique_results.values())
            
        except Exception as e:
            logger.error(f"Author search failed: {e}")
            return []
    
    def get_trending_topics(self, year: int, top_k: int = 10) -> List[Dict]:
        """Get trending topics for a specific year based on keyword frequency"""
        # This is a simplified version - would need more sophisticated analysis
        query_terms = [
            "transformer attention mechanism",
            "diffusion models generative",
            "large language models",
            "computer vision detection",
            "reinforcement learning policy",
            "graph neural networks",
            "self-supervised learning",
            "few-shot learning",
            "adversarial training robust",
            "multimodal learning vision language"
        ]
        
        trending = []
        for term in query_terms:
            results = self.search_papers(term, top_k=5, year=year)
            if results:
                trending.append({
                    'topic': term,
                    'paper_count': len(results),
                    'avg_score': sum(r['score'] for r in results) / len(results),
                    'sample_papers': results[:2]
                })
        
        # Sort by paper count and average score
        trending.sort(key=lambda x: (x['paper_count'], x['avg_score']), reverse=True)
        return trending[:top_k]
    
    def export_search_results(self, results: List[Dict], filename: str):
        """Export search results to JSON file"""
        try:
            os.makedirs(RESULTS_DIR, exist_ok=True)
            filepath = os.path.join(RESULTS_DIR, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Results exported to: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return None
    
    def interactive_search(self):
        """Interactive search interface"""
        print("🔍 AI Conference Paper Search Interface")
        print("="*60)
        
        if not self.connect():
            print("❌ Failed to connect to database. Please check Milvus server.")
            return
        
        # Show database stats
        stats = self.get_conference_stats()
        print(f"📊 Database contains {stats.get('total_chunks', 0)} text chunks")
        print("📚 Papers by conference:")
        for conf, conf_stats in stats.get('by_conference', {}).items():
            print(f"   {conf}: {conf_stats['unique_papers']} papers")
        
        print("\n💡 Search Options:")
        print("1. Semantic search (e.g., 'deep learning neural networks')")
        print("2. Author search (e.g., 'author:Yoshua Bengio')")
        print("3. Conference filter (e.g., 'transformers conference:ICLR')")
        print("4. Year filter (e.g., 'computer vision year:2023')")
        print("5. Year range (e.g., 'reinforcement learning years:2020-2023')")
        print("6. Get stats")
        print("7. Get trending topics")
        print("Type 'quit' to exit")
        
        while True:
            print("\n" + "-"*40)
            query = input("🔍 Enter search query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if query.lower() == 'stats':
                stats = self.get_conference_stats()
                print(json.dumps(stats, indent=2))
                continue
            
            if query.lower().startswith('trending'):
                parts = query.split()
                year = 2023  # default
                if len(parts) > 1 and parts[1].isdigit():
                    year = int(parts[1])
                
                trending = self.get_trending_topics(year)
                print(f"\n🔥 Trending topics in {year}:")
                for i, topic in enumerate(trending, 1):
                    print(f"{i}. {topic['topic']} ({topic['paper_count']} papers)")
                continue
            
            # Parse query for filters
            conference_filter = None
            year_filter = None
            year_range = None
            top_k = 10
            
            # Extract filters
            if ' conference:' in query:
                parts = query.split(' conference:')
                query = parts[0].strip()
                conference_filter = parts[1].split()[0].upper()
            
            if ' year:' in query:
                parts = query.split(' year:')
                query = parts[0].strip()
                year_filter = int(parts[1].split()[0])
            
            if ' years:' in query:
                parts = query.split(' years:')
                query = parts[0].strip()
                year_range_str = parts[1].split()[0]
                if '-' in year_range_str:
                    start, end = year_range_str.split('-')
                    year_range = (int(start), int(end))
            
            if ' top:' in query:
                parts = query.split(' top:')
                query = parts[0].strip()
                top_k = int(parts[1].split()[0])
            
            # Handle author search
            if query.startswith('author:'):
                author_name = query[7:].strip()
                results = self.search_by_author(author_name, top_k)
                print(f"\n📖 Found {len(results)} papers by '{author_name}':")
            else:
                # Regular semantic search
                results = self.search_papers(
                    query, top_k=top_k, 
                    conference=conference_filter, 
                    year=year_filter,
                    year_range=year_range
                )
                print(f"\n🎯 Found {len(results)} similar papers:")
            
            # Display results
            for i, result in enumerate(results, 1):
                title = result['title'][:60] + "..." if len(result['title']) > 60 else result['title']
                authors = result.get('authors', 'Unknown')[:40] + "..." if len(result.get('authors', '')) > 40 else result.get('authors', 'Unknown')
                
                score_info = f" (Score: {result.get('score', 0):.3f})" if 'score' in result else ""
                
                print(f"\n{i}. {title}")
                print(f"   👥 {authors}")
                print(f"   📅 {result['conference']} {result['year']}{score_info}")
                if result.get('url'):
                    print(f"   🔗 {result['url']}")
            
            # Option to export results
            if results:
                export = input("\n💾 Export results? (y/n): ").strip().lower()
                if export == 'y':
                    filename = f"search_results_{query.replace(' ', '_')[:20]}.json"
                    self.export_search_results(results, filename)


def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description="Search AI Conference Papers")
    parser.add_argument("--query", type=str, help="Search query")
    parser.add_argument("--conference", type=str, help="Filter by conference")
    parser.add_argument("--year", type=int, help="Filter by year")
    parser.add_argument("--top-k", type=int, default=10, help="Number of results")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--stats", action="store_true", help="Show database statistics")
    
    args = parser.parse_args()
    
    # Create search interface
    search = PaperSearchInterface()
    
    if args.interactive or not any([args.query, args.stats]):
        # Interactive mode
        search.interactive_search()
    
    elif args.stats:
        # Show statistics
        if search.connect():
            stats = search.get_conference_stats()
            print(json.dumps(stats, indent=2))
    
    elif args.query:
        # Command line search
        if search.connect():
            results = search.search_papers(
                args.query, 
                top_k=args.top_k,
                conference=args.conference,
                year=args.year
            )
            
            print(f"Found {len(results)} results for '{args.query}':")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result['title']}")
                print(f"   Authors: {result.get('authors', 'Unknown')}")
                print(f"   {result['conference']} {result['year']} (Score: {result.get('score', 0):.3f})")


if __name__ == "__main__":
    main()