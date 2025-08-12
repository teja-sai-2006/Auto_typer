#!/usr/bin/env python3

"""
Setup script for Auto Typer application.
This script will create a virtual environment and install the required packages.
"""

import os
import sys
import subprocess
import shutil
import platform
import argparse

def print_status(message):
    """Print a status message with color."""
    print(f"\033[94m[Setup]\033[0m {message}")

def print_error(message):
    """Print an error message with color."""
    print(f"\033[91m[Error]\033[0m {message}")

def print_success(message):
    """Print a success message with color."""
    print(f"\033[92m[Success]\033[0m {message}")

def create_virtual_env(venv_dir):
    """Create a virtual environment."""
    print_status(f"Creating virtual environment in {venv_dir}")
    try:
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
        print_success("Virtual environment created successfully.")
        return True
    except subprocess.CalledProcessError:
        print_error("Failed to create virtual environment.")
        return False

def get_python_executable(venv_dir):
    """Get the path to the Python executable in the virtual environment."""
    if platform.system() == "Windows":
        return os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        return os.path.join(venv_dir, "bin", "python")

def install_packages(venv_python):
    """Install required packages."""
    print_status("Installing required packages...")
    packages = ["keyboard", "tk"]
    
    try:
        subprocess.run([venv_python, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        subprocess.run([venv_python, "-m", "pip", "install"] + packages, check=True)
        print_success("Required packages installed successfully.")
        return True
    except subprocess.CalledProcessError:
        print_error("Failed to install required packages.")
        return False

def create_activation_script(venv_dir, script_path):
    """Create a script to activate the virtual environment and run the application."""
    print_status("Creating activation script...")
    
    if platform.system() == "Windows":
        # Create a batch script for Windows
        with open(script_path, "w") as f:
            f.write(f'@echo off\n')
            f.write(f'echo Activating virtual environment and running Auto Typer...\n')
            f.write(f'call "{os.path.join(venv_dir, "Scripts", "activate.bat")}"\n')
            f.write(f'cd "{os.path.dirname(os.path.abspath(script_path))}\\code of the application"\n')
            f.write(f'python frontend.py\n')
            f.write(f'deactivate\n')
    else:
        # Create a bash script for Unix-like systems
        with open(script_path, "w") as f:
            f.write(f'#!/bin/bash\n')
            f.write(f'echo "Activating virtual environment and running Auto Typer..."\n')
            f.write(f'source "{os.path.join(venv_dir, "bin", "activate")}"\n')
            f.write(f'cd "{os.path.dirname(os.path.abspath(script_path))}/code of the application"\n')
            f.write(f'python frontend.py\n')
            f.write(f'deactivate\n')
        
        # Make the script executable
        os.chmod(script_path, 0o755)
    
    print_success(f"Activation script created: {script_path}")

def main():
    parser = argparse.ArgumentParser(description="Setup Auto Typer application")
    parser.add_argument("--venv-dir", default="venv", help="Directory name for the virtual environment")
    args = parser.parse_args()
    
    # Get the directory of this script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(base_dir, args.venv_dir)
    
    print_status("Setting up Auto Typer application...")
    print_status(f"Base directory: {base_dir}")
    
    # Check if virtual environment exists
    if os.path.exists(venv_dir):
        response = input(f"Virtual environment directory {venv_dir} already exists. Recreate? (y/n): ")
        if response.lower() == 'y':
            shutil.rmtree(venv_dir)
        else:
            print_status("Using existing virtual environment.")
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists(venv_dir):
        if not create_virtual_env(venv_dir):
            return 1
    
    # Get Python executable path
    venv_python = get_python_executable(venv_dir)
    
    # Install required packages
    if not install_packages(venv_python):
        return 1
    
    # Create activation script
    script_name = "run_auto_typer.bat" if platform.system() == "Windows" else "run_auto_typer.sh"
    script_path = os.path.join(base_dir, script_name)
    create_activation_script(venv_dir, script_path)
    
    print_status("Auto Typer setup completed successfully.")
    print_status(f"To run the application, use: {script_path}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
