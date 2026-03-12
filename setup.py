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
from pathlib import Path

def print_status(message: str) -> None:
    """Print a status message with color."""
    print(f"\033[94m[Setup]\033[0m {message}")

def print_error(message: str) -> None:
    """Print an error message with color."""
    print(f"\033[91m[Error]\033[0m {message}")

def print_success(message: str) -> None:
    """Print a success message with color."""
    print(f"\033[92m[Success]\033[0m {message}")

def create_virtual_env(venv_dir: str) -> bool:
    """Create a virtual environment."""
    print_status(f"Creating virtual environment in {venv_dir}")
    try:
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
        print_success("Virtual environment created successfully.")
        return True
    except subprocess.CalledProcessError:
        print_error("Failed to create virtual environment.")
        return False

def get_python_executable(venv_dir: str) -> str:
    """Get the path to the Python executable in the virtual environment."""
    if platform.system() == "Windows":
        return os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        return os.path.join(venv_dir, "bin", "python")

def parse_requirements(req_file: Path) -> list[str]:
    """Parse a requirements.txt style file into a list of packages.

    Empty lines and comments (# ...) are ignored.
    """
    packages: list[str] = []
    if not req_file.exists():
        return packages
    for line in req_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        packages.append(line)
    return packages

def install_packages(venv_python: str, base_dir: Path) -> bool:
    """Install required packages inside the virtual environment.

    Reads from requirements.txt if present; falls back to minimal default list.
    Tkinter is part of the standard library; we just verify it can be imported.
    """
    req_file = base_dir / "requirements.txt"
    packages = parse_requirements(req_file) or ["keyboard"]  # minimal fallback
    print_status(f"Installing required packages: {', '.join(packages)}")

    try:
        subprocess.run([venv_python, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        if packages:
            subprocess.run([venv_python, "-m", "pip", "install", *packages], check=True)
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install required packages: {e}")
        return False

    # Verify tkinter availability (can't be installed via pip reliably on many systems)
    try:
        subprocess.run([venv_python, "-c", "import tkinter"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print_error(
            "tkinter is not available in this Python build. Install system package (e.g., 'sudo apt install python3-tk') if GUI fails."
        )
    else:
        print_status("tkinter module available.")

    print_success("Dependencies installed.")
    return True

def print_run_instructions(venv_dir: Path, base_dir: Path) -> None:
    """Show user how to activate venv & run launcher without creating wrapper scripts."""
    if platform.system() == "Windows":
        print_status("Run commands (PowerShell):")
        print("  .\\%s\\Scripts\\Activate.ps1" % venv_dir.name)
        print("  python run_auto_typer.py")
    else:
        print_status("Run commands (bash):")
        print(f"  source {venv_dir}/bin/activate")
        print("  python run_auto_typer.py  # add 'sudo' if hotkeys fail")

def main():
    parser = argparse.ArgumentParser(description="Setup Auto Typer application")
    parser.add_argument("--venv-dir", default="venv", help="Directory name for the virtual environment")
    parser.add_argument("--force", action="store_true", help="Recreate virtual environment if it already exists")
    args = parser.parse_args()
    
    # Get the directory of this script
    base_dir = Path(__file__).resolve().parent
    venv_dir = base_dir / args.venv_dir
    
    print_status("Setting up Auto Typer application...")
    print_status(f"Base directory: {base_dir}")
    
    # Check if virtual environment exists
    if venv_dir.exists():
        if args.force:
            print_status("--force specified; removing existing virtual environment.")
            shutil.rmtree(venv_dir)
        else:
            print_status(f"Virtual environment already exists at {venv_dir}. Use --force to recreate.")
    
    # Create virtual environment if it doesn't exist
    if not venv_dir.exists():
        if not create_virtual_env(str(venv_dir)):
            return 1
    
    # Get Python executable path
    venv_python = get_python_executable(str(venv_dir))
    
    # Install required packages
    if not install_packages(venv_python, base_dir):
        return 1
    
    # Show run instructions instead of creating wrapper scripts
    print_run_instructions(venv_dir, base_dir)
    print_status("Auto Typer setup completed successfully.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
