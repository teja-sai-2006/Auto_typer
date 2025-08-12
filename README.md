# Auto Typer

A cross-platform application that simulates keyboard typing with customizable delays, text snippets, and hotkeys. Works seamlessly on both Windows and Linux.

## Features

1) Simulates typing on the keyboard based on saved snippets
2) Typing starts when a configured hotkey is pressed
3) Works in the background while the application is running
4) Includes random backspacing to make typing appear more human-like
5) Customizable backspace probability (0 to 1) and frequency
6) Adjustable typing speed with minimum and maximum delay settings
7) Support for multiple saved snippets with categories
8) Enhanced special character support, including uppercase letters
9) Improved error handling and fallback methods for all typing operations
10) New test scripts for debugging and validating functionality

## Latest Updates (August 2025)

### Core
- Refactored launcher (`run_auto_typer.py`) to detect packaged (PyInstaller) vs development mode.
- Graceful, optional privilege elevation: continues without admin/root if unavailable (with warning) instead of exiting.
- More robust resource path resolution when frozen (supports `--onefile`).
- Added safer dependency bootstrap (skipped when frozen; dev mode auto-installs only `keyboard`).

### Typing & Stability
- Improved special key handling and uppercase reliability (shift timing adjustments).
- Added safer snippet save (temp file + atomic replace) and history export formatting.
- Reduced risk of hotkey duplication by normalization improvements.

### UI / UX
- Reorganized form sections with semantic grouping and consistent spacing.
- Improved history window (Treeview, alternating row colors, export & clear actions).
- Added transformation toggles (uppercase, lowercase, remove spaces/symbols, keep alphanumeric).

### Developer / Packaging
- Added minimal `requirements.txt` (only `keyboard`).
- Documented reproducible PyInstaller build process for Windows & Linux.
- Launcher now tolerant to missing elevation—helpful for distributing `.exe` without forcing UAC.

### (Older 2023 Highlights)
- Backspace simulation & randomness
- Setup script & virtualenv automation
- Test scripts for keyboard/backspace behavior

## Recent UI Improvements

### Theme & Appearance
- Improved theme toggle button with better visibility and styling
- Enhanced visual design with consistent borders and better hover/press states
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

## Installation

### Method 1: Using the setup script (Recommended for development)

1. Clone or download this repository
2. Run the setup script to create a virtual environment:

```bash
python setup.py
```

3. This will create a `run_auto_typer.sh` (Linux/Mac) or `run_auto_typer.bat` (Windows) script
4. Run the script to start the application:

```bash
# On Linux/Mac:
./run_auto_typer.sh

# On Windows:
run_auto_typer.bat
```

### Method 2: Using sudo (Linux/Mac) when needed

The keyboard library requires root privileges to register global hotkeys. Use the provided script:

```bash
sudo ./run_sudo_typer.sh
```

### Method 3: Manual installation

1. Install required packages:

```bash
pip install keyboard
```

2. Run the application:

```bash
cd "code of the application"
python frontend.py
```

## How to Use

1. Launch the application:
   - On Windows: Double-click `frontend.py` or create a shortcut
   - On Linux: Use `run_sudo_typer.sh` for root privileges
   - Alternative: Use the new setup script and `run_auto_typer.sh`

2. Create a new snippet by filling in the details:
   - Name: A unique name for your snippet
   - Category: Optional grouping for organization
   - Text: The content to be typed
   - Min/Max Delay: The typing speed variation (in seconds)
   - Backspace settings: Probability and count for simulated typos
   - Hotkey: The key combination that triggers the typing

3. Click "Add / Save" to store your snippet

4. When you need to use the snippet, press its assigned hotkey while the application is running in the background

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

### Permission Issues

On Linux/Mac, the keyboard library requires root privileges:

```bash
sudo ./run_sudo_typer.sh
```

On Windows, run as Administrator.

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
