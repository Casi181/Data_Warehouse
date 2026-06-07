"""Pytest configuration for the Casi Financial DW backend tests."""
import sys
import os

# Add backend root to sys.path so test imports resolve correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
