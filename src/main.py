from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label, Static
from textual.containers import Container, Horizontal, Vertical
from textual.binding import Binding
from rich.text import Text
from rich.ansi import AnsiDecoder

from .themes.discovery import ThemeDiscovery
from .sandbox.manager import SandboxManager
from .preview.engine import PreviewEngine
from .apply.engine import ApplyEngine
import logging
import asyncio

# Configure basic logging
logging.basicConfig(level=logging.ERROR, filename="tui_errors.log")

class ThemeItem(ListItem):
    """ListItem that holds the theme name safely."""
    def __init__(self, label: str, theme_name: str):
        super().__init__(Label(label))
        self.theme_name = theme_name

class ThemePreviewApp(App):
    """ZSH Theme Preview TUI."""

    CSS = """
    Screen {
        layout: horizontal;
        background: $surface;
    }

    #sidebar {
        width: 30;
        dock: left;
        height: 100%;
        background: $surface;
        border-right: vkey $primary;
        scrollbar-gutter: stable;
    }

    #preview_container {
        height: 100%;
        width: 1fr;
        padding: 0 1;
        background: black;  /* Keep preview black for accurate terminal colors */
        color: white;
    }
    
    #preview_output {
        height: 100%;
    }

    /* Ranger-style List Items */
    ListItem {
        padding: 0 1;
        color: $text;
    }

    /* Highlight hovered item slightly */
    ListItem:hover {
        background: $boost;
    }
    
    /* Highlight selected item clearly (reverse or accent) */
    .selected {
        background: $primary;
        color: $text;
        text-style: bold;
    }
    
    /* Header/Footer styling */
    Header {
        background: $surface-darken-1;
        color: $text-muted;
        dock: top;
        height: 1;
    }
    
    Footer {
        background: $surface-darken-1;
        color: $text-muted;
        dock: bottom;
        height: 1;
    }
    
    Label.header {
        background: $surface;
        color: $primary;
        text-style: bold;
        padding: 0 1;
        margin-bottom: 1;
        border-bottom: solid $primary;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("enter", "select_theme", "Apply", show=True),
    ]

    def action_cursor_down(self):
        self.query_one("#theme_list", ListView).action_cursor_down()

    def action_cursor_up(self):
        self.query_one("#theme_list", ListView).action_cursor_up()

    def action_select_theme(self):
        """Called when user presses Enter (global binding)."""
        self._apply_current_selection()

    def on_list_view_selected(self, event: ListView.Selected):
        """Called when user presses Enter on the list."""
        if hasattr(event.item, 'theme_name'):
            self.apply_theme(event.item.theme_name)

    def _apply_current_selection(self):
        list_view = self.query_one("#theme_list", ListView)
        if list_view.highlighted_child:
            item = list_view.highlighted_child
            if isinstance(item, ThemeItem):
                self.apply_theme(item.theme_name)

    def apply_theme(self, theme_name):
        self.notify(f"Applying theme: {theme_name}...", title="Working", timeout=2)
        # Run in thread to not block UI during file ops/network
        self.run_worker(self._apply_theme_task(theme_name), exclusive=False)

    async def _apply_theme_task(self, theme_name):
        try:
            msg = await asyncio.to_thread(self.apply_engine.apply_theme, theme_name)
            self.notify(msg, title="Success", severity="information", timeout=5)
        except Exception as e:
            self.notify(f"Error: {e}", title="Error", severity="error", timeout=10)

    def __init__(self):
        super().__init__()
        self.sandbox = SandboxManager()
        self.discovery = ThemeDiscovery()
        self.preview_engine = PreviewEngine(self.sandbox, self.discovery)
        self.apply_engine = ApplyEngine(self.discovery)
        self.themes = []
        self.decoder = AnsiDecoder()

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Label("Available Themes", classes="header")
                yield ListView(id="theme_list")
            
            with Container(id="preview_container"):
                yield Label("Preview", classes="header")
                yield Static(id="preview_output", expand=True)
                
        yield Footer()

    def on_mount(self):
        """Event when the app loads."""
        self.sandbox.setup()
        self.themes = self.discovery.scan_themes()
        
        list_view = self.query_one("#theme_list", ListView)
        
        if not self.themes:
            list_view.append(ListItem(Label("No themes found")))
            return

        for theme in self.themes:
            # We use ThemeItem to store the theme name safely
            list_view.append(ThemeItem(theme, theme_name=theme))
            
        # Focus the list
        list_view.focus()

    def on_list_view_highlighted(self, event: ListView.Highlighted):
        """Called when the user moves selection."""
        if event.item and isinstance(event.item, ThemeItem):
            self.update_preview(event.item.theme_name)

    def update_preview(self, theme_name: str):
        """Starts a background worker to update the preview."""
        preview_pane = self.query_one("#preview_output", Static)
        preview_pane.update(Text("Generating preview...", style="dim"))
        
        self.run_worker(self._generate_preview_task(theme_name, preview_pane), exclusive=True)

    async def _generate_preview_task(self, theme_name, preview_pane):
        """Worker task to generate preview off-thread."""
        try:
            # Run the blocking generation in a thread
            output = await asyncio.to_thread(self.preview_engine.generate_preview, theme_name)
            
            # Decode ANSI
            rich_text = Text.from_ansi(output)
            
            # Update UI
            preview_pane.update(rich_text)
            
        except Exception as e:
            preview_pane.update(Text(f"Error: {e}", style="bold red"))

    def on_unmount(self):
        """Cleanup when app exits."""
        self.sandbox.cleanup()

if __name__ == "__main__":
    app = ThemePreviewApp()
    app.run()
