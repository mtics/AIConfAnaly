"""
Visualization module for conference paper analysis
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from wordcloud import WordCloud
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Tuple
import os


class Visualizer:
    def __init__(self, results_dir: str = 'outputs/results/figures'):
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)
        
        # Set style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Figure settings
        self.figsize = (12, 8)
        self.dpi = 300
    
    def plot_papers_by_conference(self, df: pd.DataFrame, save: bool = True) -> None:
        """Plot number of papers by conference"""
        fig, ax = plt.subplots(figsize=self.figsize)
        
        conf_counts = df['conference'].value_counts()
        
        bars = ax.bar(conf_counts.index, conf_counts.values)
        ax.set_title('Number of Papers by Conference', fontsize=16, fontweight='bold')
        ax.set_xlabel('Conference', fontsize=12)
        ax.set_ylabel('Number of Papers', fontsize=12)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom')
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save:
            plt.savefig(f'{self.results_dir}/papers_by_conference.png', 
                       dpi=self.dpi, bbox_inches='tight')
        plt.show()
    
    def plot_papers_by_year(self, df: pd.DataFrame, save: bool = True) -> None:
        """Plot number of papers by year"""
        fig, ax = plt.subplots(figsize=self.figsize)
        
        year_counts = df['year'].value_counts().sort_index()
        
        ax.plot(year_counts.index, year_counts.values, marker='o', linewidth=2, markersize=8)
        ax.set_title('Number of Papers by Year', fontsize=16, fontweight='bold')
        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Number of Papers', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save:
            plt.savefig(f'{self.results_dir}/papers_by_year.png', 
                       dpi=self.dpi, bbox_inches='tight')
        plt.show()
    
    def plot_conference_year_heatmap(self, df: pd.DataFrame, save: bool = True) -> None:
        """Plot heatmap of papers by conference and year"""
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Create pivot table
        pivot_table = df.groupby(['conference', 'year']).size().unstack(fill_value=0)
        
        # Create heatmap
        sns.heatmap(pivot_table, annot=True, fmt='d', cmap='YlOrRd', 
                   cbar_kws={'label': 'Number of Papers'}, ax=ax)
        
        ax.set_title('Papers by Conference and Year', fontsize=16, fontweight='bold')
        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Conference', fontsize=12)
        
        plt.tight_layout()
        
        if save:
            plt.savefig(f'{self.results_dir}/conference_year_heatmap.png', 
                       dpi=self.dpi, bbox_inches='tight')
        plt.show()
    
    def plot_field_distribution(self, df: pd.DataFrame, save: bool = True) -> None:
        """Plot distribution of research fields"""
        if 'dominant_field' not in df.columns:
            print("No field information available")
            return
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        field_counts = df['dominant_field'].value_counts()
        
        # Create horizontal bar plot for better readability
        bars = ax.barh(range(len(field_counts)), field_counts.values)
        ax.set_yticks(range(len(field_counts)))
        ax.set_yticklabels(field_counts.index)
        ax.set_xlabel('Number of Papers', fontsize=12)
        ax.set_title('Distribution of Research Fields', fontsize=16, fontweight='bold')
        
        # Add value labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2, 
                   f'{int(width)}', ha='left', va='center')
        
        plt.tight_layout()
        
        if save:
            plt.savefig(f'{self.results_dir}/field_distribution.png', 
                       dpi=self.dpi, bbox_inches='tight')
        plt.show()
    
    def plot_field_trends(self, df: pd.DataFrame, top_n: int = 8, save: bool = True) -> None:
        """Plot trends of top research fields over time"""
        if 'dominant_field' not in df.columns:
            print("No field information available")
            return
        
        # Get top N fields
        top_fields = df['dominant_field'].value_counts().head(top_n).index
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        for field in top_fields:
            field_data = df[df['dominant_field'] == field]
            yearly_counts = field_data['year'].value_counts().sort_index()
            ax.plot(yearly_counts.index, yearly_counts.values, 
                   marker='o', label=field, linewidth=2)
        
        ax.set_title(f'Trends of Top {top_n} Research Fields Over Time', 
                    fontsize=16, fontweight='bold')
        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Number of Papers', fontsize=12)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save:
            plt.savefig(f'{self.results_dir}/field_trends.png', 
                       dpi=self.dpi, bbox_inches='tight')
        plt.show()
    
    def plot_field_by_conference(self, df: pd.DataFrame, save: bool = True) -> None:
        """Plot stacked bar chart of fields by conference"""
        if 'dominant_field' not in df.columns:
            print("No field information available")
            return
        
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Create pivot table
        pivot_table = df.groupby(['conference', 'dominant_field']).size().unstack(fill_value=0)
        
        # Create stacked bar chart
        pivot_table.plot(kind='bar', stacked=True, ax=ax, 
                        colormap='tab20', figsize=(14, 10))
        
        ax.set_title('Research Fields by Conference', fontsize=16, fontweight='bold')
        ax.set_xlabel('Conference', fontsize=12)
        ax.set_ylabel('Number of Papers', fontsize=12)
        ax.legend(title='Research Field', bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save:
            plt.savefig(f'{self.results_dir}/field_by_conference.png', 
                       dpi=self.dpi, bbox_inches='tight')
        plt.show()
    
    def create_keyword_wordcloud(self, keyword_freq: Dict[str, int], 
                                title: str = "Top Keywords", save: bool = True) -> None:
        """Create word cloud from keyword frequencies"""
        if not keyword_freq:
            print("No keyword data available")
            return
        
        # Create word cloud
        wordcloud = WordCloud(
            width=1200, height=600,
            background_color='white',
            max_words=100,
            colormap='viridis'
        ).generate_from_frequencies(keyword_freq)
        
        fig, ax = plt.subplots(figsize=(15, 7.5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        if save:
            filename = title.lower().replace(' ', '_').replace('/', '_')
            plt.savefig(f'{self.results_dir}/{filename}_wordcloud.png', 
                       dpi=self.dpi, bbox_inches='tight')
        plt.show()
    
    def plot_top_keywords(self, keyword_freq: Dict[str, int], 
                         top_n: int = 20, save: bool = True) -> None:
        """Plot top N keywords as horizontal bar chart"""
        if not keyword_freq:
            print("No keyword data available")
            return
        
        # Get top N keywords
        top_keywords = dict(list(keyword_freq.items())[:top_n])
        
        fig, ax = plt.subplots(figsize=(12, 10))
        
        keywords = list(top_keywords.keys())
        counts = list(top_keywords.values())
        
        bars = ax.barh(range(len(keywords)), counts)
        ax.set_yticks(range(len(keywords)))
        ax.set_yticklabels(keywords)
        ax.set_xlabel('Frequency', fontsize=12)
        ax.set_title(f'Top {top_n} Keywords', fontsize=16, fontweight='bold')
        
        # Add value labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2, 
                   f'{int(width)}', ha='left', va='center')
        
        plt.tight_layout()
        
        if save:
            plt.savefig(f'{self.results_dir}/top_{top_n}_keywords.png', 
                       dpi=self.dpi, bbox_inches='tight')
        plt.show()
    
    def plot_abstract_length_distribution(self, df: pd.DataFrame, save: bool = True) -> None:
        """Plot distribution of abstract lengths"""
        if 'abstract_length' not in df.columns:
            print("No abstract length information available")
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Histogram
        ax1.hist(df['abstract_length'], bins=50, alpha=0.7, edgecolor='black')
        ax1.set_xlabel('Abstract Length (characters)', fontsize=12)
        ax1.set_ylabel('Frequency', fontsize=12)
        ax1.set_title('Distribution of Abstract Lengths', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Box plot by conference
        if 'conference' in df.columns:
            df.boxplot(column='abstract_length', by='conference', ax=ax2)
            ax2.set_xlabel('Conference', fontsize=12)
            ax2.set_ylabel('Abstract Length (characters)', fontsize=12)
            ax2.set_title('Abstract Length by Conference', fontsize=14, fontweight='bold')
            plt.setp(ax2.get_xticklabels(), rotation=45)
        
        plt.tight_layout()
        
        if save:
            plt.savefig(f'{self.results_dir}/abstract_length_distribution.png', 
                       dpi=self.dpi, bbox_inches='tight')
        plt.show()
    
    def create_interactive_dashboard(self, df: pd.DataFrame, keyword_freq: Dict[str, int]) -> None:
        """Create interactive Plotly dashboard"""
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Papers by Conference', 'Papers by Year', 
                          'Field Distribution', 'Top Keywords'),
            specs=[[{"type": "bar"}, {"type": "scatter"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Papers by conference
        conf_counts = df['conference'].value_counts()
        fig.add_trace(
            go.Bar(x=conf_counts.index, y=conf_counts.values, name="Conference"),
            row=1, col=1
        )
        
        # Papers by year
        year_counts = df['year'].value_counts().sort_index()
        fig.add_trace(
            go.Scatter(x=year_counts.index, y=year_counts.values, 
                      mode='lines+markers', name="Year"),
            row=1, col=2
        )
        
        # Field distribution (if available)
        if 'dominant_field' in df.columns:
            field_counts = df['dominant_field'].value_counts().head(10)
            fig.add_trace(
                go.Bar(x=field_counts.values, y=field_counts.index, 
                      orientation='h', name="Field"),
                row=2, col=1
            )
        
        # Top keywords
        if keyword_freq:
            top_keywords = dict(list(keyword_freq.items())[:15])
            fig.add_trace(
                go.Bar(x=list(top_keywords.values()), y=list(top_keywords.keys()),
                      orientation='h', name="Keywords"),
                row=2, col=2
            )
        
        fig.update_layout(
            height=800,
            title_text="Conference Paper Analysis Dashboard",
            showlegend=False
        )
        
        # Save as HTML
        fig.write_html(f'{self.results_dir}/interactive_dashboard.html')
        fig.show()
    
    def plot_field_momentum(self, momentum_data: Dict, save: bool = True) -> None:
        """Plot field momentum analysis"""
        if not momentum_data:
            print("No momentum data available")
            return
        
        fields = list(momentum_data.keys())[:15]  # Top 15 fields
        momentum_scores = [momentum_data[field]['momentum_score'] for field in fields]
        recent_papers = [momentum_data[field]['recent_papers'] for field in fields]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
        
        # Momentum scores
        colors = ['red' if momentum_data[field]['status'] == 'hot' else 
                 'orange' if momentum_data[field]['status'] == 'stable' else 'blue' 
                 for field in fields]
        
        bars1 = ax1.barh(range(len(fields)), momentum_scores, color=colors, alpha=0.7)
        ax1.set_yticks(range(len(fields)))
        ax1.set_yticklabels(fields)
        ax1.set_xlabel('Momentum Score', fontsize=12)
        ax1.set_title('Research Field Momentum (Red=Hot, Orange=Stable, Blue=Declining)', 
                     fontsize=14, fontweight='bold')
        ax1.axvline(x=1.0, color='black', linestyle='--', alpha=0.5, label='Baseline')
        
        # Add value labels
        for i, bar in enumerate(bars1):
            width = bar.get_width()
            ax1.text(width + 0.05, bar.get_y() + bar.get_height()/2, 
                    f'{width:.2f}', ha='left', va='center', fontsize=9)
        
        # Recent papers count
        bars2 = ax2.barh(range(len(fields)), recent_papers, color='green', alpha=0.7)
        ax2.set_yticks(range(len(fields)))
        ax2.set_yticklabels(fields)
        ax2.set_xlabel('Recent Papers Count', fontsize=12)
        ax2.set_title('Recent Publication Volume (Last 3 Years)', fontsize=14, fontweight='bold')
        
        # Add value labels
        for i, bar in enumerate(bars2):
            width = bar.get_width()
            ax2.text(width + 1, bar.get_y() + bar.get_height()/2, 
                    f'{int(width)}', ha='left', va='center', fontsize=9)
        
        plt.tight_layout()
        
        if save:
            plt.savefig(f'{self.results_dir}/field_momentum_analysis.png', 
                       dpi=self.dpi, bbox_inches='tight')
        plt.show()
    
    def plot_emerging_fields(self, emerging_data: Dict, save: bool = True) -> None:
        """Plot emerging research fields"""
        if not emerging_data:
            print("No emerging fields data available")
            return
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        fields = list(emerging_data.keys())
        growth_rates = [emerging_data[field]['average_growth_rate'] for field in fields]
        total_papers = [emerging_data[field]['total_papers'] for field in fields]
        
        # Create bubble chart
        scatter = ax.scatter(growth_rates, range(len(fields)), 
                           s=[p*2 for p in total_papers], 
                           alpha=0.6, c=growth_rates, cmap='Reds')
        
        ax.set_yticks(range(len(fields)))
        ax.set_yticklabels(fields)
        ax.set_xlabel('Average Growth Rate', fontsize=12)
        ax.set_title('Emerging Research Fields (Bubble size = Total papers)', 
                    fontsize=16, fontweight='bold')
        
        # Add colorbar
        cbar = plt.colorbar(scatter)
        cbar.set_label('Growth Rate', fontsize=12)
        
        # Add grid
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save:
            plt.savefig(f'{self.results_dir}/emerging_fields.png', 
                       dpi=self.dpi, bbox_inches='tight')
        plt.show()
    
    def plot_conference_specialization(self, specialization_data: Dict, save: bool = True) -> None:
        """Plot conference specialization heatmap"""
        if not specialization_data:
            print("No specialization data available")
            return
        
        # Prepare data for heatmap
        conferences = list(specialization_data.keys())
        all_fields = set()
        for conf_data in specialization_data.values():
            all_fields.update(conf_data['field_distribution'].keys())
        
        all_fields = sorted(list(all_fields))
        
        # Create matrix
        matrix = []
        for conference in conferences:
            row = []
            for field in all_fields:
                percentage = specialization_data[conference]['field_distribution'].get(field, 0)
                row.append(percentage * 100)  # Convert to percentage
            matrix.append(row)
        
        fig, ax = plt.subplots(figsize=(16, 8))
        
        # Create heatmap
        im = ax.imshow(matrix, cmap='YlOrRd', aspect='auto')
        
        # Set ticks and labels
        ax.set_xticks(range(len(all_fields)))
        ax.set_yticks(range(len(conferences)))
        ax.set_xticklabels(all_fields, rotation=45, ha='right')
        ax.set_yticklabels(conferences)
        
        # Add colorbar
        cbar = plt.colorbar(im)
        cbar.set_label('Percentage of Papers (%)', fontsize=12)
        
        # Add text annotations for values > 5%
        for i in range(len(conferences)):
            for j in range(len(all_fields)):
                if matrix[i][j] > 5:
                    text = ax.text(j, i, f'{matrix[i][j]:.1f}%',
                                 ha="center", va="center", color="black", fontsize=8)
        
        ax.set_title('Conference Specialization in Research Fields', 
                    fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        
        if save:
            plt.savefig(f'{self.results_dir}/conference_specialization.png', 
                       dpi=self.dpi, bbox_inches='tight')
        plt.show()
    
    def create_comprehensive_dashboard(self, df: pd.DataFrame, field_extractor, save: bool = True) -> None:
        """Create comprehensive interactive dashboard with all analyses"""
        
        # Calculate all analysis data
        growth_rates = field_extractor.calculate_field_growth_rates(df)
        emerging_fields = field_extractor.identify_emerging_fields(df)
        momentum_data = field_extractor.calculate_field_momentum(df)
        specialization = field_extractor.analyze_conference_specialization(df)
        
        # Create main dashboard with multiple tabs/sections
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Publication Trends by Conference', 'Field Distribution Over Time',
                'Emerging Fields (Growth Rate)', 'Field Momentum Analysis',
                'Conference Specialization', 'Research Field Evolution'
            ),
            specs=[
                [{"type": "scatter"}, {"type": "scatter"}],
                [{"type": "bar"}, {"type": "bar"}],
                [{"type": "heatmap"}, {"type": "scatter"}]
            ]
        )
        
        # 1. Publication trends by conference
        for conference in df['conference'].unique():
            conf_data = df[df['conference'] == conference]
            yearly_counts = conf_data.groupby('year').size()
            fig.add_trace(
                go.Scatter(x=yearly_counts.index, y=yearly_counts.values,
                         mode='lines+markers', name=conference),
                row=1, col=1
            )
        
        # 2. Field distribution over time (top 5 fields)
        if 'dominant_field' in df.columns:
            top_fields = df['dominant_field'].value_counts().head(5).index
            for field in top_fields:
                field_data = df[df['dominant_field'] == field]
                yearly_counts = field_data.groupby('year').size()
                fig.add_trace(
                    go.Scatter(x=yearly_counts.index, y=yearly_counts.values,
                             mode='lines+markers', name=field),
                    row=1, col=2
                )
        
        # 3. Emerging fields
        if emerging_fields:
            fields = list(emerging_fields.keys())[:10]
            growth_rates_list = [emerging_fields[field]['average_growth_rate'] for field in fields]
            fig.add_trace(
                go.Bar(x=growth_rates_list, y=fields, orientation='h',
                      name="Growth Rate"),
                row=2, col=1
            )
        
        # 4. Field momentum
        if momentum_data:
            fields = list(momentum_data.keys())[:10]
            momentum_scores = [momentum_data[field]['momentum_score'] for field in fields]
            colors = ['red' if momentum_data[field]['status'] == 'hot' else 
                     'orange' if momentum_data[field]['status'] == 'stable' else 'blue' 
                     for field in fields]
            
            fig.add_trace(
                go.Bar(x=momentum_scores, y=fields, orientation='h',
                      marker=dict(color=colors), name="Momentum"),
                row=2, col=2
            )
        
        # Update layout
        fig.update_layout(
            height=1200,
            title_text="Comprehensive AI Conference Analysis Dashboard",
            showlegend=True
        )
        
        if save:
            fig.write_html(f'{self.results_dir}/comprehensive_dashboard.html')
        
        fig.show()
    
    def save_summary_statistics(self, stats: Dict, filename: str = 'summary_stats.txt') -> None:
        """Save summary statistics to text file"""
        filepath = os.path.join(self.results_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("Conference Paper Analysis - Summary Statistics\\n")
            f.write("=" * 50 + "\\n\\n")
            
            for key, value in stats.items():
                f.write(f"{key.replace('_', ' ').title()}:\\n")
                if isinstance(value, dict):
                    for k, v in value.items():
                        f.write(f"  {k}: {v}\\n")
                else:
                    f.write(f"  {value}\\n")
                f.write("\\n")
        
        print(f"Summary statistics saved to {filepath}")