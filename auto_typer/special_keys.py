"""
Special keys mapping module for Auto Typer.
This provides mapping between characters and their keyboard simulation methods.
"""

from typing import Protocol, Union
import time
import platform
import keyboard as kb

class KeyboardController(Protocol):
    """Protocol defining the expected keyboard controller interface.
    
    The keyboard library accepts both string key names (e.g. 'shift') and
    integer scan codes, so key parameters are typed as Union[str, int].
    """
    def press(self, key: Union[str, int]) -> None: ...
    def release(self, key: Union[str, int]) -> None: ...
    def press_and_release(self, key: Union[str, int]) -> None: ...
    def write(self, text: str, delay: float = 0) -> None: ...

# Linux input event codes (from linux/input-event-codes.h)
# These are the raw scan codes used by the kernel
LINUX_SCAN_CODES = {
    '-': 12, '=': 13,
    '[': 26, ']': 27,
    ';': 39, "'": 40,
    '`': 41, '\\': 43,
    ',': 51, '.': 52, '/': 53,
    ' ': 57,
    '\n': 28, '\r': 28,
    '\t': 15, '\b': 14
}

# Mapping for shifted symbols to their base character scan code
LINUX_SHIFT_MAP = {
    '_': '-', '+': '=',
    '{': '[', '}': ']',
    ':': ';', '"': "'",
    '~': '`', '|': '\\',
    '<': ',', '>': '.', '?': '/',
    '!': '1', '@': '2', '#': '3', '$': '4',
    '%': '5', '^': '6', '&': '7', '*': '8',
    '(': '9', ')': '0'
}

# Base keys for numbers (needed for shift map above)
LINUX_NUM_CODES = {
    '1': 2, '2': 3, '3': 4, '4': 5, '5': 6,
    '6': 7, '7': 8, '8': 9, '9': 10, '0': 11
}

def type_character(keyboard: KeyboardController, char: str) -> bool:
    """
    Types a single character. On Linux, it uses explicit scan codes for symbols
    to avoid mapping issues. On other OSs, it falls back to standard methods.
    
    Args:
        keyboard (KeyboardController): The keyboard controller implementation
        char (str): The character to type
        
    Returns:
        bool: True if successful, False if failed
    """
    try:
        is_linux = platform.system() == "Linux"
        
        if is_linux:
            # 1. Handle shifted symbols specifically
            if char in LINUX_SHIFT_MAP:
                base_char = LINUX_SHIFT_MAP[char]
                scan_code = 0
                
                # Resolving scan code for base char
                if base_char in LINUX_SCAN_CODES:
                    scan_code = LINUX_SCAN_CODES[base_char]
                elif base_char in LINUX_NUM_CODES:
                    scan_code = LINUX_NUM_CODES[base_char]
                
                if scan_code > 0:
                    try:
                        keyboard.press('shift')
                        time.sleep(0.05)
                        keyboard.press_and_release(scan_code)
                        time.sleep(0.05)
                        keyboard.release('shift')
                        return True
                    except Exception as e:
                        print(f"[special_keys] Linux shift typing error: {e}")
                        try: keyboard.release('shift') 
                        except: pass
            
            # 2. Handle unshifted symbols
            if char in LINUX_SCAN_CODES:
                try:
                    keyboard.press_and_release(LINUX_SCAN_CODES[char])
                    return True
                except Exception as e:
                    print(f"[special_keys] Linux symbol typing error: {e}")

        # 3. Fallback for everything else (letters, numbers, non-Linux OS)
        keyboard.write(char)
        return True
            
    except Exception as e:
        print(f"[special_keys] Error typing character '{char}': {e}")
        return False
