# Note: This script requires the 'keyboard' library, which may need administrative privileges (e.g., running as Administrator on Windows) to register global hotkeys system-wide. [cite: 18]
import json
import os
import time
import keyboard
from datetime import datetime
import random  # Added for backspace probability
from threading import Thread
from datetime import datetime

SNIPPETS_FILE = "snippets.json"
HISTORY_FILE = "history.json"

# --- Snippet Loading/Saving ---

def load_snippets():
    """Loads snippets from the JSON file."""
    if not os.path.exists(SNIPPETS_FILE):
        return {}
    try:
        with open(SNIPPETS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"[backend] Error loading snippets: {e}")
        return {}

def save_snippets(snippets):
    """Saves snippets to the JSON file."""
    try:
        with open(SNIPPETS_FILE, "w", encoding="utf-8") as f:
            json.dump(snippets, f, indent=2, ensure_ascii=False) # Use ensure_ascii=False for broader character support
    except IOError as e:
        print(f"[backend] Error saving snippets: {e}")

# --- Hotkey Handling ---

def normalize_hotkey(hotkey_str):
    """Normalizes hotkey string parts (e.g., 'control' to 'ctrl')."""
    replacements = {
        "control": "ctrl",
        "control_l": "ctrl",
        "control_r": "ctrl",
        "alt_l": "alt",
        "alt_r": "alt",
        "shift_l": "shift",
        "shift_r": "shift",
        "win": "windows", # Added for windows key if needed
        "command": "cmd", # Added for mac command key if needed
        "option": "alt", # Mac option key alias
        "escape": "esc", # Common alias
        "pagedown": "pgdn", # Common alias
        "page up": "pgup", # Common alias
        "insert": "ins", # Common alias
        "delete": "del", # Common alias
        "print screen": "print_screen", # Common alias
        "scroll lock": "scroll_lock", # Common alias
        "caps lock": "caps_lock", # Common alias
        "num lock": "num_lock", # Common alias
        "pause": "pause break", # Common alias
        "break": "pause break", # Common alias
    }
    # Standardize separators and handle potential extra spaces
    parts = hotkey_str.lower().replace(" ", "").replace("-", "+").split("+") # Handle both space and hyphen as separators
    normalized = sorted(list(set(replacements.get(p, p) for p in parts if p))) # Sort modifiers, remove duplicates
    # Ensure order of modifiers for consistent hotkey recognition if needed, e.g., ctrl+shift+a vs shift+ctrl+a
    # The 'keyboard' library handles common modifier order variations, but sorting provides a canonical form.
    # Common modifiers first, then other keys
    modifier_order = ['ctrl', 'shift', 'alt', 'windows', 'cmd']
    sorted_parts = sorted(normalized, key=lambda x: (x not in modifier_order, modifier_order.index(x) if x in modifier_order else len(modifier_order), x))

    return "+".join(sorted_parts)


registered_hotkeys = []  # Store handles to remove later

def register_hotkeys(snippets):
    """Registers hotkeys for all snippets."""
    global registered_hotkeys

    # Unregister previous hotkeys safely
    for handle in registered_hotkeys:
        try:
            keyboard.remove_hotkey(handle)
        except Exception as e:
            # This can happen if the hotkey was already removed or invalid
            # print(f"[backend] Info: Could not remove hotkey handle: {e}") # Optional: log if needed
            pass # Continue trying to remove others
    registered_hotkeys.clear()
    print("[backend] Cleared previous hotkeys.")

    # Register new hotkeys
    count = 0
    for name, data in snippets.items():
        hotkey = data.get("hotkey", "").strip()
        if not hotkey:
            continue
        try:
            # Normalize before registering
            hotkey_norm = normalize_hotkey(hotkey)
            if not hotkey_norm: # Skip if normalization results in empty string
                print(f"[backend] Warning: Skipping empty normalized hotkey for snippet '{name}' (original: '{hotkey}')")
                continue

            # Use a lambda that captures the current 'name'
            # Pass trigger_on_release=False if needed, but default (on press) is usually desired
            # Adding a small delay before execution to prevent interfering with hotkey itself
            handle = keyboard.add_hotkey(hotkey_norm, lambda n=name: Thread(target=lambda: (time.sleep(0.1), execute_snippet(n)), daemon=True).start(), trigger_on_release=False)
            registered_hotkeys.append(handle)
            count += 1
            # print(f"[backend] Registered hotkey '{hotkey_norm}' for '{name}'") # Optional: verbose logging
        except ValueError as e:
            print(f"[backend] Error: Invalid hotkey format '{hotkey}' (normalized: '{hotkey_norm}') for snippet '{name}': {e}")
        except Exception as e:
            print(f"[backend] Error: Could not register hotkey '{hotkey}' (normalized: '{hotkey_norm}') for snippet '{name}': {e}")
    print(f"[backend] Registered {count} hotkeys.")


# --- Snippet Execution ---

def execute_snippet(name):
    """Executes the typing sequence for a given snippet name."""
    print(f"[backend] Executing snippet: {name}") # Log execution start
    snippets = load_snippets()
    snippet = snippets.get(name)
    if not snippet:
        print(f"[backend] Snippet '{name}' not found.")
        return

    # --- Get Parameters ---
    # Use default values directly, as they should be validated in the frontend before saving
    min_delay = float(snippet.get("min_delay", 0.01))
    max_delay = float(snippet.get("max_delay", 0.05))
    backspace_prob = float(snippet.get("backspace_probability", 0.0))
    min_backspaces = int(snippet.get("min_backspaces", 1))
    max_backspaces = int(snippet.get("max_backspaces", 3))
    text = snippet.get("text", "")

    # Basic validation (redundant if frontend validates, but good for safety)
    if not (0 <= min_delay <= max_delay):
        print(f"[backend] Warning: Invalid delays for '{name}'. Using defaults.")
        min_delay, max_delay = 0.01, 0.05
    if not (0.0 <= backspace_prob <= 1.0):
        print(f"[backend] Warning: Invalid backspace probability for '{name}'. Setting to 0.")
        backspace_prob = 0.0
    if not (0 < min_backspaces <= max_backspaces):
        print(f"[backend] Warning: Invalid backspace counts for '{name}'. Using defaults.")
        min_backspaces, max_backspaces = 1, 3
    if not text:
        print(f"[backend] Snippet '{name}' has no text to type.")
        return

    # --- Typing Thread ---
    def type_text_worker():
        typed_buffer = ""  # Keep track of what's been typed in this execution
        print(f"[backend] Starting typing for '{name}'...")
        try:
            for char in text:
                # --- Backspace Simulation ---
                if backspace_prob > 0 and random.random() < backspace_prob and len(typed_buffer) > 0:
                    try:
                        # Ensure max_backspaces isn't more than what's typed
                        effective_max_backspaces = min(max_backspaces, len(typed_buffer))
                        # Ensure min_backspaces isn't more than effective_max_backspaces and is at least 1
                        effective_min_backspaces = min(min_backspaces, effective_max_backspaces)
                        if effective_min_backspaces > 0 and effective_min_backspaces <= effective_max_backspaces:
                            num_backspaces = random.randint(effective_min_backspaces, effective_max_backspaces)
                            # print(f"[backend] Backspacing {num_backspaces} chars...")  # Debug log
                            # Get the characters that will be deleted *before* simulating backspaces
                            deleted_chars = typed_buffer[-num_backspaces:]
                            # Simulate backspaces
                            for _ in range(num_backspaces):
                                keyboard.press_and_release('backspace')  # Use press_and_release for compatibility
                                time.sleep(random.uniform(0.03, 0.07))  # Small delay for realism
                            # Update typed_buffer to reflect backspaces
                            typed_buffer = typed_buffer[:-num_backspaces]
                            # Log the backspace action with deleted characters
                            print(f"[backend] Simulated backspace x{num_backspaces}, deleted: '{deleted_chars}'")
                            
                            # Retype the deleted characters with a slight delay
                            time.sleep(random.uniform(0.1, 0.3))  # Pause before retyping (like a human thinking)
                            for deleted_char in deleted_chars:
                                keyboard.write(deleted_char)
                                typed_buffer += deleted_char
                                time.sleep(random.uniform(min_delay, max_delay))
                            
                            # Continue with the current character after retyping
                    except Exception as e:
                        print(f"[backend] Error simulating backspace: {e}")
                # --- Type the Character ---
                keyboard.write(char)
                typed_buffer += char
                time.sleep(random.uniform(min_delay, max_delay))
            print(f"[backend] Finished typing for '{name}'.")
        except Exception as e:
            print(f"[backend] Error during typing: {e}")
        finally:
            save_history(name, text, datetime.now().isoformat())  # Save history even if errors occur

    # Start typing in a separate thread to prevent UI freezing
    Thread(target=type_text_worker, daemon=True).start()


# --- History ---

def load_history():
    """Loads history from the JSON file."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"[backend] Error loading history: {e}")
        return []

def save_history(snippet_name, typed_text, timestamp):
     """Saves a history entry to the JSON file, limiting the history size."""
     history = load_history()
     history.insert(0, {"snippet_name": snippet_name, "typed_text": typed_text, "timestamp": timestamp})
     # Keep only the last 100 entries (or a reasonable limit) to prevent the history file from growing indefinitely
     history = history[:100]  
     try:
         with open(HISTORY_FILE, "w", encoding="utf-8") as f:
             json.dump(history, f, indent=2, ensure_ascii=False)
     except IOError as e:
         print(f"[backend] Error saving history: {e}")


def get_history():
    """Returns the typing history."""
    return load_history()

def clear_history():
    """Clears the typing history."""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)  # Save an empty list to clear the file
        print("[backend] Typing history cleared.")
        return True
    except IOError as e:
        print(f"[backend] Error clearing history: {e}")
        return False

# --- Import/Export ---

def import_snippets(path):
    """Imports snippets from a JSON file, merging with existing ones."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            imported_data = json.load(f)
            if not isinstance(imported_data, dict):
                print(f"[backend] Error: Invalid format in import file '{path}'. Expected a JSON object.")
                return None
            return imported_data
    except (json.JSONDecodeError, IOError, FileNotFoundError) as e:
        print(f"[backend] Error importing snippets from '{path}': {e}")
        return None


def export_snippets(path, snippets_to_export):
    """Exports the current snippets to a specified JSON file path."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(snippets_to_export, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        print(f"[backend] Error exporting snippets to '{path}': {e}")
        return False

def clear_all_snippets():
    """Clears all snippets."""

    try:
        with open(SNIPPETS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2)  # Save an empty object to clear the file
        print("[backend] All snippets cleared.")
        return True
    except IOError as e:
        print(f"[backend] Error clearing snippets: {e}")
        return False

# --- Misc ---

def check_for_update():
    """Dummy placeholder for checking updates."""
    # In a real app, this would involve network requests, version comparison, etc.
    return "Auto Typing App (v1.1 - Backspace Feature)"

# --- Main Execution Guard (Optional but good practice) ---
if __name__ == "__main__":
    # This block runs if the script is executed directly
    # You could put test code or initialization logic here if needed
    print("[backend] Backend script loaded. Ready to be used by frontend.")
    # Example: Load snippets on direct run to check for errors
    # initial_snippets = load_snippets()
    # print(f"[backend] Loaded {len(initial_snippets)} snippets on start.")
    # register_hotkeys(initial_snippets) # Register if running standalone? Maybe not desired.
    # keyboard.wait() # Keep the script running if you want to test hotkeys
