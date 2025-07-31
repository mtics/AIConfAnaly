#!/usr/bin/env python3
"""
AI Conference Paper Analysis System - Main Entry Point
=====================================================

Simplified main entry point for the reorganized conference analysis system.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import from the reorganized structure
from conf_analysis.main import main

if __name__ == "__main__":
    main()