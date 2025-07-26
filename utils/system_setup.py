"""
Install Dependencies Script
Installs required Python packages for the AI Conference Analysis system
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a Python package using pip"""
    try:
        print(f"📦 Installing {package}...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", package], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {package} installed successfully")
            return True
        else:
            print(f"❌ Failed to install {package}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing {package}: {e}")
        return False

def check_requirements_file():
    """Check if requirements.txt exists and install from it"""
    if os.path.exists('requirements.txt'):
        print("📋 Found requirements.txt, installing from file...")
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ All requirements installed successfully")
                return True
            else:
                print(f"❌ Failed to install requirements: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error installing requirements: {e}")
            return False
    return False

def main():
    """Install all required packages"""
    print("🚀 Installing Dependencies for AI Conference Paper Analysis")
    print("="*60)
    
    # Try to install from requirements.txt first
    if check_requirements_file():
        print("\n✅ All dependencies installed successfully!")
        return
    
    print("📋 Installing core packages manually...")
    
    # Core packages
    core_packages = [
        "PyPDF2",
        "pymupdf",
        "aiofiles", 
        "aiohttp",
        "sentence-transformers",
        "torch",
        "pymilvus",
        "transformers"
    ]
    
    successful = 0
    total = len(core_packages)
    
    for package in core_packages:
        if install_package(package):
            successful += 1
    
    print("\n" + "="*60)
    print("INSTALLATION SUMMARY")
    print("="*60)
    print(f"Successfully installed: {successful}/{total} packages")
    
    if successful == total:
        print("✅ All packages installed successfully!")
        print("\nNext steps:")
        print("1. Start Milvus server (if not running)")
        print("2. Run: python test_system.py")
    else:
        print(f"❌ {total - successful} packages failed to install")
        print("Please check error messages above and install manually if needed")

if __name__ == "__main__":
    main()