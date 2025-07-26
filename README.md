# 🚀 AI Conference Paper Analysis System

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive system for scraping, downloading, analyzing, and visualizing AI/ML conference papers from major venues including ICML, NeuRIPS, ICLR, AAAI, and IJCAI.

## 🎯 Features

- **📊 Paper Scraping**: Automated scraping from 5 major AI conferences
- **📄 PDF Download**: Intelligent PDF downloading with retry mechanisms  
- **🔍 Text Extraction**: Extract and process text content from PDFs
- **🧠 Vectorization**: Create embeddings for semantic search
- **📈 Analysis**: Comprehensive trend and field analysis
- **🎨 Visualization**: Interactive dashboards and charts
- **🔎 Search**: Vector-based semantic paper search

## 🚀 Quick Start

### Installation
```bash
# Install dependencies
python utils/system_setup.py
# OR
pip install -r requirements.txt
```

### Basic Usage
```bash
# Scrape papers from all conferences
python main.py --scrape

# Scrape specific conferences
python main.py --scrape --conferences ICML NeuRIPS

# Run analysis  
python main.py --analyze

# Complete workflow
python main.py --scrape --analyze
```

### PDF Management
```bash
# Check download status
python utils/pdf_manager.py status

# Download missing PDFs
python utils/pdf_manager.py missing

# Download all PDFs
python utils/pdf_manager.py download
```

### Generate Visualizations
```bash
# Create interactive dashboard
python visualization/generate_dashboard.py

# Run trend analysis
python visualization/trend_analysis.py

# Process and vectorize text
python utils/text_processor.py pipeline
```

## 🏗️ Project Structure

```
ConfAnalysis/
├── 📁 Core
│   ├── main.py                     # Main entry point
│   ├── config.py                   # Configuration settings
│   └── requirements.txt            # Dependencies
│
├── 🕷️ scrapers/                   # Conference paper scrapers
│   ├── base_scraper.py            # Base scraper class
│   ├── icml_scraper.py            # ICML scraper
│   ├── neurips_scraper.py         # NeuRIPS scraper  
│   ├── iclr_scraper.py            # ICLR scraper
│   ├── aaai_scraper.py            # AAAI scraper
│   └── ijcai_scraper.py           # IJCAI scraper
│
├── 📊 analysis/                   # Data analysis modules
│   ├── data_processor.py          # Data processing
│   ├── field_extractor.py         # Research field classification
│   └── visualizer.py              # Visualization generation
│
├── 🔧 utils/                      # Core utilities and tools
│   ├── config.py                  # Configuration settings
│   ├── pdf_manager.py             # PDF download and management
│   ├── text_processor.py          # Text extraction and vectorization
│   ├── vector_database.py         # Vector database operations
│   └── system_setup.py            # System and dependency setup
│
├── 🎨 visualization/              # Visualization tools
│   ├── generate_dashboard.py      # Interactive dashboard
│   └── trend_analysis.py          # Trend analysis
│
├── 🔍 search/                     # Search functionality
│   └── paper_search_interface.py  # Search interface
│
└── 📁 outputs/                    # All generated outputs
    ├── 📊 data/                   # Data storage
    │   ├── raw/                   # Raw scraped data
    │   ├── processed/             # Processed datasets
    │   ├── pdfs/                  # Downloaded PDFs
    │   └── extracted_text/        # Extracted text content
    ├── 📈 results/                # Analysis results
    │   └── figures/               # Charts and visualizations
    └── 🎨 dashboard/              # Interactive dashboards
```

## Supported Conferences

- **ICML**: International Conference on Machine Learning
- **NeuRIPS**: Conference on Neural Information Processing Systems  
- **ICLR**: International Conference on Learning Representations
- **AAAI**: AAAI Conference on Artificial Intelligence
- **IJCAI**: International Joint Conference on Artificial Intelligence

## Research Fields Detected

The system automatically classifies papers into these research areas:

- Computer Vision
- Natural Language Processing
- Reinforcement Learning
- Deep Learning
- Machine Learning Theory
- Optimization
- Probabilistic Models
- Graph Neural Networks
- Federated Learning
- Meta Learning
- Generative Models
- Adversarial Learning

## Output Files

### Data Files
- `outputs/data/raw/*.json`: Raw scraped paper data
- `outputs/data/processed/all_papers_processed.csv`: Processed paper data with features

### Analysis Results
- `outputs/results/basic_statistics.json`: Conference and temporal statistics
- `outputs/results/field_statistics.json`: Research field analysis
- `outputs/results/keyword_frequencies.json`: Most common keywords
- `outputs/results/topics_info.json`: Topic modeling results

### Visualizations
- `outputs/results/figures/`: Conference distribution charts, temporal trends, field heatmaps
- `outputs/dashboard/ai_conference_dashboard.html`: Main interactive dashboard
- Static visualization files (PNG charts and word clouds)

## Customization

### Adding New Conferences
1. Create a new scraper class inheriting from `BaseScraper`
2. Implement the `get_papers_for_year()` method
3. Add conference info to `config.py`
4. Import in `scrapers/__init__.py`

### Adding Research Fields
Edit the `field_keywords` dictionary in `analysis/field_extractor.py`:

```python
self.field_keywords['New Field'] = {
    'keyword1', 'keyword2', 'phrase example'
}
```

### Modifying Visualizations
The `Visualizer` class provides methods for different chart types. You can:
- Customize colors and styles
- Add new plot types
- Modify interactive dashboard components

## Notes

- **Rate Limiting**: Scrapers include delays to be respectful to servers
- **Error Handling**: Robust error handling for network issues
- **Data Validation**: Automatic cleaning and validation of scraped data
- **Extensible**: Easy to add new conferences or analysis methods

## Troubleshooting

1. **Import Errors**: Ensure all dependencies are installed
2. **Scraping Failures**: Check internet connection and conference website availability
3. **Empty Results**: Some conferences may have changed their website structure
4. **Memory Issues**: For large datasets, consider processing conferences separately

## Contributing

Feel free to:
- Add support for new conferences
- Improve field classification
- Add new visualization types
- Enhance NLP processing

## Legal

This tool is for academic research purposes. Respect the terms of service of conference websites and implement appropriate rate limiting.