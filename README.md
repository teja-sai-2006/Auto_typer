# Auto Typer - Text Snippet Auto-Typing Application

A cross-platform Python application that automatically types text snippets via global hotkeys. Perfect for repetitive typing tasks, code templates, and quick text insertion.

## Features

✨ **Core Features:**
- 📝 Create and manage text snippets with custom hotkeys
- ⌨️ Global hotkey support (Windows, Linux, macOS)
- 🎯 Natural typing with configurable delays between characters
- ⏸️ Pause/Resume typing (Ctrl+Space)
- 🛑 Stop typing (Ctrl+Esc)
- 📊 Typing history tracking
- 🔄 Text transformations (uppercase, lowercase, remove spaces/symbols)
- 🎲 Backspace simulation for natural typing
- 💾 Import/Export snippets to JSON

## Installation

### Quick Start (Automatic Setup)

```bash
# Linux/macOS
python setup.py
source venv/bin/activate
python run_auto_typer.py

# Windows (PowerShell)
python setup.py
.\venv\Scripts\Activate.ps1
python run_auto_typer.py
```

### Manual Setup

```bash
# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate  # Linux/macOS
# OR
.\venv\Scripts\Activate.ps1  # Windows

# Install dependencies
pip install -r requirements.txt

# Run
python run_auto_typer.py
```

### Dependencies

- **Python 3.8+**
- **keyboard>=0.13.5** - Global hotkey registration
- **tkinter** - GUI framework (included with Python)

### System Requirements

**Windows:**
- Optional: Run as Administrator for system-wide hotkeys
- Python 3.8+ with tkinter

**Linux:**
- Recommended: Run with `sudo` for system-wide hotkeys
  - Without sudo, a warning is shown but app still works
- Install tkinter: `sudo apt install python3-tk` (Ubuntu/Debian)

**macOS:**
- Grant accessibility permissions in System Preferences
- Install tkinter if needed: `brew install python-tk@3.x`

For detailed installation help, see [INSTALLATION.md](INSTALLATION.md)

## Usage

### Running the Application

```bash
# Activate virtual environment first
source venv/bin/activate  # Linux/macOS

# Run (with sudo on Linux for full hotkey support)
sudo python run_auto_typer.py
```

### Creating Snippets

1. **Open the GUI** - The application window appears with a snippet list
2. **Create New Snippet** - Enter snippet name, text, and hotkey
3. **Configure Settings:**
   - **Typing Speed:** Set min/max delay between characters (milliseconds)
   - **Text Transformations:** Apply uppercase, lowercase, remove spaces, etc.
   - **Backspace Simulation:** Optional random backspaces for natural typing
4. **Set Hotkey** - Define the hotkey (e.g., `ctrl+9`, `shift+alt+s`)
5. **Save** - Click Save to register the hotkey

### System Hotkeys

- **Pause/Resume:** Ctrl+Space (or Ctrl+Shift+Space, Ctrl+Alt+Space)
- **Stop:** Ctrl+Esc (or Ctrl+Shift+Esc, Ctrl+Alt+Esc)

### Hotkey Format

Hotkeys are automatically normalized. Examples:
- `ctrl+a` - Control + A
- `shift+windows+s` - Shift + Windows Key + S
- `alt+f4` - Alt + F4
- Aliases: `control` → `ctrl`, `windows/cmd/command` → `windows`, `escape` → `esc`

## Recent Improvements (v1.2.1)

### Bug Fixes
✅ **Fixed type conversion crashes** - Added error handling for invalid JSON numeric values
✅ **Fixed race conditions** - Proper thread synchronization for pause/stop functionality
✅ **Fixed wrong snippet execution** - Closure variable capture now works correctly

### Cross-Platform Enhancements
✅ **Windows/Linux compatibility** - Tested and verified on both platforms
✅ **Linux privilege detection** - Automatic warning when running without sudo
✅ **macOS key mapping** - Fixed Command key normalization to work universally

### Code Quality
✅ **Removed unnecessary files** - Cleaned up temp files and build artifacts
✅ **Improved documentation** - Updated installation and usage guides
✅ **Better error handling** - All errors logged with clear messages

## Project Structure

```
Auto_typer-main/
├── run_auto_typer.py       # Main launcher (cross-platform)
├── setup.py                # Automated setup script
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── INSTALLATION.md         # Installation guide
├── USAGE_GUIDE.md          # Detailed usage guide
│
├── auto_typer/
│   ├── backend.py          # Core engine (hotkeys, typing, state management)
│   ├── frontend.py         # Tkinter GUI
│   ├── special_keys.py     # Linux-specific character handling
│   ├── debug_mapping.py    # Development utility
│   ├── resources/          # User data (snippets, history)
│   └── tests/              # Test files
│
└── venv/                   # Virtual environment (auto-created)
```

## Configuration

### Typing Behavior

- **Min Delay:** Minimum milliseconds between characters (default: 10ms)
- **Max Delay:** Maximum milliseconds between characters (default: 50ms)
- **Backspace Probability:** Chance of triggering backspace (0-1, default: 0%)

### File Storage

- **Snippets:** `auto_typer/resources/snippets.json`
- **History:** `auto_typer/resources/history.json`

Both are automatically created on first run.

## Troubleshooting

### Hotkeys not registering

**Linux:** Run with sudo
```bash
sudo python run_auto_typer.py
```

**Windows:** Run as Administrator
- Right-click PowerShell and select "Run as Administrator"

### "keyboard module not found"

```bash
source venv/bin/activate
pip install keyboard>=0.13.5
```

### tkinter not found

- **Ubuntu/Debian:** `sudo apt install python3-tk`
- **Arch Linux:** `sudo pacman -S tk`
- **macOS:** `brew install python-tk@3.x`

### Application crashes

Check console output for [backend] or [frontend] error messages, which provide detailed error information.

## Development

### Running Tests

```bash
source venv/bin/activate
cd auto_typer/tests
python -m pytest
```

### Code Structure

- **backend.py:** Hotkey registration, snippet execution, state management
- **frontend.py:** Tkinter GUI, user interactions
- **special_keys.py:** Linux-specific keyboard event handling

## Compatibility

| Platform | Status | Notes |
|----------|--------|-------|
| Windows | ✅ Tested | Run as Administrator recommended |
| Linux | ✅ Tested | Run with sudo recommended |
| macOS | ✅ Designed | Requires accessibility permissions |

## System Requirements

- Python 3.8+
- 50-60 MB disk space (including virtual environment)
- ~20 MB RAM during execution
- Network: Not required

## License

[See LICENSE file, if present]

## Contributing

Improvements and bug reports are welcome. Please test on your target platform before submitting.

## Support & Documentation

- **Installation Help:** [INSTALLATION.md](INSTALLATION.md)
- **Usage Guide:** [USAGE_GUIDE.md](USAGE_GUIDE.md)
- **Bug Fixes:** Check recent commits for latest improvements
- **Error Messages:** Console output prefixed with [backend] or [frontend]

---

**Version:** 1.2.1
**Last Updated:** March 2026
**Python Compatibility:** 3.8, 3.9, 3.10, 3.11, 3.12, 3.13, 3.14
- Unified color scheme for both dark and light themes
- More professional form field appearance with consistent padding

### Layout & Organization
- Responsive window sizing for different screen resolutions
- Better organized form fields grouped by function
- Enhanced visual hierarchy with section headers
- Improved status bar visibility

### Usability Improvements
- Enhanced text field appearance for better readability
- Increased padding in form sections for easier interaction
- Improved history view with sortable columns and export feature
- Better styling for all interactive elements

### System Integration
- Added launcher scripts for Linux (run_auto_typer.sh, run_arch_typer.sh)
- Improved handling of system-wide hotkeys with proper privilege management
- Better error handling for keyboard input across applications

## Installation / Running

The only runtime dependency is the `keyboard` library (plus Tkinter which ships with most Python installs).

Quick start (Linux / macOS):
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# For full global hotkey support on Linux you usually need sudo:
sudo python run_auto_typer.py
```

Quick start (Windows PowerShell):
```powershell
python -m venv venv
venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python run_auto_typer.py
```

Note: We removed the legacy helper scripts (`run_auto_typer.sh`, `run_auto_typer.bat`) because they added confusion and did not reliably handle privilege elevation. Use the unified `run_auto_typer.py` launcher instead.

If you run without elevation and some hotkeys fail to register you'll see a warning; you can then re-run with Administrator (Windows) or sudo (Linux) if needed.

## How to Use

1. Launch the application:
   - Preferred: run `python run_auto_typer.py` (add `sudo` on Linux if hotkeys fail)
   - Direct: `python auto_typer/frontend.py` also works (but launcher prepares resources)

2. Create a new snippet by filling in the details:
   - Name: A unique name for your snippet
   - Category: Optional grouping for organization
   - Text: The content to be typed
   - Min/Max Delay: The typing speed variation (in seconds)
   - Backspace settings: Probability and count for simulated typos
   - Hotkey: The key combination that triggers the typing

3. Click "Add / Save" to store your snippet

4. When you need to use the snippet, press its assigned hotkey while the application is running in the background.

### Built‑in Control Hotkeys (Multiple Fallbacks)

Because some desktop environments reserve certain combos, the app now registers several alternatives simultaneously:

Pause / Resume typing:
- ctrl+space
- ctrl+shift+space
- ctrl+alt+space

Stop typing immediately:
- ctrl+esc
- ctrl+shift+esc
- ctrl+alt+esc

Any one that isn't intercepted by the OS will work; you can press another if one triggers a system action.

## Building a Standalone Executable (.exe / single binary)

PyInstaller is the recommended tool. Install it in a clean venv first.

Windows example:
```bash
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt pyinstaller
pyinstaller --noconfirm --clean --onefile --windowed \
   --name AutoTyper \
   --icon auto_typer/resources/app_icon.ico \
   run_auto_typer.py
```

Linux example:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt pyinstaller
pyinstaller --noconfirm --clean --onefile --name auto_typer run_auto_typer.py
```

After build:
- Output binary is in `dist/`.
- Copy (or bundle) the `auto_typer/resources` directory if running in `--onedir` mode. In `--onefile` mode resources are accessed via the embedded path logic.

Optional: create a `.spec` file if you need data file collection customization.

### Common Packaging Tips
- If hotkeys fail on end-user systems, instruct them to “Run as Administrator” (Windows) or run via `sudo` (Linux) only if necessary.
- Avoid bundling unnecessary libraries to keep size small (only dependency is `keyboard`).
- Test both an elevated and non-elevated run for acceptable fallback behavior.

## Troubleshooting

### Uppercase Letters Not Working

If uppercase letters aren't typing correctly, try running the test script:

```bash
cd "code of the application"
sudo python test_backspace.py uppercase
```

### Backspace Simulation Issues

To test backspace functionality separately:

```bash
cd "code of the application"
sudo python test_backspace.py backspace
```

### Permission / Hotkey Registration Issues

If control hotkeys (pause/stop) or your snippet hotkeys do not work:
1. Re-run the launcher with elevated permissions (sudo on Linux, Run as Administrator on Windows).
2. Avoid system-reserved combos (e.g. many Linux distros use Ctrl+Space for input method switching; pick something like `ctrl+shift+1`).
3. Check the terminal log: it lists each registered hotkey or any failure.

## Requirements

- Python 3.8+ (recommended; earlier 3.6+ may work but untested recently)
- `keyboard` (see `requirements.txt`)
- Tkinter (ships with most Python distributions; on some minimal Linux distros install `python3-tk` package)

Install all requirements in dev mode:
```bash
pip install -r requirements.txt
```

## Contact

If you want to add any features or make any suggestions 
email: tejasai13052006@gmail.com

The code is completely made in Python, both front and back end.
