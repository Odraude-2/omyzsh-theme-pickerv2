# Oh-My-Zsh Theme Picker TUI

A terminal-based interface (TUI) to preview and apply **Oh-My-Zsh** themes in real-time. 
It runs the theme in a secure sandbox, capturing the exact prompt with all ANSI colors and symbols, without modifying your shell until you click apply.

<img width="1123" height="495" alt="Screenshot_20260204_235634" src="https://github.com/user-attachments/assets/e8fc3710-e50e-46bc-9353-58cd700fd6c2" />


## Features
- **Real-time Preview**: See exactly how the prompt looks (Git integration, time, colors).
- **Auto-Download**: Automatically fetches themes from the official [Oh-My-Zsh repo](https://github.com/ohmyzsh/ohmyzsh).
- **Safe Sandbox**: Previews run in an isolated environment (`/tmp/omz-preview`).
- **One-Key Apply**: Press `Enter` to backup your `.zshrc` and apply the new theme instantly.
- **Vim-style Navigation**: Use `j` / `k` to browse themes efficiently.

## Requirements
- Linux / macOS
- `zsh` installed
- Python 3.8+ (if running from source)

## Installation (Source)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Odraude-2/omyzsh-theme-picker.git
   cd omyzsh-theme-picker
   ```

2. **Set up the environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Run the app:**
   ```bash
   python3 -m src.main
   ```

## Controls
| Key | Action |
| :--- | :--- |
| `↑` / `k` | Move cursor up |
| `↓` / `j` | Move cursor down |
| `Enter` | **Apply** selected theme |
| `q` | Quit application |

## How it works
The application spawns a background `zsh` process in a PTY (pseudo-terminal) using a temporary `.zshrc`. It captures the raw bytes, strips the control characters, and renders the ANSI output to the preview pane. 

When you apply a theme, it:
1. Backs up your `~/.zshrc`.
2. Updates the `ZSH_THEME` variable.
3. Installs the theme file to `~/.oh-my-zsh/custom/themes` if it was downloaded remotely.

## License
MIT
