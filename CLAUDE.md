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
# Full analysis pipeline (recommended)
python main_new.py

# Or using module approach
python -m conf_analysis.main

# Generate comprehensive dashboard
python -c "from conf_analysis.main import main; main()"
```

### Cleanup and Maintenance
```bash
# Clean up redundant files (run once after reorganization)
python tools/utilities/cleanup_project.py
```

## Architecture Overview

### Final Optimized Structure

```
ConfAnalysis/
├── conf_analysis/          # 🏗️ Core analysis system
│   ├── core/              # Core components  
│   │   ├── analyzer.py    # Enhanced analyzer (70+ scenarios, 25+ tech trends)
│   │   ├── scrapers/      # Conference-specific scrapers
│   │   ├── models/        # Data models
│   │   ├── services/      # Business services
│   │   ├── utils/         # Utility functions
│   │   ├── database/      # Database modules
│   │   └── embeddings/    # Vector encoding
│   ├── docs/             # Project documentation
│   └── main.py           # Main analysis program
├── tools/                 # 🔧 Utility tools (organized)
│   ├── utilities/         # Helper utilities
│   ├── data_generators/   # Data generation scripts
│   └── visualization_generators/  # Chart generators
├── frontend/             # 🎨 Web interface (cleaned & optimized)
│   ├── unified_analysis_dashboard.html  # ⭐ Main dashboard
│   └── unified_analysis_report.html     # ⭐ Generated report
├── outputs/              # 📊 Analysis results
├── tests/               # 🧪 Test files
├── main_new.py          # 🚪 Main entry point
└── PROJECT_STRUCTURE.md # 📁 Structure documentation
```

### Core Components

**Core Analysis (`conf_analysis/core/`)**
- `analyzer.py`: UnifiedAnalyzer with enhanced field classification
- `scrapers/`: Conference-specific scraping implementations
- `models/`: Data models for papers and analysis results
- `utils/`: Configuration, text processing, and database utilities

**Tools (`tools/`)**
- `utilities/`: Legacy analyzer scripts and cleanup tools
- `visualization_generators/`: Chart and dashboard generators
- `data_generators/`: Data processing and analysis scripts

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