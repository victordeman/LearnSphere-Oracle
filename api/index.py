import sys
import os

# Add the root directory to sys.path to allow importing from backend.src.main
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from backend.src.main import app
