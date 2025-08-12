"""
Special keys mapping module for Auto Typer.
This provides mapping between characters and their keyboard simulation methods.
"""

from typing import Protocol
import time  # Add time module for sleep function

class KeyboardController(Protocol):
    """Protocol defining the expected keyboard controller interface."""
    def press(self, key: str) -> None: ...
    def release(self, key: str) -> None: ...
    def press_and_release(self, key: str) -> None: ...

# Dictionary mapping special characters to their shift+key combinations
SHIFT_CHAR_MAP = {
    # Common shifted characters on a US keyboard
    '!': ('1', True),  # shift+1
    '@': ('2', True),  # shift+2
    '#': ('3', True),  # shift+3
    '$': ('4', True),  # shift+4
    '%': ('5', True),  # shift+5
    '^': ('6', True),  # shift+6
    '&': ('7', True),  # shift+7
    '*': ('8', True),  # shift+8
    '(': ('9', True),  # shift+9
    ')': ('0', True),  # shift+0
    '_': ('-', True),  # shift+-
    '+': ('=', True),  # shift+=
    '{': ('[', True),  # shift+[
    '}': (']', True),  # shift+]
    '|': ('\\', True), # shift+\
    ':': (';', True),  # shift+;
    '"': ("'", True),  # shift+'
    '<': (',', True),  # shift+,
    '>': ('.', True),  # shift+.
    '?': ('/', True),  # shift+/
    '~': ('`', True),  # shift+`
}

# Special key mapping for non-printable or complex keys
SPECIAL_KEY_MAP = {
    '\n': 'enter',
    '\r': 'enter',
    '\t': 'tab',
    ' ': 'space',
    '\b': 'backspace',
}

def get_key_combination(char: str) -> tuple[str, bool]:
    """
    Returns the keyboard key combination needed to type a character.
    
    Args:
        char (str): The character to type
        
    Returns:
        tuple: (key, needs_shift) where:
            - key is the base key to press
            - needs_shift is True if shift should be held down
    """
    # Handle uppercase letters
    if char.isupper():
        return (char.lower(), True)
    
    # Check if it's a special character that needs shift
    if char in SHIFT_CHAR_MAP:
        return SHIFT_CHAR_MAP[char]
    
    # Check if it's a special key
    if char in SPECIAL_KEY_MAP:
        return (SPECIAL_KEY_MAP[char], False)
    
    # Regular character
    return (char, False)

def type_character(keyboard: KeyboardController, char: str) -> bool:
    """
    Types a single character using the keyboard module.
    
    Args:
        keyboard (KeyboardController): The keyboard controller implementation
        char (str): The character to type
        
    Returns:
        bool: True if successful, False if failed
    """
    try:
        key, needs_shift = get_key_combination(char)
        
        if needs_shift:
            keyboard.press('shift')
            time.sleep(0.03)
            keyboard.press_and_release(key)
            time.sleep(0.03)
            keyboard.release('shift')
        else:
            keyboard.press_and_release(key)
        return True
    except Exception as e:
        print(f"[special_keys] Error typing character '{char}': {e}")
        return False
