import sys
import os

# Ensure the src directory is in the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from src.main import ThemePreviewApp

if __name__ == "__main__":
    app = ThemePreviewApp()
    app.run()
