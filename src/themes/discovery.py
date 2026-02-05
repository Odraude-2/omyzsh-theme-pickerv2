from pathlib import Path
import os

class ThemeDiscovery:
    """Discovers available Oh-My-Zsh themes."""

    def __init__(self):
        self.omz_path = Path(os.environ.get("ZSH", Path.home() / ".oh-my-zsh"))
        self.themes = []

import requests
import logging

logger = logging.getLogger(__name__)

class ThemeDiscovery:
    """Discovers available Oh-My-Zsh themes."""

    OHMYZSH_REPO_API = "https://api.github.com/repos/ohmyzsh/ohmyzsh/contents/themes"
    RAW_THEME_URL = "https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/themes/{theme}.zsh-theme"

    def __init__(self, cache_dir: str = ".cache/themes"):
        self.omz_path = Path(os.environ.get("ZSH", Path.home() / ".oh-my-zsh"))
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.themes = []

    def scan_themes(self):
        """Scans for themes in standard/custom dirs AND remote (cached list)."""
        local_themes = set()
        
        # Standard themes
        std_themes_dir = self.omz_path / "themes"
        if std_themes_dir.exists():
            for f in std_themes_dir.glob("*.zsh-theme"):
                local_themes.add(f.stem)

        # Custom themes
        custom_themes_dir = self.omz_path / "custom/themes"
        if custom_themes_dir.exists():
             for f in custom_themes_dir.glob("*.zsh-theme"):
                local_themes.add(f.stem)
             for d in custom_themes_dir.iterdir():
                 if d.is_dir():
                     theme_file = d / f"{d.name}.zsh-theme"
                     if theme_file.exists():
                         local_themes.add(d.name)
        
        # If we have very few local themes, or user wants remote, lets fetch remote list if not cached
        # For this MVP, we will fetch standard list if local is empty OR just append standard ones 
        # that we know exist so user can select them.
        
        # Let's eagerly fetch the list of standard themes from GitHub API if valid
        # This allows users without OMZ to see themes.
        remote_themes = self._fetch_remote_list()
        
        all_themes = local_themes.union(remote_themes)
        self.themes = sorted(list(all_themes))
        return self.themes

    def _fetch_remote_list(self):
        """Fetches list of themes from GitHub API."""
        # Simple caching of the list
        list_cache = self.cache_dir / "remote_list.txt"
        if list_cache.exists():
             return set(list_cache.read_text().splitlines())

        try:
            resp = requests.get(self.OHMYZSH_REPO_API, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                themes = {item['name'].replace(".zsh-theme", "") for item in data if item['name'].endswith(".zsh-theme")}
                
                # Save to cache
                list_cache.write_text("\n".join(themes))
                return themes
        except Exception as e:
            logger.error(f"Failed to fetch remote themes: {e}")
        
        return set()

    def get_theme_path(self, theme_name: str):
        """
        Returns the path to the theme file. 
        Downloads it if it's a remote theme and not found locally.
        """
        # 1. Check local installed
        std_path = self.omz_path / "themes" / f"{theme_name}.zsh-theme"
        if std_path.exists():
            return std_path
            
        custom_path = self.omz_path / "custom/themes" / f"{theme_name}.zsh-theme"
        if custom_path.exists():
            return custom_path
            
        # 2. Check cache
        cached_path = self.cache_dir / f"{theme_name}.zsh-theme"
        if cached_path.exists():
            return cached_path
            
        # 3. Download
        return self._download_theme(theme_name, cached_path)

    def _download_theme(self, theme_name, dest_path):
        url = self.RAW_THEME_URL.format(theme=theme_name)
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                dest_path.write_text(resp.text)
                return dest_path
        except Exception as e:
            logger.error(f"Error downloading theme {theme_name}: {e}")
        return None

