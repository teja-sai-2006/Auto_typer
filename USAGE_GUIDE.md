# Auto Typer Usage Guide

## Important: Running With Root Privileges

**The application requires root privileges on Linux to register global hotkeys.**

Always run the application using the provided script:

```
sudo ./run_sudo_typer.sh
```

## Creating and Using Snippets

### Creating a New Snippet:

1. Open the application using `sudo ./run_sudo_typer.sh`
2. Fill in the snippet details:
   - **Name**: A unique identifier for your snippet
   - **Category**: Optional grouping
   - **Text**: The content you want to type automatically
   - **Min/Max Delay**: Typing speed (lower = faster)
   - **Backspace Probability**: How often to simulate typos (0 = disabled)
   - **Hotkey**: Click the field and press your desired key combination

3. Click **Add / Save** to store your snippet

### Testing a Snippet:

1. Select a snippet from the list
2. Click **Test Typing**
3. You'll get a 3-second countdown to position your cursor where you want the text typed
4. The application will type the text automatically

### Using Hotkeys:

1. After setting up your snippets with hotkeys, they'll work system-wide
2. Press your defined hotkey combination (e.g., `Ctrl+1`) and the text will be typed
3. **Control keys during typing**:
   - `Ctrl+Space`: Pause/Resume typing
   - `Ctrl+Esc`: Stop typing completely

## Troubleshooting

### Hotkeys Not Working:

1. **Check Permissions**: Make sure you're running with sudo: `sudo ./run_sudo_typer.sh`
2. **Hotkey Format**: Use simple combinations like `ctrl+1` or `ctrl+shift+a` 
3. **Conflicting Hotkeys**: Avoid using hotkeys that your system or other applications already use

### Test Typing Not Working:

1. Make sure you focus your cursor in a text field before the countdown ends
2. Check if you're running the application with sudo
3. Try using a simpler snippet with less text for testing

### General Issues:

1. Check the terminal for error messages
2. Restart the application if it becomes unresponsive
3. If all else fails, try deleting the snippets.json file and starting fresh

## Advanced Features

- **Text Transformations**: Convert to uppercase/lowercase, remove spaces or symbols
- **History**: View and export your typing history
- **Import/Export**: Share snippets between computers or create backups
