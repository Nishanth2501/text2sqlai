"""
Text-to-SQL Assistant - Streamlit Cloud Entry Point
This file serves as the entry point for Streamlit Cloud deployment.
"""

import sys
import os

# Add the current directory to Python path so we can import src modules
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Now import and run the main Streamlit app
try:
    from service.ui_streamlit import *
except ImportError as e:
    import streamlit as st
    st.error(f"Import error: {e}")
    st.error("Please check that all dependencies are installed correctly.")
    st.stop()
