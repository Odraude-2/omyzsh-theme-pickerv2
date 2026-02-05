from src.sandbox.manager import SandboxManager
from src.preview.engine import PreviewEngine
from src.themes.discovery import ThemeDiscovery
import logging

logging.basicConfig(level=logging.DEBUG)

def test_engine():
    print("Initializing Sandbox...")
    sandbox = SandboxManager()
    sandbox.setup()
    
    print("Discovering themes...")
    discovery = ThemeDiscovery()
    themes = discovery.scan_themes()
    print(f"Found {len(themes)} themes: {themes[:5]}...")
    
    if not themes:
        # Fallback if no specific themes found, try a standard one if exists, or just 'robbyrussell'
        themes = ["robbyrussell"]

    engine = PreviewEngine(sandbox)
    
    # Test first theme
    theme = themes[0]
    print(f"Testing preview for theme: {theme}")
    
    output = engine.generate_preview(theme)
    
    print("-" * 40)
    print("RAW OUTPUT CAPTURED:")
    print(repr(output))
    print("-" * 40)
    
    if len(output.strip()) > 0:
        print("SUCCESS: Output captured.")
    else:
        print("FAILURE: No output captured.")
    
    sandbox.cleanup()

if __name__ == "__main__":
    test_engine()
