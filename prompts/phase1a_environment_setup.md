# Phase 1A: Environment Setup - ScraperV4 Development

## Objective
Set up a complete development environment for ScraperV4, a professional web scraping application using Scrapling, Eel, SQLAlchemy, and modern Python practices. Create a robust foundation with proper dependency management, virtual environment configuration, and essential development tools.

## Context
ScraperV4 is a desktop web scraping application that combines:
- **Scrapling**: Modern web scraping with StealthyFetcher for stealth capabilities
- **Eel**: Python-JavaScript bridge for desktop GUI applications
- **File Storage**: JSON-based data persistence system
- **Service Container**: Dependency injection architecture for scalable code organization
- **Template System**: Self-healing scraping configurations with automatic adaptation

## Prerequisites
- Python 3.9+ installed on system
- Git for version control
- Node.js 16+ (for frontend dependencies if needed)
- IDE/Editor with Python support (VS Code recommended)

## Implementation Steps

### 1. Python Environment Setup

```bash
# Verify Python version
python --version  # Should be 3.9+

# Create virtual environment in venv directory
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Upgrade pip to latest version
pip install --upgrade pip setuptools wheel
```

### 2. Core Dependencies Installation

```bash
# Install core scraping and web framework dependencies
pip install scrapling
pip install eel

# Install data processing and utilities
pip install pandas
pip install requests
pip install bs4 # from bs4 import BeautifulSoup
pip install lxml

# Install development and testing dependencies
pip install pytest
pip install pytest-asyncio
pip install pytest-cov
pip install black
pip install flake8
pip install mypy

# Install additional utilities
pip install python-dotenv
pip install click
pip install rich
pip install pydantic
```

### 3. Development Tools Configuration

Create `.env` file for environment variables:
```bash
# Storage configuration
STORAGE_DATA_FOLDER=data
STORAGE_JOBS_FOLDER=data/jobs
STORAGE_RESULTS_FOLDER=data/results

# Scrapling configuration
SCRAPLING_STEALTH_MODE=true
SCRAPLING_USER_AGENT=ScraperV4/1.0
SCRAPLING_TIMEOUT=30

# Eel configuration
EEL_PORT=8080
EEL_DEBUG=true

# Logging configuration
LOG_LEVEL=INFO
LOG_FILE=logs/scraperv4.log
```

Create `requirements.txt`:
```bash
# Generate requirements file
pip freeze > requirements.txt
```

### 4. Git Repository Initialization

```bash
# Initialize git repository (if not already done)
git init

# Create comprehensive .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
logs/
*.log

# Data files
data/jobs/*.json
data/results/*.json

# Environment variables
.env
.env.local
.env.production

# OS
.DS_Store
Thumbs.db

# Testing
.coverage
.pytest_cache/
htmlcov/

# MyPy
.mypy_cache/
.dmypy.json
dmypy.json
EOF
```

### 5. Project Configuration Files

Create `pyproject.toml`:
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "scraperv4"
version = "1.0.0"
description = "Professional web scraping application with Scrapling and Eel"
authors = [{name = "Your Name", email = "your.email@example.com"}]
license = {text = "MIT"}
requires-python = ">=3.9"
dependencies = [
    "scrapling",
    "eel",
    "pandas",
    "requests",
    "beautifulsoup4",
    "lxml",
    "python-dotenv",
    "click",
    "rich",
    "pydantic",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-asyncio",
    "pytest-cov",
    "black",
    "flake8",
    "mypy",
]

[tool.black]
line-length = 88
target-version = ['py39']
include = '\.pyi?$'

[tool.flake8]
max-line-length = 88
extend-ignore = ["E203", "W503"]

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --cov=src --cov-report=html --cov-report=term-missing"
```

### 6. Directory Structure Preparation

```bash
# Create essential directories
mkdir -p {src,tests,logs,data,templates,web}
mkdir -p src/{core,services,data,scrapers,utils}
mkdir -p data/{jobs,results,exports}
mkdir -p tests/{unit,integration,e2e}
mkdir -p web/{static,templates}
mkdir -p web/static/{css,js,images}

# Create empty __init__.py files for Python packages
touch src/__init__.py
touch src/core/__init__.py
touch src/services/__init__.py
touch src/data/__init__.py
touch src/scrapers/__init__.py
touch src/utils/__init__.py
touch tests/__init__.py
```

### 7. Development Environment Validation

Create `validate_environment.py`:
```python
#!/usr/bin/env python3
"""Environment validation script for ScraperV4."""

import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check Python version compatibility."""
    version = sys.version_info
    if version.major != 3 or version.minor < 9:
        print(f"❌ Python {version.major}.{version.minor} - Requires Python 3.9+")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_virtual_environment():
    """Check if virtual environment is active."""
    venv_active = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    if not venv_active:
        print("❌ Virtual environment not active")
        return False
    print("✅ Virtual environment active")
    return True

def check_dependencies():
    """Check core dependencies installation."""
    dependencies = [
        'scrapling', 'eel', 'pandas', 'requests', 'beautifulsoup4', 'lxml'
    ]
    
    failed = []
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep}")
            failed.append(dep)
    
    return len(failed) == 0

def check_directory_structure():
    """Check project directory structure."""
    required_dirs = [
        'src', 'tests', 'logs', 'data', 'templates', 'web',
        'src/core', 'src/services', 'src/data', 'src/scrapers', 'src/utils'
    ]
    
    failed = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            print(f"❌ Missing directory: {dir_path}")
            failed.append(dir_path)
        else:
            print(f"✅ Directory: {dir_path}")
    
    return len(failed) == 0

def main():
    print("🔍 ScraperV4 Environment Validation")
    print("=" * 40)
    
    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_virtual_environment),
        ("Dependencies", check_dependencies),
        ("Directory Structure", check_directory_structure),
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"\n{name}:")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 Environment setup completed successfully!")
        return 0
    else:
        print("❌ Environment setup has issues. Please fix the above errors.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

## Validation Criteria

### Success Metrics
1. ✅ Python 3.9+ virtual environment active
2. ✅ All core dependencies installed without conflicts
3. ✅ Project directory structure created
4. ✅ Configuration files in place (.env, pyproject.toml, .gitignore)
5. ✅ Git repository initialized (if applicable)
6. ✅ Environment validation script passes all checks

### Validation Commands
```bash
# Run environment validation
python validate_environment.py

# Verify virtual environment
which python  # Should point to venv/bin/python

# Test core imports
python -c "import scrapling, eel; print('Core imports successful')"

# Check package versions
pip list | grep -E "(scrapling|eel|pandas)"
```

## Troubleshooting Guide

### Common Issues and Solutions

**Virtual Environment Issues:**
```bash
# If activation fails, recreate environment
rm -rf venv
python -m venv venv
source venv/bin/activate
```

**Dependency Conflicts:**
```bash
# Clear pip cache and reinstall
pip cache purge
pip install --no-cache-dir -r requirements.txt
```

**Permission Issues (macOS/Linux):**
```bash
# Fix directory permissions
chmod -R 755 .
```

**Python Version Issues:**
- Use `pyenv` to install Python 3.9+ if system version is older
- On macOS: `brew install python@3.9`
- On Ubuntu: `sudo apt install python3.9 python3.9-venv`

### Environment Variables Troubleshooting
- Ensure `.env` file is in project root
- Verify no syntax errors in `.env` (no spaces around `=`)
- Check file permissions: `chmod 600 .env`

## Next Steps
After successful completion:
1. Proceed to **Phase 1B: Project Structure** to establish the application architecture
2. Keep the virtual environment activated for all subsequent development
3. Regularly update `requirements.txt` when adding new dependencies
4. Run `python validate_environment.py` periodically to ensure environment integrity

## File Deliverables
- `venv/` - Virtual environment directory
- `requirements.txt` - Dependency specifications
- `.env` - Environment variables configuration
- `pyproject.toml` - Project configuration
- `.gitignore` - Git ignore patterns
- `validate_environment.py` - Environment validation script
- Directory structure: `src/`, `tests/`, `logs/`, `data/`, `templates/`, `web/`