import keyboard
import sys

print("--- Keyboard Mapping Diagnostic ---")
print("This script checks how the 'keyboard' library maps specific characters on your system.")

chars_to_test = ['{', '}', '#', '<', '>', '[', ']', ';', ':', '.', ',']

print(f"Testing characters: {' '.join(chars_to_test)}")

for char in chars_to_test:
    try:
        # key_to_scan_codes returns a specific data structure depending on OS
        # On Linux it returns a list of (scan_code, modifiers) tuples
        scan_codes = keyboard.key_to_scan_codes(char)
        print(f"['{char}']MAPS TO: {scan_codes}")
        
        # Check if it looks like a valid mapping
        if not scan_codes:
             print(f"  -> WARNING: Empty mapping (will likely fall back to unicode)")
             
    except ValueError:
        print(f"['{char}'] NO MAPPING FOUND (will use Unicode Fallback)")
    except Exception as e:
        print(f"['{char}'] ERROR: {e}")

print("\nIf you see 'NO MAPPING FOUND' or empty mappings, 'keyboard' cannot find these keys on your current layout.")
