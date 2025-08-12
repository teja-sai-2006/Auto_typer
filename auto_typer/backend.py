# Note: This script requires the 'keyboard' library, which may need administrative privileges (e.g., running as Administrator on Windows) to register global hotkeys system-wide. [cite: 18]
import json
import os
import time
import keyboard
from datetime import datetime
import random  # Added for backspace probability
from threading import Thread
from datetime import datetime
from typing import TypedDict, Optional, Dict, List, Any, Callable

class SnippetData(TypedDict):
    text: str
    min_delay: float
    max_delay: float
    backspace_probability: float
    min_backspaces: int
    max_backspaces: int
    hotkey: str
    uppercase: bool
    lowercase: bool
    remove_spaces: bool
    remove_symbols: bool
    keep_alphanumeric_spaces: bool

class HistoryEntry(TypedDict):
    snippet_name: str
    typed_text: str
    timestamp: str

SnippetsDict = Dict[str, SnippetData]

def type_character_safely(char: str) -> bool:
    """Type a single character safely and reliably."""
    if not char:
        return True
    
    try:
        # Small delay before typing to ensure readiness
        time.sleep(0.05)
        
        if char == ' ':
            keyboard.press_and_release('space')
        elif char == '\n' or char == '\r':
            keyboard.press_and_release('enter')
        elif char == '\t':
            keyboard.press_and_release('tab')
        elif char.isupper():
            # More reliable uppercase handling with explicit key presses
            try:
                keyboard.press('shift')
                time.sleep(0.05)  # Increased delay for more reliable shift press
                keyboard.press_and_release(char.lower())  # Use lowercase with shift held
                time.sleep(0.05)  # Increased delay before releasing shift
                keyboard.release('shift')
                time.sleep(0.03)  # Additional delay after releasing shift
            except Exception as e:
                print(f"[backend] Error in uppercase handling: {e}, trying fallback")
                # Fallback method for uppercase
                keyboard.write(char)
        else:
            # For all other characters, use write for better compatibility
            keyboard.write(char)
        
        # Always add a small delay after typing
        time.sleep(0.05)
        return True
    except Exception as e:
        print(f"[backend] Error typing character '{char}': {e}")
        return False
# Define type for type_character function
from typing import Callable, Any

# For type checking purposes only
from typing import Protocol

class KeyboardModule(Protocol):
    def press(self, hotkey: Any) -> None: ...
    def release(self, hotkey: Any) -> None: ...
    def press_and_release(self, hotkey: Any, do_press: bool = ..., do_release: bool = ...) -> None: ...

type_character_type = Callable[[KeyboardModule, str], bool]
type_character: Optional[type_character_type] = None
special_keys_available: bool = False

try:
    from special_keys import type_character as tc  # Import special keys handling
    type_character = tc  # type: ignore
    special_keys_available = True
except ImportError:
    print("[backend] special_keys.py module not found. Using fallback typing methods.")

# Get the directory where this script (backend.py) is located
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = os.path.join(BACKEND_DIR, "resources")

# Make sure the resources directory exists
if not os.path.exists(RESOURCES_DIR):
    os.makedirs(RESOURCES_DIR)

# Define file paths in the resources directory
SNIPPETS_FILE = os.path.join(RESOURCES_DIR, "snippets.json")
HISTORY_FILE = os.path.join(RESOURCES_DIR, "history.json")

# --- Snippet Loading/Saving ---

def load_snippets() -> SnippetsDict:
    """Loads snippets from the JSON file."""
    if not os.path.exists(SNIPPETS_FILE):
        # Create an empty snippets file if it doesn't exist
        try:
            with open(SNIPPETS_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=2)
        except IOError as e:
            print(f"[backend] Error creating snippets file: {e}")
        return {}
    try:
        with open(SNIPPETS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"[backend] Error loading snippets: {e}")
        return {}

def save_snippets(snippets: SnippetsDict) -> bool:
    """Saves snippets to the JSON file."""
    # Ensure resources directory exists
    if not os.path.exists(RESOURCES_DIR):
        try:
            os.makedirs(RESOURCES_DIR)
        except Exception as e:
            print(f"[backend] Error creating resources directory: {e}")
            return False

    temp_file = SNIPPETS_FILE + '.tmp'
    try:
        # Create a temporary file first
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(snippets, f, indent=2, ensure_ascii=False)  # Use ensure_ascii=False for broader character support

        # If writing to temp file was successful, rename it to the actual file
        os.replace(temp_file, SNIPPETS_FILE)
        print(f"[backend] Successfully saved snippets to {SNIPPETS_FILE}")
        return True
    except IOError as e:
        print(f"[backend] Error saving snippets: {e}")
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)  # Clean up temp file if it exists
            except:
                pass
        return False

# --- Hotkey Handling ---

def normalize_hotkey(hotkey_str: str) -> str:
    """Normalizes hotkey string parts (e.g., 'control' to 'ctrl')."""
    replacements: Dict[str, str] = {
        "control": "ctrl",
        "control_l": "ctrl",
        "control_r": "ctrl",
        "alt_l": "alt",
        "alt_r": "alt",
        "shift_l": "shift",
        "shift_r": "shift",
        "win": "windows",  # Added for windows key if needed
        "command": "cmd",  # Added for mac command key if needed
        "option": "alt",  # Mac option key alias
        "escape": "esc",  # Common alias
        "pagedown": "pgdn",  # Common alias
        "page up": "pgup",  # Common alias
        "insert": "ins",  # Common alias
        "delete": "del",  # Common alias
        "print screen": "print_screen",  # Common alias
        "scroll lock": "scroll_lock",  # Common alias
        "caps lock": "caps_lock",  # Common alias
        "num lock": "num_lock",  # Common alias
        "pause": "pause break",  # Common alias
        "break": "pause break",  # Common alias
    }
    # Standardize separators and handle potential extra spaces
    parts: List[str] = hotkey_str.lower().replace(" ", "").replace("-", "+").split("+")  # Handle both space and hyphen as separators
    
    # Process parts with replacements and filter out any empty values
    processed_parts: List[str] = []
    for p in parts:
        if p:  # Skip empty parts
            processed_parts.append(replacements.get(p, p))
    
    # Common modifiers first, then other keys
    modifier_order: List[str] = ['ctrl', 'shift', 'alt', 'windows', 'cmd']
    # Create a set to remove duplicates, then sort with modifiers first
    sorted_parts: List[str] = sorted(set(processed_parts), key=lambda x: (x not in modifier_order, modifier_order.index(x) if x in modifier_order else len(modifier_order), x))

    return "+".join(sorted_parts)


from typing import Any
registered_hotkeys: List[Any] = []  # Store handles to remove later

def register_hotkeys(snippets: SnippetsDict) -> None:
    """Registers hotkeys for all snippets.
    
    Args:
        snippets (SnippetsDict): The dictionary of snippets to register hotkeys for
    """
    global registered_hotkeys
    for handle in registered_hotkeys:
        try:
            keyboard.remove_hotkey(handle)
        except Exception as e:
            # This can happen if the hotkey was already removed or invalid
            # print(f"[backend] Info: Could not remove hotkey handle: {e}") # Optional: log if needed
            pass # Continue trying to remove others
    registered_hotkeys.clear()
    print("[backend] Cleared previous hotkeys.")
    
    # Setup system hotkeys for control
    try:
        setup_system_hotkeys()
    except Exception as e:
        print(f"[backend] Warning: Could not register system hotkeys: {e}")

            # Register new hotkeys
    count = 0
    for name, data in snippets.items():
        hotkey = data.get("hotkey", "").strip()
        if not hotkey:
            continue

        try:
            hotkey_norm = normalize_hotkey(hotkey)
            if not hotkey_norm:  # Skip if normalization results in empty string
                print(f"[backend] Warning: Skipping empty normalized hotkey for snippet '{name}' (original: '{hotkey}')")
                continue

            # Create a local copy with explicit type and function for execution
            snippet_name: str = name
            def execute_with_delay(n: str = snippet_name) -> None:
                time.sleep(0.1)
                execute_snippet(n)

            handle = keyboard.add_hotkey(
                hotkey_norm, 
                lambda: Thread(target=execute_with_delay, daemon=True).start(),
                trigger_on_release=False
            )
            registered_hotkeys.append(handle)
            count += 1
            print(f"[backend] Registered hotkey '{hotkey_norm}' for '{name}'")

        except (ValueError, Exception) as e:
            print(f"[backend] Error: Could not register hotkey '{hotkey}' for snippet '{name}': {e}")

    print(f"[backend] Registered {count} hotkeys.")
# --- Global Control Variables ---
typing_paused: bool = False
typing_stopped: bool = False

# --- Default System Hotkeys ---
def setup_system_hotkeys():
    """Sets up system-wide default hotkeys for controlling typing."""
    try:
        # Register CTRL+Space to pause/resume typing
        keyboard.add_hotkey('ctrl+space', toggle_pause_typing)
        # Register CTRL+Esc to stop typing completely
        keyboard.add_hotkey('ctrl+esc', stop_typing)
        print("[backend] System hotkeys registered successfully.")
    except Exception as e:
        print(f"[backend] Error registering system hotkeys: {e}")

def toggle_pause_typing() -> None:
    """Toggles the pause state of typing."""
    global typing_paused
    typing_paused = not typing_paused
    print(f"[backend] Typing {'paused' if typing_paused else 'resumed'}.")

def stop_typing() -> None:
    """Stops typing completely."""
    global typing_stopped
    typing_stopped = True
    print("[backend] Typing stopped.")

# --- Text Manipulation Functions ---
def apply_text_transformations(text: str, transformations: Optional[Dict[str, bool]] = None) -> str:
    """Applies specified text transformations."""
    if not transformations:
        return text
    
    result = text
    
    # Only apply transformations if they are explicitly set to True
    if transformations.get("uppercase") is True:
        result = result.upper()
    elif transformations.get("lowercase") is True:
        result = result.lower()
    
    # Remove spaces only if explicitly requested
    if transformations.get("remove_spaces") is True:
        result = result.replace(" ", "")
    
    # Remove symbols only if explicitly requested
    if transformations.get("remove_symbols") is True:
        import re
        result = re.sub(r'[^\w\s]', '', result)
    
    # Keep only spaces and alphanumerics only if explicitly requested
    if transformations.get("keep_alphanumeric_spaces") is True:
        import re
        result = re.sub(r'[^\w\s]', '', result)
    
    return result

# --- Snippet Execution ---

def execute_snippet(name: str) -> None:
    """Executes the typing sequence for a given snippet name.
    
    Args:
        name (str): The name of the snippet to execute
    """
    global typing_paused, typing_stopped
    typing_paused = False
    typing_stopped = False
    
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
    
    # Get text transformations
    transformations = {
        "uppercase": snippet.get("uppercase", False),
        "lowercase": snippet.get("lowercase", False),
        "remove_spaces": snippet.get("remove_spaces", False),
        "remove_symbols": snippet.get("remove_symbols", False),
        "keep_alphanumeric_spaces": snippet.get("keep_alphanumeric_spaces", False)
    }
    
    # Apply text transformations
    text = apply_text_transformations(text, transformations)

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
        # Declare globals inside nested function
        global typing_paused, typing_stopped
        
        typed_buffer = ""  # Keep track of what's been typed in this execution
        print(f"[backend] Starting typing for '{name}'...")
        print("[backend] Use CTRL+Space to pause/resume, CTRL+Esc to stop typing completely")
        try:
            for char in text:
                # Check if typing has been completely stopped
                if typing_stopped:
                    print("[backend] Typing stopped by user.")
                    break
                
                # Check if typing is paused and wait until unpaused
                while typing_paused and not typing_stopped:
                    time.sleep(0.1)  # Check every 100ms
                    continue
                
                # If stopped while paused, break out
                if typing_stopped:
                    print("[backend] Typing stopped by user while paused.")
                    break
                
                # --- Backspace Simulation ---
                if backspace_prob > 0 and random.random() < backspace_prob and len(typed_buffer) > 0:
                    try:
                        # Ensure max_backspaces isn't more than what's typed
                        effective_max_backspaces = min(max_backspaces, len(typed_buffer))
                        # Ensure min_backspaces isn't more than effective_max_backspaces and is at least 1
                        effective_min_backspaces = min(min_backspaces, effective_max_backspaces)
                        if effective_min_backspaces > 0 and effective_min_backspaces <= effective_max_backspaces:
                            num_backspaces = random.randint(effective_min_backspaces, effective_max_backspaces)
                            # Get the characters that will be deleted *before* simulating backspaces
                            deleted_chars = typed_buffer[-num_backspaces:]
                            print(f"[backend] Backspace simulation triggered. Will delete and retype: '{deleted_chars}'")
                            
                            # Simulate backspaces with improved handling
                            successful_backspaces = 0
                            for _ in range(num_backspaces):
                                if typing_stopped:
                                    break
                                    
                                while typing_paused and not typing_stopped:
                                    time.sleep(0.1)
                                    continue
                                
                                try:
                                    # Most reliable way to press backspace
                                    keyboard.press_and_release('backspace')  # Use press_and_release for compatibility
                                    successful_backspaces += 1
                                    time.sleep(random.uniform(0.03, 0.07))  # Small delay for realism
                                except Exception as e:
                                    print(f"[backend] Error pressing backspace: {str(e)}")
                                    # Try alternative method
                                    try:
                                        keyboard.write("\b")  # Try alternative backspace method
                                        successful_backspaces += 1
                                        time.sleep(random.uniform(0.03, 0.07))
                                    except Exception as e2:
                                        print(f"[backend] All backspace methods failed: {str(e2)}")
                            
                            if typing_stopped:
                                break
                                
                            # Update typed_buffer to reflect only the successful backspaces
                            if successful_backspaces > 0:
                                # Only delete the characters that were actually backspaced
                                typed_buffer = typed_buffer[:-successful_backspaces]
                                # Update deleted_chars to only include characters that were actually deleted
                                deleted_chars = deleted_chars[-successful_backspaces:]
                                # Log the backspace action with deleted characters
                                print(f"[backend] Simulated backspace x{successful_backspaces}, deleted: '{deleted_chars}'")
                            
                            # Retype the deleted characters with a slight delay
                            time.sleep(random.uniform(0.1, 0.3))  # Pause before retyping (like a human thinking)
                            print(f"[backend] Now retyping deleted characters: '{deleted_chars}'")
                            
                            # Retype each deleted character individually
                            for deleted_char in deleted_chars:
                                if typing_stopped:
                                    break
                                    
                                while typing_paused and not typing_stopped:
                                    time.sleep(0.1)
                                    continue
                                
                                try:
                                    # Try using our special keys module first if available
                                    if type_character and special_keys_available:
                                        if type_character(keyboard, deleted_char):
                                            print(f"[backend] Retyped character using special_keys module: '{deleted_char}'")
                                            typed_buffer += deleted_char
                                        else:
                                            # Fall back to our own handling if special_keys fails
                                            raise Exception("Special keys typing failed for retyping, using fallback")
                                    else:
                                        # Handle special characters first
                                        if deleted_char == ' ':
                                            keyboard.press_and_release('space')
                                            print(f"[backend] Retyped space character")
                                            typed_buffer += deleted_char
                                        elif deleted_char == '\n' or deleted_char == '\r':
                                            keyboard.press_and_release('enter')
                                            print(f"[backend] Retyped newline character")
                                            typed_buffer += deleted_char
                                        elif deleted_char == '\t':
                                            keyboard.press_and_release('tab')
                                            print(f"[backend] Retyped tab character")
                                            typed_buffer += deleted_char
                                        elif deleted_char.isupper():
                                            # Special handling for uppercase letters
                                            keyboard.press('shift')
                                            time.sleep(0.03)
                                            keyboard.press_and_release(deleted_char.lower())
                                            time.sleep(0.03)
                                            keyboard.release('shift')
                                            print(f"[backend] Retyped uppercase character: '{deleted_char}'")
                                            typed_buffer += deleted_char
                                        else:
                                            # First attempt: Use keyboard.write which works well for most characters
                                            keyboard.write(deleted_char)
                                            print(f"[backend] Retyped character: '{deleted_char}'")
                                            typed_buffer += deleted_char
                                    
                                    # Add a small delay between characters
                                    time.sleep(random.uniform(min_delay, max_delay))
                                except Exception as e:
                                    print(f"[backend] Error retyping character '{deleted_char}': {str(e)}")
                                    # Second attempt: Try press_and_release which works better for some keys
                                    try:
                                        if deleted_char.isupper():
                                            # Try alternative method for uppercase with explicit shift
                                            keyboard.press('shift')
                                            time.sleep(0.03)
                                            keyboard.press_and_release(deleted_char.lower())
                                            time.sleep(0.03)
                                            keyboard.release('shift')
                                            print(f"[backend] Retyped uppercase character (fallback 1): '{deleted_char}'")
                                        else:
                                            keyboard.press_and_release(deleted_char)
                                            print(f"[backend] Retyped character (fallback method 1): '{deleted_char}'")
                                        typed_buffer += deleted_char
                                        time.sleep(random.uniform(min_delay, max_delay))
                                    except Exception as e2:
                                        print(f"[backend] Error with fallback method 1: {str(e2)}")
                                        # Third attempt: Try simulating the keypresses one by one
                                        try:
                                            # For more complex characters, try this
                                            if deleted_char.isupper():
                                                # For uppercase, manually simulate shift
                                                keyboard.press('shift')
                                                time.sleep(0.03)
                                                keyboard.press_and_release(deleted_char.lower())
                                                time.sleep(0.03)
                                                keyboard.release('shift')
                                                print(f"[backend] Retyped uppercase character (fallback 2): '{deleted_char}'")
                                            else:
                                                keyboard.press(deleted_char)
                                                time.sleep(0.03)
                                                keyboard.release(deleted_char)
                                                print(f"[backend] Retyped character (fallback method 2): '{deleted_char}'")
                                            typed_buffer += deleted_char
                                            time.sleep(random.uniform(min_delay, max_delay))
                                        except Exception as e3:
                                            print(f"[backend] All retyping methods failed for '{deleted_char}': {str(e3)}")
                            
                            if typing_stopped:
                                break
                    except Exception as e:
                        print(f"[backend] Error simulating backspace: {e}")
                
                if typing_stopped:
                    break
                
                    # --- Type the Character ---
                if type_character_safely(char):
                    typed_buffer += char
                    print(f"[backend] Successfully typed character: '{char}'")
                    # Add random delay between characters for natural typing
                    time.sleep(random.uniform(min_delay, max_delay))
                else:
                    print(f"[backend] Failed to type character: '{char}', trying direct method...")
                    # Fallback to direct typing method
                    try:
                        keyboard.write(char)
                        typed_buffer += char
                        time.sleep(0.05)  # Fixed delay for direct method
                        # Add random delay between characters
                        time.sleep(random.uniform(min_delay, max_delay))
                    except Exception as e:
                        print(f"[backend] Direct typing failed for '{char}': {e}")
                        # Second attempt: Try press_and_release which works better for some keys
                        try:
                            if char.isupper():
                                # Try alternative method for uppercase with explicit shift
                                keyboard.press('shift')
                                time.sleep(0.03)
                                keyboard.press_and_release(char.lower())
                                time.sleep(0.03)
                                keyboard.release('shift')
                                print(f"[backend] Typed uppercase character (fallback 1): '{char}'")
                            else:
                                keyboard.press_and_release(char)
                                print(f"[backend] Typed character (fallback method 1): '{char}'")
                            typed_buffer += char
                            time.sleep(random.uniform(min_delay, max_delay))
                        except Exception as e2:
                            print(f"[backend] Error with fallback method 1: {str(e2)}")
                            # Third attempt: Try other approach for this character
                            try:
                                # Last resort - try write method with just this character
                                if char.isupper():
                                    # For uppercase, manually simulate shift press and release
                                    keyboard.press('shift')
                                    time.sleep(0.03)
                                    keyboard.press_and_release(char.lower())
                                    time.sleep(0.03)
                                    keyboard.release('shift')
                                    print(f"[backend] Typed uppercase character (fallback 2): '{char}'")
                                else:
                                    # For more complex characters, try this
                                    keyboard.press(char)
                                    time.sleep(0.03)
                                    keyboard.release(char)
                                    print(f"[backend] Typed character (fallback method 2): '{char}'")
                                typed_buffer += char
                                time.sleep(random.uniform(min_delay, max_delay))
                            except Exception as e3:
                                print(f"[backend] All typing methods failed for '{char}': {str(e3)}")
                            if typing_stopped:
                                print("[backend] Typing was manually stopped by user.")
                                break
            else:
                print(f"[backend] Finished typing for '{name}'.")
        except Exception as e:
            print(f"[backend] Error during typing: {str(e)}")
            import traceback
            traceback.print_exc()  # Print full stack trace for debugging
        finally:
            # Reset control flags
            typing_paused = False
            typing_stopped = False
            try:
                save_history(name, text, datetime.now().isoformat())  # Save history even if errors occur
            except Exception as e:
                print(f"[backend] Error saving history: {str(e)}")

    # Start typing in a separate thread to prevent UI freezing
    Thread(target=type_text_worker, daemon=True).start()


# --- History ---

def load_history() -> List[HistoryEntry]:
    """Loads history from the JSON file."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"[backend] Error loading history: {e}")
        return []

def save_history(snippet_name: str, typed_text: str, timestamp: str) -> None:
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


def get_history() -> List[HistoryEntry]:
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

def import_snippets(path: str) -> Optional[SnippetsDict]:
    """Imports snippets from a JSON file, merging with existing ones.
    
    Args:
        path (str): The path to the JSON file containing snippets to import
    
    Returns:
        Optional[SnippetsDict]: The imported snippets, or None if import fails
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            imported_data = json.load(f)
            if not isinstance(imported_data, dict):
                print(f"[backend] Error: Invalid format in import file '{path}'. Expected a JSON object.")
                return None
            # Cast the imported data to SnippetsDict
            snippets: SnippetsDict = imported_data  # type: ignore
            return snippets
    except (json.JSONDecodeError, IOError, FileNotFoundError) as e:
        print(f"[backend] Error importing snippets from '{path}': {e}")
        return None


def export_snippets(path: str, snippets_to_export: SnippetsDict) -> bool:
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

def check_for_update() -> str:
    """Dummy placeholder for checking updates."""
    # In a real app, this would involve network requests, version comparison, etc.
    return "Auto Typing App (v1.2 - Backspace Feature)"

# --- Main Execution Guard (Optional but good practice) ---
if __name__ == "__main__":
    # This block runs if the script is executed directly
    print("[backend] Backend script loaded. Ready to be used by frontend.")
    
    # Setup system hotkeys for control
    setup_system_hotkeys()
    
    # Example: Load snippets on direct run to check for errors
    initial_snippets = load_snippets()
    print(f"[backend] Loaded {len(initial_snippets)} snippets on start.")
    register_hotkeys(initial_snippets) # Register hotkeys when running standalone
    
    # Keep the script running to test hotkeys
    print("[backend] Press Ctrl+C to exit")
    try:
        keyboard.wait() 
    except KeyboardInterrupt:
        print("[backend] Exiting...")
        # Clean up before exit if needed
    except Exception as e:
        print(f"[backend] Error: {e}")
