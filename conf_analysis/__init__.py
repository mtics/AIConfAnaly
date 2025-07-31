"""
AI Conference Paper Analysis System
==================================

A comprehensive system for analyzing research papers from major AI/ML conferences.
Provides automated scraping, NLP-based analysis, field classification, and
interactive visualizations.

Main modules:
- core: Core analysis functionality
- analysis: Advanced analysis tools  
- visualization: Data visualization components
"""

__version__ = "2.0.0"
__author__ = "Conference Analysis Team"

from .core.analyzer import UnifiedAnalyzer
from .main import main

__all__ = ["UnifiedAnalyzer", "main"]