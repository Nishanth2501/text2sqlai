"""
Text-to-SQL Assistant - Streamlit Cloud Entry Point
This file serves as the entry point for Streamlit Cloud deployment.
"""

import sys
import os

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the main Streamlit app
from service.ui_streamlit import *
