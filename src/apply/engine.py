import os
import shutil
import re
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class ApplyEngine:
    """Handles applying the selected theme to the user's real configuration."""

    def __init__(self, discovery_engine):
        self.discovery = discovery_engine
        self.zshrc_path = Path.home() / ".zshrc"
        self.omz_custom_path = Path(os.environ.get("ZSH_CUSTOM", Path.home() / ".oh-my-zsh/custom")) / "themes"

    def apply_theme(self, theme_name: str) -> str:
        """
        Applies the theme:
        1. Backs up .zshrc
        2. Installs theme if remote.
        3. Updates ZSH_THEME in .zshrc.
        Returns a success message or raises Exception.
        """
        # 1. Backup .zshrc
        if self.zshrc_path.exists():
            backup_path = self.zshrc_path.with_suffix(f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            shutil.copy(self.zshrc_path, backup_path)
            logger.info(f"Backed up .zshrc to {backup_path}")
        else:
            raise FileNotFoundError(f"{self.zshrc_path} not found!")

        # 2. Ensure theme is installed
        # Check if it is a standard theme (in OMZ/themes) or needs custom installation
        theme_path = self.discovery.get_theme_path(theme_name)
        
        # If the theme path comes from our cache, we must install it to ~/.oh-my-zsh/custom/themes
        if ".cache" in str(theme_path):
             self._install_custom_theme(theme_name, theme_path)

        # 3. Modify .zshrc
        self._update_zshrc(theme_name)
        
        return f"Theme '{theme_name}' applied successfully! (.zshrc backed up)"

    def _install_custom_theme(self, theme_name, source_path):
        """Copies the cached theme to the user's custom themes directory."""
        self.omz_custom_path.mkdir(parents=True, exist_ok=True)
        dest_path = self.omz_custom_path / f"{theme_name}.zsh-theme"
        
        shutil.copy(source_path, dest_path)
        logger.info(f"Installed custom theme to {dest_path}")

    def _update_zshrc(self, theme_name):
        """Updates the ZSH_THEME variable in .zshrc."""
        content = self.zshrc_path.read_text()
        
        # Regex to find ZSH_THEME="..." or ZSH_THEME='...'
        # We replace the whole line
        new_line = f'ZSH_THEME="{theme_name}"'
        
        # Look for existing ZSH_THEME definition
        # Handles: ZSH_THEME="robbyrussell" or ZSH_THEME='robbyrussell' or ZSH_THEME=robbyrussell
        pattern = re.compile(r'^ZSH_THEME=.*$', re.MULTILINE)
        
        if pattern.search(content):
            new_content = pattern.sub(new_line, content)
        else:
            # If not found, append it (unlikely for OMZ users but possible)
            new_content = content + f"\n{new_line}\n"
            
        self.zshrc_path.write_text(new_content)
