from src.main import ThemePreviewApp, ThemeItem
from textual.widgets import ListItem

def test_theme_loading_with_special_chars():
    # Mock themes
    special_themes = ["wezm+", "foo-bar", "normal", "123_test"]
    
    app = ThemePreviewApp()
    app.themes = special_themes
    
    # We will just test the list item creation logic, we don't need to run the full app
    # But we need to verify the code change works.
    
    print("Testing ThemeItem creation...")
    for theme in special_themes:
        try:
            item = ThemeItem(theme, theme_name=theme)
            print(f"✅ Created item for '{theme}'")
            if item.theme_name != theme:
                print(f"❌ Mismatch: {item.theme_name}")
        except Exception as e:
            print(f"❌ Failed to create item for '{theme}': {e}")

if __name__ == "__main__":
    test_theme_loading_with_special_chars()
