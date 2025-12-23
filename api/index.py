"""
Vercel serverless function entry point
"""
from app import app

# Vercel expects the app to be available as a handler
handler = app

