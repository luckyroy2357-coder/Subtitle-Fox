"""
Netlify serverless function for Flask app
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from app import app

# Netlify serverless function handler
def handler(event, context):
    """Handle Netlify serverless function requests"""
    from serverless_wsgi import handle_request
    
    return handle_request(app, event, context)

