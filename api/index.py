"""
Vercel serverless function entry point for Flask app
"""
import sys
import os

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import Flask app
from app import app

# Export for Vercel
# Vercel automatically handles WSGI apps
__all__ = ['app']
