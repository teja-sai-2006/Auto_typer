#!/usr/bin/env python3

"""
Enhanced test script to validate keyboard input and backspace retyping functionality
"""

import time
import random
import keyboard
import sys

def test_uppercase_typing():
    """Tests uppercase letter typing with improved shift handling"""
    print("\n=== Testing Uppercase Letters ===")
    print("Waiting 3 seconds before typing uppercase letters...")
    time.sleep(3)
    
    uppercase_text = "HELLO WORLD THIS IS A TEST"
    print(f"\nTyping text: '{uppercase_text}'")
    
    # Add a newline before starting
    keyboard.press_and_release('enter')
    time.sleep(0.5)  # Wait a bit after newline
    
    for char in uppercase_text:
        if char == ' ':
            keyboard.press_and_release('space')
            time.sleep(0.1)  # Consistent timing for spaces
        else:
            # Improved uppercase handling with better timing
            keyboard.press('shift')
            time.sleep(0.05)  # Increased delay for shift
            keyboard.press_and_release(char.lower())
            time.sleep(0.05)  # Increased delay before releasing shift
            keyboard.release('shift')
            time.sleep(0.05)  # Additional delay after character
        
    # Add a newline at the end
    time.sleep(0.5)  # Wait before newline
    keyboard.press_and_release('enter')
    print("\nUppercase test completed!")

def test_mixed_case_typing():
    """Tests mixed case typing with improved character handling"""
    print("\n=== Testing Mixed Case Text ===")
    print("Waiting 3 seconds before typing mixed case text...")
    time.sleep(3)
    
    mixed_text = "Hello World! This is a Test with Mixed Case."
    print(f"\nTyping text: '{mixed_text}'")
    
    # Add a newline before starting
    keyboard.press_and_release('enter')
    time.sleep(0.5)  # Wait a bit after newline
    
    for char in mixed_text:
        if char == ' ':
            keyboard.press_and_release('space')
            time.sleep(0.1)  # Consistent timing for spaces
        elif char == '!':
            keyboard.press('shift')
            time.sleep(0.05)  # Increased delay for shift
            keyboard.press_and_release('1')
            time.sleep(0.05)  # Increased delay before releasing shift
            keyboard.release('shift')
            time.sleep(0.05)  # Additional delay after character
        elif char.isupper():
            keyboard.press('shift')
            time.sleep(0.05)  # Increased delay for shift
            keyboard.press_and_release(char.lower())
            time.sleep(0.05)  # Increased delay before releasing shift
            keyboard.release('shift')
            time.sleep(0.05)  # Additional delay after character
        else:
            keyboard.write(char)
            time.sleep(0.05)  # Consistent timing for regular characters
        
    # Add a newline at the end
    time.sleep(0.5)  # Wait before newline
    keyboard.press_and_release('enter')
    print("\nMixed case test completed!")

def test_backspace_retyping():
    """Simulates the backspace retyping logic from the main application"""
    print("\n=== Testing Backspace Retyping ===")
    print("Will type characters, backspace some, then retype them")
    print("Waiting 3 seconds before starting...")
    time.sleep(3)
    
    # Sample text with uppercase and special characters
    text = "This IS a TEST of BACKSPACE retyping!"
    typed_buffer = ""
    
    # Add a newline before starting
    keyboard.press_and_release('enter')
    time.sleep(0.5)  # Wait a bit after newline
    
    print(f"\nTyping initial text (first 20 chars): '{text[:20]}'")
    
    # Type the initial characters
    for char in text[:20]:  # Type first 20 characters
        if char == ' ':
            keyboard.press_and_release('space')
            time.sleep(0.1)  # Consistent timing for spaces
        elif char == '!':
            keyboard.press('shift')
            time.sleep(0.05)  # Increased delay for shift
            keyboard.press_and_release('1')
            time.sleep(0.05)  # Increased delay before releasing shift
            keyboard.release('shift')
            time.sleep(0.05)  # Additional delay after character
        elif char.isupper():
            keyboard.press('shift')
            time.sleep(0.05)  # Increased delay for shift
            keyboard.press_and_release(char.lower())
            time.sleep(0.05)  # Increased delay before releasing shift
            keyboard.release('shift')
            time.sleep(0.05)  # Additional delay after character
        else:
            keyboard.write(char)
            time.sleep(0.05)  # Consistent timing for regular characters
        
        typed_buffer += char
    
    print(f"\nTyped initial text: '{typed_buffer}'")
    print("\nNow simulating backspace...")
    
    # Simulate backspace on the last 8 characters
    num_backspaces = 8
    deleted_chars = typed_buffer[-num_backspaces:]
    
    # Do backspace simulation with improved timing
    for i in range(num_backspaces):
        keyboard.press_and_release('backspace')
        time.sleep(0.1)  # Slightly longer delay between backspaces
    
    # Update buffer
    typed_buffer = typed_buffer[:-num_backspaces]
    print(f"After backspace: '{typed_buffer}'")
    print(f"Characters to retype: '{deleted_chars}'")
    
    # Wait a moment before retyping
    time.sleep(1.0)  # Longer pause before retyping
    
    # Retype the deleted characters
    print("\nNow retyping deleted characters:")
    for char in deleted_chars:
        print(f"Retyping: '{char}'")
        
        if char == ' ':
            keyboard.press_and_release('space')
            time.sleep(0.1)  # Consistent timing for spaces
        elif char == '!':
            keyboard.press('shift')
            time.sleep(0.05)  # Increased delay for shift
            keyboard.press_and_release('1')
            time.sleep(0.05)  # Increased delay before releasing shift
            keyboard.release('shift')
            time.sleep(0.05)  # Additional delay after character
        elif char.isupper():
            keyboard.press('shift')
            time.sleep(0.05)  # Increased delay for shift
            keyboard.press_and_release(char.lower())
            time.sleep(0.05)  # Increased delay before releasing shift
            keyboard.release('shift')
            time.sleep(0.05)  # Additional delay after character
        else:
            keyboard.write(char)
            time.sleep(0.05)  # Consistent timing for regular characters
            
        typed_buffer += char
    
    # Add a newline at the end
    time.sleep(0.5)  # Wait before newline
    keyboard.press_and_release('enter')
    
    print(f"\nFinal text: '{typed_buffer}'")
    print("\nBackspace test complete!")

if __name__ == "__main__":
    print("This script will test the keyboard typing and backspace functionality.")
    print("Click in a text editor where you want the text to appear.")
    
    # Check command line arguments for which test to run
    if len(sys.argv) > 1:
        test_name = sys.argv[1].lower()
        if test_name == "uppercase":
            test_uppercase_typing()
        elif test_name == "mixed":
            test_mixed_case_typing()
        elif test_name == "backspace":
            test_backspace_retyping()
        else:
            print(f"Unknown test: {test_name}")
            print("Available tests: uppercase, mixed, backspace")
    else:
        # Run all tests with a pause between them
        print("Running all tests in sequence...")
        print("You have 3 seconds to position your cursor...")
        time.sleep(3)
        
        test_uppercase_typing()
        time.sleep(2)
        test_mixed_case_typing()
        time.sleep(2)
        test_backspace_retyping()
