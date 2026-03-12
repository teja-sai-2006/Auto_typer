#!/usr/bin/env python3

"""
Universal launcher script for Auto Typer application.
Works on both Windows and Linux platforms.
"""

import os
import sys
import subprocess
import platform
import ctypes

PACKAGED = getattr(sys, 'frozen', False)

# Set up Windows-specific attributes
if platform.system() == 'Windows':
    try:
        windll = ctypes.windll  # type: ignore[attr-defined]
    except Exception:
        windll = None
else:
    windll = None

def is_admin() -> bool:
    """Check if the script is running with admin/root privileges.

    We skip forced elevation when running in a frozen/packaged mode to avoid
    recursion and UAC loops. Global hotkeys may still work without elevation
    on many systems; if not, user will be informed.
    """
    try:
        if platform.system() == 'Windows' and windll:
            try:
                return bool(windll.shell32.IsUserAnAdmin())  # type: ignore[attr-defined]
            except Exception:
                return False
        else:
            # On POSIX
            return os.geteuid() == 0  # type: ignore[attr-defined]
    except Exception:
        return False

def setup_dependencies() -> bool:
    """Ensure required runtime dependencies are present (only in dev/unfrozen)."""
    if PACKAGED:
        # Dependencies are bundled already
        return True
    try:
        import keyboard  # type: ignore
        _ = keyboard.__dict__  # Access attribute to avoid "unused" diagnostics
        return True
    except ImportError:
        print("Installing required packages (development mode)...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "keyboard"])  # noqa: S603 S607
            return True
        except Exception as e:
            print(f"Error installing packages: {e}")
            return False

def resolve_base_dir() -> str:
    """Return the base directory depending on packaging state."""
    if PACKAGED:
        # sys._MEIPASS is extraction dir in onefile mode; fall back to exe dir
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))  # type: ignore[attr-defined]
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return base_dir


def main() -> None:
    base_dir = resolve_base_dir()
    app_dir = os.path.join(base_dir, "auto_typer")
    
    # Ensure resources directory exists
    resources_dir = os.path.join(app_dir, "resources")
    os.makedirs(resources_dir, exist_ok=True)
    
    # Create empty files if they don't exist
    new_snippets = os.path.join(resources_dir, "snippets.json")
    new_history = os.path.join(resources_dir, "history.json")
    
    if not os.path.exists(new_snippets):
        with open(new_snippets, 'w') as f:
            f.write('{}')
    if not os.path.exists(new_history):
        with open(new_history, 'w') as f:
            f.write('[]')
    
    # Install dependencies if needed (skipped when frozen)
    if not setup_dependencies():
        print("Failed to install required packages (development mode).")
        sys.exit(1)
    
    # Check for root/admin privileges (optional in packaged mode)
    if not is_admin():
        if PACKAGED:
            print("[launcher] Warning: Not running with elevated privileges. Some global hotkeys may not register.")
        else:
            if platform.system() == 'Windows':
                if windll:
                    try:
                        windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)  # type: ignore[attr-defined]
                        return
                    except Exception:
                        print("[launcher] Could not elevate privileges on Windows. Continuing without elevation.")
                else:
                    print("[launcher] Windows elevation helpers unavailable. Continuing.")
            else:
                # Offer a sudo relaunch only in dev scenario
                if sys.stdin.isatty():
                    resp = input("Re-run with sudo for full hotkey support? (y/N): ").strip().lower()
                    if resp == 'y':
                        try:
                            os.execvp("sudo", ["sudo", sys.executable] + sys.argv)
                        except Exception as e:
                            print(f"[launcher] Error attempting sudo: {e}")
                print("[launcher] Continuing without elevation; some hotkeys may fail.")
    
    # If we're here, we have admin privileges
    print("Running Auto Typer...")
    
    # Run the application
    os.chdir(app_dir)
    try:
        # Ensure PYTHONPATH includes the app directory
        env = os.environ.copy()
        env["PYTHONPATH"] = app_dir + os.pathsep + env.get("PYTHONPATH", "")
        subprocess.run([sys.executable, "frontend.py"], check=True, env=env)
    except subprocess.CalledProcessError as e:
        print(f"Error running application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
