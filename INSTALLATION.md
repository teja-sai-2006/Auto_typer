# Auto Typer - Installation & Setup Guide

## Quick Start

### Linux / macOS
```bash
# 1. Clone or navigate to the project directory
cd Auto_typer-main

# 2. Run setup (creates venv and installs dependencies)
python setup.py

# 3. Activate virtual environment
source venv/bin/activate

# 4. Run the application (with sudo for full hotkey support on Linux)
sudo python run_auto_typer.py
```

### Windows
```batch
# 1. Navigate to project directory
cd Auto_typer-main

# 2. Run setup (creates venv and installs dependencies)
python setup.py

# 3. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 4. Run as Administrator (recommended for system-wide hotkeys)
python run_auto_typer.py
```

---

## What Gets Installed

### Required Dependencies
- **keyboard** (>= 0.13.5) - Global hotkey registration and keyboard event handling
  - Handles cross-platform support for Windows, Linux, and macOS

### Standard Library
- **tkinter** - GUI framework (included with Python on most systems)
- **json** - Configuration file handling
- **threading** - Concurrent typing execution
- **os** - File and path operations

### Installation Size
- Virtual environment: ~50-60 MB
- Application code: ~150 KB

---

## Platform-Specific Requirements

### Windows
- **Optional**: Run as Administrator for system-wide hotkey registration
- Python 3.8+ with tkinter included

### Linux
- **Recommended**: Run with `sudo` for system-wide hotkey registration
  - Without `sudo`, a warning will be displayed
  - Some hotkeys may not register globally
- Install tkinter package:
  - Arch Linux: `pacman -S tk`
  - Ubuntu/Debian: `apt install python3-tk`
  - Fedora: `dnf install python3-tkinter`

### macOS
- **Required**: Grant accessibility permissions in System Preferences
- Python 3.8+ with tkinter
- Install tkinter (if not included):
  - `brew install python-tk@3.x` (replace x with your Python version)

---

## Project Structure

```
Auto_typer-main/
├── run_auto_typer.py       # Main launcher (handles privilege elevation)
├── setup.py                # Installation script
├── requirements.txt        # Dependency list
├── README.md               # Project documentation
├── USAGE_GUIDE.md          # User guide
├── INSTALLATION.md         # This file
│
├── auto_typer/             # Main package
│   ├── backend.py          # Core hotkey & typing engine
│   ├── frontend.py         # Tkinter GUI
│   ├── special_keys.py     # Linux-specific character handling
│   ├── debug_mapping.py    # Development utility
│   ├── resources/          # Snippets & history data storage
│   └── tests/              # Test files
│
└── venv/                   # Virtual environment (created by setup.py)
    ├── bin/               # Python executables and scripts
    └── lib/               # Installed packages
```

---

## Cleaned Up Files

The following unnecessary files have been removed:
- `tempCodeRunnerFile.py` - VS Code temporary file
- `=0.13.5` - Corrupted pip metadata file
- `run_auto_typer.bat` - Empty Windows batch file
- `tree.txt` - File listing documentation

---

## Troubleshooting

### Issue: "keyboard module not found"
**Solution**:
```bash
source venv/bin/activate
pip install keyboard>=0.13.5
```

### Issue: tkinter not found
**Solution**: Install system package
- Linux (Ubuntu/Debian): `sudo apt install python3-tk`
- Linux (Arch): `sudo pacman -S tk`
- macOS: `brew install python-tk@3.x`

### Issue: Hotkeys not registering on Linux
**Solution**: Run with sudo
```bash
source venv/bin/activate
sudo python run_auto_typer.py
```

### Issue: Hotkeys not registering on Windows
**Solution**: Run PowerShell as Administrator
```powershell
.\venv\Scripts\Activate.ps1
# Right-click PowerShell and select "Run as administrator"
python run_auto_typer.py
```

### Issue: Application crashes
**Solution**: Check console output for detailed error messages. All errors are logged with [backend], [frontend] prefixes.

---

## Configuration

### Hotkey Format
Hotkeys are normalized automatically. Supported formats:
- Modifier + Key: `ctrl+a`, `shift+windows+s`, `alt+f4`
- Aliases are automatically converted:
  - `control` → `ctrl`
  - `windows/cmd/command` → `windows`
  - `escape` → `esc`
  - `pagedown` → `pgdn`

### System Control Hotkeys
- **Pause/Resume**: Ctrl+Space (or Ctrl+Shift+Space, Ctrl+Alt+Space if reserved)
- **Stop**: Ctrl+Esc (or Ctrl+Shift+Esc, Ctrl+Alt+Esc if reserved)

---

## Development

### Running from source without installation
```bash
cd Auto_typer-main

# Create virtual environment manually
python -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run
python run_auto_typer.py
```

### Running tests (if available)
```bash
source venv/bin/activate
cd auto_typer/tests
python -m pytest
```

---

## Version Info
- **Application**: Auto Typer v1.2
- **Python**: 3.8+
- **Keyboard Library**: 0.13.5+
- **GUI Framework**: Tkinter

---

## Support
For issues or feature requests, refer to:
- `README.md` - Project overview
- `USAGE_GUIDE.md` - Feature documentation
- `auto_typer/backend.py` - Code with detailed comments
