#!/usr/bin/env python3
"""
Project Cleanup Utility
=======================

This script helps clean up redundant files and directories in the project.
"""

import os
import shutil
from pathlib import Path

def cleanup_project():
    """Clean up redundant files and directories"""
    project_root = Path(__file__).parent.parent.parent
    
    # Directories to remove (unrelated MCP projects)
    dirs_to_remove = [
        'arxiv-latex-mcp',
        'claude-code-mcp', 
        'claude-memory-mcp',
        'jupyter-notebook-mcp',
        'mcp-memory-keeper',
        'mcp-memory-service',
        'paper-search-mcp'
    ]
    
    # Files to remove (redundant scripts)
    files_to_remove = [
        'detailed_analysis_generator.py',
        'generate_comprehensive_trends.py',
        'generate_conference_trends_viz.py',
        'generate_enhanced_visualization.py',
        'generate_standalone_report.py',
        'generate_trend_visualization.py',
        'research_trends_analyzer.py',
        'research_trends_simple.py',
        'trend_analyzer.py',
        'serve.py'
    ]
    
    # Documentation files to merge
    docs_to_remove = [
        'COMPREHENSIVE_TRENDS_SUMMARY.md',
        'ENHANCED_ANALYSIS_COMPLETE_SUMMARY.md', 
        'KEYWORD_VISUALIZATION_SUMMARY.md',
        'MCP_THINKING_MEMORY_GUIDE.md',
        'RESEARCH_TRENDS_SUMMARY.md'
    ]
    
    print("🧹 Starting project cleanup...")
    
    # Remove unrelated directories
    for dir_name in dirs_to_remove:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"  📁 Removing directory: {dir_name}")
            shutil.rmtree(dir_path)
    
    # Remove redundant files
    for file_name in files_to_remove:
        file_path = project_root / file_name
        if file_path.exists():
            print(f"  📄 Removing file: {file_name}")
            file_path.unlink()
    
    # Remove redundant documentation
    for doc_name in docs_to_remove:
        doc_path = project_root / doc_name
        if doc_path.exists():
            print(f"  📋 Removing document: {doc_name}")
            doc_path.unlink()
    
    # Remove old directories
    old_dirs = ['src', 'code']
    for dir_name in old_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"  🗂️  Removing old directory: {dir_name}")
            shutil.rmtree(dir_path)
    
    # Clean up frontend
    frontend_path = project_root / 'frontend'
    frontend_clean_path = project_root / 'frontend_clean'
    
    if frontend_path.exists() and frontend_clean_path.exists():
        print("  🎨 Replacing frontend with cleaned version")
        shutil.rmtree(frontend_path)
        frontend_clean_path.rename(frontend_path)
    
    print("✅ Project cleanup completed!")
    print("\n📋 Optimized project structure:")
    print("  📁 conf_analysis/     - Core analysis system")
    print("  📁 tools/            - Utility tools")
    print("  📁 frontend/         - Clean web interface")
    print("  📁 outputs/          - Analysis results")
    print("  📁 tests/            - Test files")
    print("  📄 main_new.py       - New main entry point")
    print("  📄 CLAUDE.md         - Project instructions")
    print("  📄 README.md         - Project documentation")

if __name__ == "__main__":
    cleanup_project()