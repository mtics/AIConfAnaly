"""
AI Conference Trend Analysis Script
Generates comprehensive analysis reports on AI/ML conference paper trends
"""

import pandas as pd
import json
import os
from datetime import datetime
from analysis.data_processor import DataProcessor
from analysis.field_extractor import FieldExtractor
from analysis.visualizer import Visualizer
from utils.config import *


class TrendAnalyzer:
    def __init__(self):
        self.data_processor = DataProcessor()
        self.field_extractor = FieldExtractor()
        self.visualizer = Visualizer()
        
    def load_and_process_data(self):
        """Load and process all conference data"""
        print("Loading raw data...")
        df = self.data_processor.load_raw_data()
        
        print("Processing paper data...")
        processed_df = self.data_processor.process_papers(df)
        
        print("Extracting research fields...")
        field_df = self.field_extractor.extract_fields_by_keywords(processed_df)
        final_df = self.field_extractor.get_dominant_field(field_df)
        
        return final_df
    
    def generate_comprehensive_analysis(self, df):
        """Generate comprehensive analysis of AI conference trends"""
        
        print("Calculating field statistics...")
        field_stats = self.field_extractor.get_field_statistics(df)
        
        print("Analyzing field growth rates...")
        growth_rates = self.field_extractor.calculate_field_growth_rates(df)
        
        print("Identifying emerging fields...")
        emerging_fields = self.field_extractor.identify_emerging_fields(df)
        
        print("Calculating field momentum...")
        momentum_data = self.field_extractor.calculate_field_momentum(df)
        
        print("Analyzing conference specialization...")
        specialization = self.field_extractor.analyze_conference_specialization(df)
        
        print("Extracting keyword frequencies...")
        keyword_freq = self.data_processor.get_keyword_frequencies(df)
        
        print("Getting conference statistics...")
        conf_stats = self.data_processor.get_conference_statistics(df)
        
        return {
            'field_stats': field_stats,
            'growth_rates': growth_rates,
            'emerging_fields': emerging_fields,
            'momentum_data': momentum_data,
            'specialization': specialization,
            'keyword_freq': keyword_freq,
            'conf_stats': conf_stats,
            'total_papers': len(df),
            'year_range': f"{df['year'].min()}-{df['year'].max()}",
            'conferences': list(df['conference'].unique())
        }
    
    def create_visualizations(self, df, analysis_results):
        """Create all visualizations"""
        print("Creating visualizations...")
        
        # Basic visualizations
        self.visualizer.plot_papers_by_conference(df)
        self.visualizer.plot_papers_by_year(df)
        self.visualizer.plot_conference_year_heatmap(df)
        
        # Field analysis visualizations
        if 'dominant_field' in df.columns:
            self.visualizer.plot_field_distribution(df)
            self.visualizer.plot_field_trends(df)
            self.visualizer.plot_field_by_conference(df)
        
        # Advanced analysis visualizations
        if analysis_results['momentum_data']:
            self.visualizer.plot_field_momentum(analysis_results['momentum_data'])
        
        if analysis_results['emerging_fields']:
            self.visualizer.plot_emerging_fields(analysis_results['emerging_fields'])
        
        if analysis_results['specialization']:
            self.visualizer.plot_conference_specialization(analysis_results['specialization'])
        
        # Keyword analysis
        if analysis_results['keyword_freq']:
            self.visualizer.plot_top_keywords(analysis_results['keyword_freq'])
            self.visualizer.create_keyword_wordcloud(analysis_results['keyword_freq'])
        
        # Text statistics
        if 'abstract_length' in df.columns:
            self.visualizer.plot_abstract_length_distribution(df)
        
        # Comprehensive dashboard
        self.visualizer.create_comprehensive_dashboard(df, self.field_extractor)
        
        print("All visualizations created successfully!")
    
    def generate_report(self, analysis_results):
        """Generate comprehensive text report"""
        
        report = []
        report.append("=" * 80)
        report.append("AI CONFERENCE TREND ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Analysis Period: {analysis_results['year_range']}")
        report.append(f"Total Papers Analyzed: {analysis_results['total_papers']:,}")
        report.append(f"Conferences: {', '.join(analysis_results['conferences'])}")
        report.append("")
        
        # Executive Summary
        report.append("EXECUTIVE SUMMARY")
        report.append("-" * 40)
        
        # Top emerging fields
        if analysis_results['emerging_fields']:
            top_emerging = list(analysis_results['emerging_fields'].keys())[:3]
            report.append(f"Top Emerging Fields: {', '.join(top_emerging)}")
        
        # Hot fields by momentum
        if analysis_results['momentum_data']:
            hot_fields = [field for field, data in analysis_results['momentum_data'].items() 
                         if data['status'] == 'hot'][:3]
            report.append(f"Hottest Fields (Recent Momentum): {', '.join(hot_fields)}")
        
        # Conference with most papers
        conf_stats = analysis_results['conf_stats']['papers_by_conference']
        top_conf = max(conf_stats.items(), key=lambda x: x[1])
        report.append(f"Most Prolific Conference: {top_conf[0]} ({top_conf[1]:,} papers)")
        
        report.append("")
        
        # Detailed Field Analysis
        report.append("DETAILED FIELD ANALYSIS")
        report.append("-" * 40)
        
        if analysis_results['field_stats'].get('field_distribution'):
            report.append("Field Distribution:")
            for field, count in list(analysis_results['field_stats']['field_distribution'].items())[:10]:
                percentage = (count / analysis_results['total_papers']) * 100
                report.append(f"  {field}: {count:,} papers ({percentage:.1f}%)")
        
        report.append("")
        
        # Emerging Fields Analysis
        if analysis_results['emerging_fields']:
            report.append("EMERGING FIELDS ANALYSIS")
            report.append("-" * 40)
            report.append("Fields showing significant growth (>30% average growth rate):")
            
            for field, data in list(analysis_results['emerging_fields'].items())[:10]:
                growth_rate = data['average_growth_rate'] * 100
                total_papers = data['total_papers']
                report.append(f"  {field}:")
                report.append(f"    Growth Rate: {growth_rate:.1f}%")
                report.append(f"    Total Papers: {total_papers}")
                report.append(f"    Trend: {data['recent_trend']}")
                report.append("")
        
        # Field Momentum Analysis
        if analysis_results['momentum_data']:
            report.append("FIELD MOMENTUM ANALYSIS")
            report.append("-" * 40)
            
            hot_fields = [(field, data) for field, data in analysis_results['momentum_data'].items() 
                         if data['status'] == 'hot']
            declining_fields = [(field, data) for field, data in analysis_results['momentum_data'].items() 
                               if data['status'] == 'declining']
            
            if hot_fields:
                report.append("Hot Fields (High Recent Activity):")
                for field, data in hot_fields[:5]:
                    report.append(f"  {field}: Momentum Score {data['momentum_score']:.2f}")
            
            if declining_fields:
                report.append("\nDeclining Fields:")
                for field, data in declining_fields[:5]:
                    report.append(f"  {field}: Momentum Score {data['momentum_score']:.2f}")
        
        report.append("")
        
        # Conference Specialization
        if analysis_results['specialization']:
            report.append("CONFERENCE SPECIALIZATION ANALYSIS")
            report.append("-" * 40)
            
            for conf, data in analysis_results['specialization'].items():
                report.append(f"{conf}:")
                report.append(f"  Total Papers: {data['total_papers']:,}")
                report.append(f"  Diversity Score: {data['diversity_score']}")
                
                if data['top_specializations']:
                    report.append("  Top Specializations:")
                    for field, pct in data['top_specializations'].items():
                        report.append(f"    {field}: {pct*100:.1f}%")
                report.append("")
        
        # Top Keywords
        if analysis_results['keyword_freq']:
            report.append("TOP RESEARCH KEYWORDS")
            report.append("-" * 40)
            top_keywords = list(analysis_results['keyword_freq'].items())[:20]
            for i, (keyword, freq) in enumerate(top_keywords, 1):
                report.append(f"{i:2d}. {keyword}: {freq}")
        
        report.append("")
        report.append("=" * 80)
        report.append("END OF REPORT")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_results(self, analysis_results, report):
        """Save analysis results and report"""
        
        # Ensure results directory exists
        os.makedirs(RESULTS_DIR, exist_ok=True)
        
        # Save detailed analysis results as JSON
        results_file = os.path.join(RESULTS_DIR, 'trend_analysis_results.json')
        
        # Convert numpy types to Python types for JSON serialization
        json_results = {}
        for key, value in analysis_results.items():
            if key in ['growth_rates', 'emerging_fields', 'momentum_data']:
                json_results[key] = self._convert_for_json(value)
            else:
                json_results[key] = value
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(json_results, f, indent=2, ensure_ascii=False, default=str)
        
        # Save text report
        report_file = os.path.join(RESULTS_DIR, 'ai_conference_trend_report.txt')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"Analysis results saved to: {results_file}")
        print(f"Report saved to: {report_file}")
    
    def _convert_for_json(self, obj):
        """Convert numpy types and complex objects for JSON serialization"""
        if isinstance(obj, dict):
            return {key: self._convert_for_json(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_for_json(item) for item in obj]
        elif hasattr(obj, 'item'):  # numpy scalar
            return obj.item()
        elif hasattr(obj, 'tolist'):  # numpy array
            return obj.tolist()
        else:
            return obj
    
    def run_full_analysis(self):
        """Run complete trend analysis pipeline"""
        print("Starting AI Conference Trend Analysis...")
        print("=" * 50)
        
        # Load and process data
        df = self.load_and_process_data()
        print(f"Loaded {len(df)} papers from {len(df['conference'].unique())} conferences")
        
        # Generate analysis
        analysis_results = self.generate_comprehensive_analysis(df)
        
        # Create visualizations
        self.create_visualizations(df, analysis_results)
        
        # Generate report
        report = self.generate_report(analysis_results)
        
        # Save results
        self.save_results(analysis_results, report)
        
        print("\n" + "=" * 50)
        print("Analysis completed successfully!")
        print(f"Check the '{RESULTS_DIR}' directory for all outputs.")
        
        return df, analysis_results, report


def main():
    """Main function to run the trend analysis"""
    analyzer = TrendAnalyzer()
    df, results, report = analyzer.run_full_analysis()
    
    # Print summary
    print("\nANALYSIS SUMMARY:")
    print("-" * 30)
    print(f"Total papers analyzed: {len(df):,}")
    print(f"Research fields identified: {len(results['field_stats']['field_distribution'])}")
    print(f"Emerging fields: {len(results['emerging_fields'])}")
    
    if results['momentum_data']:
        hot_fields = sum(1 for data in results['momentum_data'].values() if data['status'] == 'hot')
        print(f"Hot fields: {hot_fields}")


if __name__ == "__main__":
    main()