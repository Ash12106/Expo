#!/usr/bin/env python3
"""
VVCE Solar Plant ML Prediction System - Development Server
Run this file to start the application in development mode
"""

import os
import logging
from app import app

# Configure logging for development
logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    # Set development environment variables if not already set
    if not os.environ.get('SESSION_SECRET'):
        os.environ['SESSION_SECRET'] = 'dev-secret-key-change-in-production'
    
    if not os.environ.get('DATABASE_URL'):
        os.environ['DATABASE_URL'] = 'sqlite:///instance/solar_ml.db'
    
    # Create instance directory if it doesn't exist
    os.makedirs('instance', exist_ok=True)
    
    print("Starting VVCE Solar Plant ML Prediction System...")
    print("Access the application at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    
    # Run in development mode
    app.run(host='0.0.0.0', port=5000, debug=True)