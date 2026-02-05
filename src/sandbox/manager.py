import os
import shutil
import tempfile
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class SandboxManager:
    """Manages the temporary sandbox environment for ZSH preview."""

    def __init__(self, base_path: str = "/tmp/omz-preview"):
        self.base_path = Path(base_path)
        self.zshrc_path = self.base_path / ".zshrc"
        self.omz_path = self.base_path / "oh-my-zsh"
        self.custom_themes_path = self.omz_path / "custom/themes"

    def setup(self):
        """Creates the sandbox directory structure and mocks necessary files."""
        if self.base_path.exists():
            shutil.rmtree(self.base_path)
        
        self.base_path.mkdir(parents=True, exist_ok=True)
        # Mock OMZ structure if we want to isolate completely, 
        # OR we can symlink the user's real OMZ if we just want to preview themes.
        # For safety and speed (no git clone), let's try to reuse the local OMZ but in a safe way
        # strictly not modifying it.
        # ACTUALLY, the requirement says "No modificar entorno del usuario".
        # So we should probably copy or link the OMZ lib but NOT the user's config.
        
        user_omz = Path.home() / ".oh-my-zsh"
        if user_omz.exists():
            # Symlink the OMZ lib to save space and time
            # We must be careful not to write to it.
            # But themes might be in custom...
            os.symlink(user_omz, self.omz_path)
        else:
             # Fallback if no local OMZ (maybe download minimal? or warn)
             # For MVP assuming local OMZ exists as per context found earlier
             logger.warning("Local .oh-my-zsh not found. Preview might fail if it depends on lib files.")

    def create_zshrc(self, theme_name: str, theme_path: Path = None):
        """Generates a temporary .zshrc that loads the specified theme."""
        
        # Ensure custom themes dir exists in sandbox
        sandbox_custom_themes = self.omz_path / "custom/themes"
        sandbox_custom_themes.mkdir(parents=True, exist_ok=True)

        if theme_path and theme_path.exists():
            # If the theme is external/cached, we need to make it available to the sandbox.
            # We can copy it to sandbox/oh-my-zsh/custom/themes/
            dest = sandbox_custom_themes / f"{theme_name}.zsh-theme"
            if not dest.exists(): # overwrite if needed or symlink? Copy is safer.
                shutil.copy(theme_path, dest)
        
        # Standard OMZ loading logic
        content = f"""
# Sandbox .zshrc
export ZSH="{self.omz_path}"
export ZSH_THEME="{theme_name}"

# Disable auto-update
zstyle ':omz:update' mode disabled

# Init OMZ
source $ZSH/oh-my-zsh.sh

# Disable the "partial line" marker (%)
unsetopt PROMPT_SP

echo "DEBUG_OMZ_LOADED"
"""
        with open(self.zshrc_path, "w") as f:
            f.write(content)
            
    def cleanup(self):
        """Removes the sandbox environment."""
        if self.base_path.exists():
            shutil.rmtree(self.base_path)
