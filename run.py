#!/usr/bin/env python3
"""
Time Capsule Web - Application Entry Point

This module serves as the main entry point for the Time Capsule Web application.
It initializes the Flask application and runs the development server.
"""

import os
import sys

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
from backend.app import create_app

# Load environment variables
load_dotenv()


def main():
    """Main entry point for the application.

    Initializes and runs the Flask development server with configuration
    from environment variables.

    Environment Variables:
        HOST: Server host address (default: '0.0.0.0').
        PORT: Server port number (default: 5000).
        FLASK_DEBUG: Enable debug mode when set to '1' (default: '0').

    Returns:
        None
    """
    app = create_app()
    
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', '0') == '1'
    
    print(f"Starting Time Capsule Web on http://{host}:{port}")
    print("Press Ctrl+C to stop the server")
    
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    main()
