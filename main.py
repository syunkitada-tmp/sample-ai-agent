#!/usr/bin/env python3
"""
Japanese Stock Information AI Agent
Entry point for the CLI application.
"""

import sys
import os

# Add src to path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.presentation.cli.main import cli

if __name__ == '__main__':
    cli()