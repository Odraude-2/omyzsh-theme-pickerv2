import pexpect
import os
import logging
from ..sandbox.manager import SandboxManager

logger = logging.getLogger(__name__)

from ..themes.discovery import ThemeDiscovery

class PreviewEngine:
    """Handles the execution of ZSH in a PTY and captures the prompt output."""

    def __init__(self, sandbox_manager: SandboxManager, discovery: ThemeDiscovery = None):
        self.sandbox = sandbox_manager
        self.discovery = discovery

    def generate_preview(self, theme_name: str) -> str:
        """
        Generates a preview for the given theme.
        Returns the raw ANSI string captured from the terminal.
        """
        theme_path = None
        if self.discovery:
            theme_path = self.discovery.get_theme_path(theme_name)

        # 1. Setup Sandbox Config
        self.sandbox.create_zshrc(theme_name, theme_path=theme_path) # Ensure theme content is available (load if needed)
        # We need a way to access discovery instance or pass the path.
        # Ideally PreviewEngine should just ask SandboxManager to load 'X', 
        # but SandboxManager needs the FILE.
        # Refactor: PreviewEngine should use ThemeDiscovery to get the path? 
        # Or MainApp passes the path? MainApp passes the name.
        
        # Let's instantiate Discovery here or pass it in init.
        # For now, let's assume SandboxManager's create_zshrc handles the file 
        # if we pass the content or path.
        pass # Placeholder for diff match, implementation below

        
        # 2. Prepare Environment
        env = os.environ.copy()
        env["ZDOTDIR"] = str(self.sandbox.base_path)
        # Ensure we don't inherit some variables that might mess up the preview
        # But we need basic TERM stuff
        env["TERM"] = "xterm-256color" 

        # 3. Spawn ZSH
        # We spawn zsh to just load the prompt and wait for input.
        # We can try to capture what it prints.
        # -i for interactive, -c to run a command? 
        # If we run a command, the prompt might not show if not interactive.
        # 'zsh -i' will show the prompt and wait.
        
        try:
            # Spawning zsh in interactive mode
            child = pexpect.spawn("zsh -i", env=env, encoding="utf-8", timeout=3)
            
            # We expect the prompt to appear. 
            # The tricky part is knowing *what* the prompt is if we don't know the theme.
            # But usually zsh will print the prompt and then wait.
            # We can try to send a simple command like 'echo preview' and capture everything before it?
            # Or just wait a bit?
            
            # Strategy:
            # Send a carriage return to force a new prompt if needed (though start-up should show it).
            # Read everything.
            
            # Actually, `pexpect` reads until a pattern. If we don't have a pattern, it's hard.
            # But we can read non-blocking?
            
            # Let's try sending a unique string and waiting for it.
            # The prompt is printed *before* the unique string output.
            # ZSH startup -> Prompt -> We type 'echo MARKER' -> Output 'MARKER' -> Prompt again.
            
            # Ideally we want just the prompt.
            # If we send empty line?
            
            # Let's try reading initially.
            # child.expect(...) might be hard if prompt contains wild chars.
            
            # Alternative: use zsh to print the prompt variable?
            # echo $PROMPT might not render the functions inside it.
            # `print -P $PROMPT` ?
            
            # Better strategy for accuracy:
            # Send 'print -P "$PROMPT"'? No, themes use PROMPT_SUBST and complex hooks (precmd).
            # We must let zsh run its hooks.
            
            # So:
            # 1. Spawn
            # 2. Wait for some initial stabilization?
            # 3. Send Ctrl+C to clear any weird state?
            # 4. Read the output.
            
            # Let's try a simple approach first:
            # Spawn, wait for a short duration (latency check), read everything.
            
            # Refined Strategy:
            # Send a command that produces a known output, e.g. `echo __PREVIEW_END__`
            # The output will look like: 
            # [PROMPT] echo __PREVIEW_END__
            # __PREVIEW_END__
            # [PROMPT]
            
            # We can capture the first [PROMPT].
            
            # Note: Startup might produce "Oh My Zsh" banner or updates. We silenced updates in zshrc.
            
            # Wrapper to ensure we capture the prompt displayed AFTER OMZ loads.
            # We added 'echo "DEBUG_OMZ_LOADED"' to zshrc.
            # So output should be:
            # ... initialization ...
            # DEBUG_OMZ_LOADED
            # <PROMPT>
            
            child.expect("DEBUG_OMZ_LOADED")
            
            # Now we are at the prompt.
            # But the prompt might follow the newline after DEBUG_OMZ_LOADED.
            import time
            time.sleep(0.1) # Wait for prompt to render
            
            # Now send marker to verify where the prompt ends
            child.sendline("echo __MARKER__")
            child.expect("__MARKER__")
            
            # The prompt is in `child.before`
            # But `child.before` includes the newline after DEBUG_OMZ_LOADED and the 'echo __MARKER__' we typed.
            
            raw = child.before
            # Clean up:
            # child.before contains ".... echo " because we matched "__MARKER__"
            # and the input was "echo __MARKER__"
            
            # Remove the last occurrence of 'echo '
            if "echo " in raw:
                raw = raw.rsplit("echo ", 1)[0]
                
            return raw.strip()

        except Exception as e:
            logger.error(f"Error generating preview for {theme_name}: {e}")
            return f"Error: {e}"
