import sys
import os

# Add the project root and frontend to the path so modules can find each other
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend"))

import streamlit as st

# Import the dashboard logic
# We use exec or import depending on how dashboard.py is structured.
# Since dashboard.py is a standard Streamlit script, we can just import it 
# if it doesn't have a name == main guard, or we can use the run command.
# The cleanest way for Streamlit is to have the entry logic in a function.

from dashboard import main

if __name__ == "__main__":
    main()
