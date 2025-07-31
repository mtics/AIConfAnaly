"""
Main script for conference paper analysis
"""

import os
import sys
import argparse
from datetime import datetime
import pandas as pd

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.config import CONFERENCES
from scrapers import ICMLScraper, NeuRIPSScraper, ICLRScraper, AAAIScraper, IJCAIScraper
from analysis import DataProcessor, FieldExtractor, Visualizer


def scrape_conferences(conferences: list = None, years: list = None):
    """Scrape papers from specified conferences and years"""
    print("Starting conference paper scraping...")
    
    # Initialize scrapers
    scrapers = {
        'ICML': ICMLScraper(),
        'NeuRIPS': NeuRIPSScraper(),
        'ICLR': ICLRScraper(),
        'AAAI': AAAIScraper(),
        'IJCAI': IJCAIScraper()
    }
    
    # Filter conferences if specified
    if conferences:
        scrapers = {k: v for k, v in scrapers.items() if k in conferences}
    
    # Scrape each conference
    for conf_name, scraper in scrapers.items():
        print(f"\\nScraping {conf_name}...")
        conf_years = years if years else CONFERENCES[conf_name]['years']
        
        try:
            scraper.scrape_all_years(conf_years)
            print(f"Successfully scraped {conf_name}")
        except Exception as e:
            print(f"Error scraping {conf_name}: {e}")
    
    print("\\nScraping completed!")


def analyze_papers(visualize: bool = True, save_results: bool = True):
    """Analyze scraped papers and generate insights"""
    print("Starting paper analysis...")
    
    # Initialize processors
    processor = DataProcessor()
    field_extractor = FieldExtractor()
    visualizer = Visualizer() if visualize else None
    
    # Load and process data
    print("Loading raw data...")
    try:
        df = processor.load_raw_data()
        print(f"Loaded {len(df)} papers")
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    
    if df.empty:
        print("No data found. Please run scraping first.")
        return
    
    # Process papers
    print("Processing papers...")
    processed_df = processor.process_papers(df)
    
    # Extract research fields
    print("Extracting research fields...")
    field_df = field_extractor.extract_fields_by_keywords(processed_df)
    field_df = field_extractor.get_dominant_field(field_df)
    
    # Perform clustering and topic modeling
    print("Performing content clustering...")
    clustered_df = field_extractor.cluster_papers_by_content(field_df)
    
    print("Performing topic modeling...")
    topic_df, topics_info = field_extractor.topic_modeling_lda(clustered_df)
    
    # Get statistics
    print("Generating statistics...")
    basic_stats = processor.get_conference_statistics(topic_df)
    field_stats = field_extractor.get_field_statistics(topic_df)
    keyword_freq = processor.get_keyword_frequencies(topic_df)
    bigram_freq = processor.get_bigram_frequencies(topic_df)
    
    # Save processed data
    if save_results:
        print("Saving processed data...")
        processor.save_processed_data(
            topic_df, 'outputs/data/processed/all_papers_processed.csv'
        )
        
        # Save statistics
        import json
        with open('outputs/results/basic_statistics.json', 'w', encoding='utf-8') as f:
            json.dump(basic_stats, f, ensure_ascii=False, indent=2, default=str)
        
        with open('outputs/results/field_statistics.json', 'w', encoding='utf-8') as f:
            json.dump(field_stats, f, ensure_ascii=False, indent=2, default=str)
        
        with open('outputs/results/keyword_frequencies.json', 'w', encoding='utf-8') as f:
            json.dump(keyword_freq, f, ensure_ascii=False, indent=2)
        
        with open('outputs/results/topics_info.json', 'w', encoding='utf-8') as f:
            json.dump(topics_info, f, ensure_ascii=False, indent=2, default=str)
    
    # Generate visualizations
    if visualize and visualizer:
        print("Generating visualizations...")
        
        # Basic plots
        visualizer.plot_papers_by_conference(topic_df)
        visualizer.plot_papers_by_year(topic_df)
        visualizer.plot_conference_year_heatmap(topic_df)
        
        # Field analysis plots
        visualizer.plot_field_distribution(topic_df)
        visualizer.plot_field_trends(topic_df)
        visualizer.plot_field_by_conference(topic_df)
        
        # Keyword analysis
        visualizer.create_keyword_wordcloud(keyword_freq, "All Keywords")
        visualizer.plot_top_keywords(keyword_freq, top_n=25)
        
        # Abstract analysis
        visualizer.plot_abstract_length_distribution(topic_df)
        
        # Interactive dashboard
        visualizer.create_interactive_dashboard(topic_df, keyword_freq)
        
        # Save summary
        all_stats = {**basic_stats, **field_stats}
        visualizer.save_summary_statistics(all_stats)
    
    # Print summary
    print("\\n" + "="*50)
    print("ANALYSIS SUMMARY")
    print("="*50)
    print(f"Total papers analyzed: {len(topic_df)}")
    print(f"Conferences: {', '.join(topic_df['conference'].unique())}")
    print(f"Years: {topic_df['year'].min()} - {topic_df['year'].max()}")
    print(f"Top research fields:")
    if 'dominant_field' in topic_df.columns:
        top_fields = topic_df['dominant_field'].value_counts().head(5)
        for field, count in top_fields.items():
            print(f"  - {field}: {count} papers")
    
    print(f"\\nTop keywords:")
    for i, (keyword, freq) in enumerate(list(keyword_freq.items())[:10]):
        print(f"  {i+1}. {keyword}: {freq}")
    
    print(f"\\nResults saved to 'outputs/results/' directory")
    print("Analysis completed!")
    
    return topic_df


def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description='Conference Paper Analysis Tool')
    parser.add_argument('--scrape', action='store_true', 
                       help='Scrape papers from conferences')
    parser.add_argument('--analyze', action='store_true',
                       help='Analyze scraped papers')
    parser.add_argument('--conferences', nargs='+', 
                       choices=['ICML', 'NeuRIPS', 'ICLR', 'AAAI', 'IJCAI'],
                       help='Conferences to scrape')
    parser.add_argument('--years', nargs='+', type=int,
                       help='Years to scrape')
    parser.add_argument('--no-visualize', action='store_true',
                       help='Skip visualization generation')
    parser.add_argument('--no-save', action='store_true',
                       help='Skip saving results')
    
    args = parser.parse_args()
    
    # Create directories
    os.makedirs('outputs/data/raw', exist_ok=True)
    os.makedirs('outputs/data/processed', exist_ok=True)
    os.makedirs('outputs/results', exist_ok=True)
    os.makedirs('outputs/results/figures', exist_ok=True)
    os.makedirs('outputs/dashboard', exist_ok=True)
    
    # Run based on arguments
    if args.scrape:
        scrape_conferences(args.conferences, args.years)
    
    if args.analyze:
        analyze_papers(
            visualize=not args.no_visualize,
            save_results=not args.no_save
        )
    
    # If no specific action, run full pipeline
    if not args.scrape and not args.analyze:
        print("Running full analysis pipeline...")
        print("Step 1: Scraping conferences...")
        scrape_conferences(args.conferences, args.years)
        print("\\nStep 2: Analyzing papers...")
        analyze_papers(
            visualize=not args.no_visualize,
            save_results=not args.no_save
        )


if __name__ == "__main__":
    main()