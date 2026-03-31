"""
run.py
======
Entry point for PuzzleVision.

Usage
-----
    python run.py
"""

import sys
import os

# Ensure the project root is on the Python path so that `src` is importable
sys.path.insert(0, os.path.dirname(__file__))

from src.app import main

if __name__ == "__main__":
    sys.exit(main())
