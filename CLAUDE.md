# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a conference paper analysis tool that scrapes and analyzes research papers from major AI/ML conferences (ICML, NeuRIPS, ICLR, AAAI, IJCAI). It performs automated scraping, NLP-based analysis, field classification, and generates comprehensive interactive visualizations.

## Development Commands

### Setup and Dependencies
```bash
# Install dependencies via pip
pip install -r requirements.txt

# Or via conda
conda env create -f environment.yml
conda activate ConfAnalysis
```

### Main Commands
```bash
# Full pipeline (scrape + analyze)
python main.py

# Scraping only
python main.py --scrape
python main.py --scrape --conferences ICML NeuRIPS
python main.py --scrape --years 2020 2021 2022

# Analysis only
python main.py --analyze
python main.py --analyze --no-visualize
python main.py --analyze --no-save

# Generate interactive dashboard
python generate_dashboard.py
```

## Architecture Overview

### Core Components

**Scrapers (`scrapers/`)**
- `base_scraper.py`: Abstract base class with common scraping functionality
- Conference-specific scrapers inherit from BaseScraper and implement `get_papers_for_year()`
- Each scraper handles different website structures and parsing patterns
- Built-in rate limiting and error handling

**Analysis Pipeline (`analysis/`)**
- `data_processor.py`: NLP processing, text cleaning, keyword extraction
- `field_extractor.py`: Research field classification using predefined keywords and ML techniques
- `visualizer.py`: Chart generation, word clouds, interactive dashboards

**Configuration (`config.py`)**
- Conference URLs, years, and scraping parameters
- Data paths and analysis settings
- Visualization configurations

### Data Flow
1. **Scraping**: Conference-specific scrapers extract paper metadata → JSON files in `data/raw/`
2. **Processing**: DataProcessor cleans text, extracts keywords → CSV in `data/processed/`
3. **Field Classification**: FieldExtractor categorizes papers by research area
4. **Analysis**: Statistical analysis and trend identification
5. **Visualization**: Charts, word clouds, interactive dashboard → `results/figures/`

### Key Design Patterns
- **Strategy Pattern**: Different scraper implementations for each conference
- **Template Method**: BaseScraper defines common workflow, subclasses implement specifics
- **Pipeline Architecture**: Sequential data processing stages with intermediate outputs
- **Configuration-driven**: Centralized settings in config.py for easy customization

## Research Field Classification

The system automatically classifies papers into research areas using keyword matching and ML techniques. Fields include Computer Vision, NLP, Reinforcement Learning, Deep Learning Theory, Optimization, etc. Keywords are defined in `analysis/field_extractor.py`.

## Adding New Conferences

1. Create new scraper class inheriting from `BaseScraper`
2. Implement `get_papers_for_year(year)` method
3. Add conference configuration to `CONFERENCES` dict in `config.py`
4. Import in `scrapers/__init__.py`

## Data Storage Structure

- `data/raw/`: JSON files with scraped paper data (one per conference/year)
- `data/processed/`: Processed CSV files with extracted features  
- `results/`: Analysis outputs and interactive dashboard
  - `ai_conference_dashboard.html`: Main interactive dashboard
  - `figures/`: Static visualization files

## Output Files

The main output is an interactive HTML dashboard located at:
- `results/ai_conference_dashboard.html`

This dashboard provides comprehensive analysis including:
- Publication trends across conferences and years
- Detailed research field classification (130+ categories)
- Interactive visualizations with hover details
- Conference comparison and field evolution analysis