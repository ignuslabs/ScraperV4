"""Test Suite for ScraperV4 - sets up proper import paths."""

import sys
import os

# Get the project root directory (parent of tests/)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add project root to path so we can import from src/
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Also ensure src/ is directly accessible
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)
