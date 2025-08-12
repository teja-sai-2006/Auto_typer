# Ensure backend.py is in the same directory as this file.
from datetime import datetime
import os
import threading
import time
import argparse
import tkinter as tk
from tkinter import ttk, filedialog, messagebox  # Added required tkinter submodules
from typing import Dict, Any, Set, Optional, List, Sequence, cast
import keyboard  # Import the keyboard library in the frontend as well

# Attempt to import backend, handle potential ImportError
try:
    from backend import (
        save_snippets, load_snippets, register_hotkeys, normalize_hotkey,
        import_snippets, export_snippets, clear_all_snippets,
        get_history, clear_history, check_for_update, execute_snippet
    )
except ImportError:
    messagebox.showerror("Error", "backend.py not found or contains errors. Please ensure it's in the same directory.")
    exit()  # Exit if backend cannot be imported

# --- Parse command line arguments ---
parser = argparse.ArgumentParser(description='Auto Typing App')
parser.add_argument('--app-dir', help='Directory where the application files are located')
args = parser.parse_args()

# Change to the specified app directory if provided
if args.app_dir and os.path.exists(args.app_dir):
    os.chdir(args.app_dir)
    print(f"[frontend] Changed working directory to: {args.app_dir}")

# --- Global Snippet Data ---
# Load snippets at the start, handle potential errors during loading
try:
    snippets = load_snippets() or {}

    # --- Add a default snippet if none are loaded ---
    if not snippets:
        print("[frontend] No snippets found or error loading. Adding a sample snippet.")
        sample_snippet_name = "Welcome Message"
        sample_snippet_data: Dict[str, Any] = {
            "text": "Hello! This is a sample snippet. You can edit or delete it.",
            "min_delay": 0.02,
            "max_delay": 0.08,
            "backspace_probability": 0.1,
            "min_backspaces": 1,
            "max_backspaces": 2,
            "hotkey": "",  # No default hotkey assigned, user can set one
            "uppercase": False,
            "lowercase": False,
            "remove_spaces": False,
            "remove_symbols": False,
            "keep_alphanumeric_spaces": False,
            "category": "Samples",
            "history": []
        }
        snippets[sample_snippet_name] = sample_snippet_data  # type: ignore[assignment]
        save_snippets(snippets)
    else:
        print(f"[frontend] Loaded {len(snippets)} snippets from file.")
    # --- End default snippet logic ---

except Exception as e:
    messagebox.showerror("Load Error", f"Failed to load or initialize snippets:\n{e}\n\nStarting with an empty set.")
    snippets = {}


class AutoTypingApp(ttk.Frame):
    def __init__(self, master: tk.Tk):
        super().__init__(master)
        self.master = master
        self.fields: Dict[str, Any] = {}
        self._hotkey_listener_handle: Optional[Any] = None
        self._captured_hotkey_parts: Set[str] = set()
        self.search_var: tk.StringVar
        self.search_entry: ttk.Entry
        self.listbox: tk.Listbox
        self.status: ttk.Label
        self.made_by_label: ttk.Label
        self.theme_button: ttk.Button
        self.uppercase_var: tk.BooleanVar
        self.lowercase_var: tk.BooleanVar
        self.remove_spaces_var: tk.BooleanVar
        self.remove_symbols_var: tk.BooleanVar
        self.keep_alphanumeric_spaces_var: tk.BooleanVar
        self.style: ttk.Style
        self.available_themes: List[str] = []
        self.theme_mode: str = ""

        # --- Basic Window Setup ---
        master.title("Auto Typing App v1.2")
        
        # Get screen dimensions to set window size proportionally
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        
        # Set window size to 80% of screen dimensions (but capped for very large screens)
        width = min(int(screen_width * 0.8), 1200)
        height = min(int(screen_height * 0.8), 800)
        master.geometry(f"{width}x{height}")
        
        # Set minimum size to ensure UI is still usable
        master.minsize(800, 550)
        
        # Configure resizing behavior with improved weights
        master.rowconfigure(0, weight=1)  # Main content row
        master.columnconfigure(0, weight=1, minsize=250)  # Left panel (List)
        master.columnconfigure(1, weight=3, minsize=450)  # Right panel (Form)
        master.rowconfigure(2, weight=0)  # Status bar row

        self.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.create_widgets()

        # --- Style and Theme ---
        self.style = ttk.Style()
        self.available_themes = list(self.style.theme_names())
        # Try to set a modern theme if available
        preferred_themes = ['clam', 'alt', 'default']
        for theme in preferred_themes:
            if theme in self.available_themes:
                self.style.theme_use(theme)
                break
        self.theme_mode = "light"  # Default theme mode
        # Now call configure_styles AFTER widgets have been created
        self.configure_styles()  # THIS CALL IS MOVED DOWN

        # --- Initial Actions ---
        self.refresh_list()  # Populate the listbox initially
        self.register_app_hotkeys()  # Register snippets from loaded data
        # Start update check in background
        threading.Thread(target=self._check_updates_thread, daemon=True).start()
        # Set focus to search entry initially
        self.search_entry.focus_set()

        # Ensure the global hotkey listener is unhooked on close
        master.protocol("WM_DELETE_WINDOW", self.on_close)

    def configure_styles(self):
        """Configures custom styles for widgets."""
        # Define colors based on theme mode
        bg_color = "#f0f0f0" if self.theme_mode == "light" else "#2b2b2b"
        fg_color = "black" if self.theme_mode == "light" else "white"
        entry_bg = "white" if self.theme_mode == "light" else "#3c3f41"
        entry_fg = "black" if self.theme_mode == "light" else "white"
        list_bg = "white" if self.theme_mode == "light" else "#313335"
        list_fg = "black" if self.theme_mode == "light" else "white"
        list_select_bg = "#cce8ff" if self.theme_mode == "light" else "#0078d7"  # More distinct selection
        list_select_fg = "black" if self.theme_mode == "light" else "white"
        button_bg = "#e0e0e0" if self.theme_mode == "light" else "#555555"
        button_fg = "black" if self.theme_mode == "light" else "white"
        status_bg = "#e8e8e8" if self.theme_mode == "light" else "#3a3a3a"
        status_fg = "#333333" if self.theme_mode == "light" else "#cccccc"
        
        # Theme button specific colors
        theme_button_bg = "#4a6fa5" if self.theme_mode == "light" else "#555555"
        theme_button_fg = "white" if self.theme_mode == "light" else "#cccccc"
        theme_button_active_bg = "#5c8cd5" if self.theme_mode == "light" else "#777777"

        # Apply styles
        self.style.configure(".", background=bg_color, foreground=fg_color)  # type: ignore
        self.style.configure("TFrame", background=bg_color)  # type: ignore
        self.style.configure("TLabel", background=bg_color, foreground=fg_color)  # type: ignore
        self.style.configure("TButton", background=button_bg, foreground=button_fg, padding=5)  # type: ignore
        self.style.map("TButton", background=[('active', '#c0c0c0' if self.theme_mode == 'light' else '#6a6a6a')])  # type: ignore
        self.style.configure("TEntry", fieldbackground=entry_bg, foreground=entry_fg, insertcolor=fg_color)  # type: ignore
        self.style.configure("TCombobox", fieldbackground=entry_bg, foreground=entry_fg, insertcolor=fg_color)  # type: ignore
        
        # Custom style for theme toggle button
        self.style.configure("Theme.TButton",  # type: ignore
                            background=theme_button_bg, 
                            foreground=theme_button_fg, 
                            borderwidth=2,
                            relief="raised",
                            padding=8)
        self.style.map("Theme.TButton",  # type: ignore
                      background=[('active', theme_button_active_bg), 
                                 ('pressed', '#3a5e8c' if self.theme_mode == 'light' else '#444444')])
        
        # Custom styles for action buttons
        # Primary action button (Add/Save)
        self.style.configure("Action.TButton",  # type: ignore
                            background="#4caf50" if self.theme_mode == "light" else "#2e7d32",
                            foreground="white",
                            borderwidth=2,
                            relief="raised",
                            padding=8)
        self.style.map("Action.TButton",  # type: ignore
                      background=[('active', '#66bb6a' if self.theme_mode == "light" else "#43a047"),
                                 ('pressed', '#43a047' if self.theme_mode == "light" else "#1b5e20")])
        
        # Danger button (Delete)
        self.style.configure("Danger.TButton",  # type: ignore
                            background="#f44336" if self.theme_mode == "light" else "#c62828",
                            foreground="white",
                            borderwidth=2,
                            relief="raised",
                            padding=8)
        self.style.map("Danger.TButton",  # type: ignore
                      background=[('active', '#ef5350' if self.theme_mode == "light" else "#d32f2f"),
                                 ('pressed', '#d32f2f' if self.theme_mode == "light" else "#b71c1c")])
        
        # Test button (Test Typing)
        self.style.configure("Test.TButton",  # type: ignore
                            background="#2196f3" if self.theme_mode == "light" else "#1565c0",
                            foreground="white",
                            borderwidth=2,
                            relief="raised",
                            padding=8)
        self.style.map("Test.TButton",  # type: ignore
                      background=[('active', '#42a5f5' if self.theme_mode == "light" else "#1976d2"),
                                 ('pressed', '#1e88e5' if self.theme_mode == "light" else "#0d47a1")])
        
        # Info button (Show History)
        self.style.configure("Info.TButton",  # type: ignore
                            background="#9c27b0" if self.theme_mode == "light" else "#7b1fa2",
                            foreground="white",
                            borderwidth=2,
                            relief="raised",
                            padding=8)
        self.style.map("Info.TButton",  # type: ignore
                      background=[('active', '#ab47bc' if self.theme_mode == "light" else "#8e24aa"),
                                 ('pressed', '#8e24aa' if self.theme_mode == "light" else "#6a1b9a")])
        
        # Secondary button (Clear Fields)
        self.style.configure("Secondary.TButton",  # type: ignore
                            background="#ff9800" if self.theme_mode == "light" else "#ef6c00",
                            foreground="white",
                            borderwidth=2,
                            relief="raised",
                            padding=8)
        self.style.map("Secondary.TButton",  # type: ignore
                      background=[('active', '#ffa726' if self.theme_mode == "light" else "#f57c00"),
                                 ('pressed', '#fb8c00' if self.theme_mode == "light" else "#e65100")])
        # Listbox needs direct configuration as it's not a ttk widget
        self.listbox.configure(
            background=list_bg, foreground=list_fg,
            selectbackground=list_select_bg, selectforeground=list_select_fg,
            highlightthickness=0, borderwidth=1, relief="sunken"
        )
        # Text widget also needs direct config
        self.fields["Text"].configure(
            background=entry_bg, foreground=entry_fg, insertbackground=fg_color,
            borderwidth=1, relief="sunken"
        )
        # Status bar style
        self.status.configure(background=status_bg, foreground=status_fg)
        self.made_by_label.configure(background=bg_color, foreground="#888" if self.theme_mode == "light" else "#aaa")

    def create_widgets(self):
        """Creates and arranges all the UI elements."""
        # --- Menu Bar ---
        menubar = tk.Menu(self.master)
        self.master['menu'] = menubar

        # File Menu
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Import Snippets...", command=self.on_import)
        filemenu.add_command(label="Export Snippets...", command=self.on_export)
        filemenu.add_separator()
        filemenu.add_command(label="Clear All Snippets...", command=self.on_clear_all)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.master.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        # View Menu
        viewmenu = tk.Menu(menubar, tearoff=0)
        viewmenu.add_command(label="Toggle Dark/Light Theme", command=self.toggle_theme)
        menubar.add_cascade(label="View", menu=viewmenu)
        
        # Theme Toggle Button (added for better accessibility)
        self.theme_button = ttk.Button(
            self.master, 
            text="Toggle Theme", 
            command=self.toggle_theme,
            style="Theme.TButton"
        )
        self.theme_button.place(relx=0.97, rely=0.03, anchor='ne')

        # Help Menu (Optional)
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=helpmenu)

        # --- Left Panel (Snippet List) ---
        left_panel = ttk.Frame(self.master, padding="5 5 5 5")
        left_panel.grid(row=0, column=0, sticky="nsew")
        left_panel.rowconfigure(1, weight=1)  # Listbox frame row
        left_panel.columnconfigure(0, weight=1)  # Entry column

        # Search Bar
        search_frame = ttk.Frame(left_panel)
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        search_frame.columnconfigure(1, weight=1)
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=1, sticky="ew")
        self.search_entry.bind("<KeyRelease>", lambda ev: self.refresh_list())  # Use KeyRelease for better UX

        # Listbox with Scrollbar
        listbox_frame = ttk.Frame(left_panel)
        listbox_frame.grid(row=1, column=0, sticky="nsew")
        listbox_frame.rowconfigure(0, weight=1)
        listbox_frame.columnconfigure(0, weight=1)

        self.listbox = tk.Listbox(listbox_frame, exportselection=False, activestyle='none')  # Use exportselection=False
        self.listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.listbox.yview)  # type: ignore
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.listbox.config(yscrollcommand=scrollbar.set)
        self.listbox.bind("<<ListboxSelect>>", self.on_listbox_select)  # Use a dedicated handler

        # --- Right Panel (Snippet Details Form) ---
        right_panel = ttk.Frame(self.master, padding="5 5 5 5")
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.rowconfigure(0, weight=1)  # Form frame row
        right_panel.columnconfigure(0, weight=1)  # Form frame column

        form_frame = ttk.LabelFrame(right_panel, text="Snippet Details", padding="10 10 10 10")
        form_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        form_frame.columnconfigure(1, weight=1)  # Make entry column expandable

        # Define form fields with improved grouping
        # Group form fields logically
        field_groups = {
            "Basic Info": ["Name", "Category"],
            "Snippet Content": ["Text"],
            "Typing Settings": ["Min Delay (s)", "Max Delay (s)"],
            "Backspace Simulation": ["Backspace Prob (0-1)", "Min Backspaces", "Max Backspaces"],
            "Text Transformations": ["Text Transformations"],
            "Activation": ["Hotkey"]
        }
    # (Optional) Flattened field list if validation needed later
    # flattened_labels: List[str] = [name for group in field_groups.values() for name in group]

        self.fields = {}
        grid_row_index = 0
        
        # Loop through groups to create section headers and fields
        for group_name, group_fields in field_groups.items():
            # Add section header
            section_header = ttk.Label(
                form_frame, 
                text=group_name, 
                font=("Segoe UI", 10, "bold")
            )
            section_header.grid(
                row=grid_row_index, 
                column=0, 
                columnspan=2, 
                sticky="w", 
                pady=(15 if grid_row_index > 0 else 5, 5), 
                padx=0
            )
            grid_row_index += 1
            
            # Add fields for this section
            for lbl in group_fields:
                # Create label with improved styling
                field_label = ttk.Label(
                    form_frame, 
                    text=f"{lbl}:"
                )
                field_label.grid(
                    row=grid_row_index, 
                    column=0, 
                    sticky="nw", 
                    pady=6, 
                    padx=(10, 15)
                )

                if lbl == "Text":
                    # Text widget with its own scrollbar
                    text_frame = ttk.Frame(form_frame)
                    text_frame.grid(
                        row=grid_row_index, 
                        column=1, 
                        sticky="nsew", 
                        pady=6
                    )
                    text_frame.rowconfigure(0, weight=1)
                    text_frame.columnconfigure(0, weight=1)
                    form_frame.rowconfigure(grid_row_index, weight=1)  # Allow text area to expand vertically

                    txt_widget = tk.Text(
                        text_frame, 
                        height=8, 
                        width=40, 
                        wrap="word",
                        undo=True,  # Enable undo functionality
                        padx=8,     # Internal padding for text
                        pady=8      # Internal padding for text
                    )
                    txt_widget.grid(row=0, column=0, sticky="nsew")
                    txt_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=txt_widget.yview)  # type: ignore
                    txt_scrollbar.grid(row=0, column=1, sticky="ns")
                    txt_widget.config(yscrollcommand=txt_scrollbar.set)
                    self.fields[lbl] = txt_widget
                    
                elif lbl == "Category":
                    # Combobox for categories with improved styling
                    combo_widget = ttk.Combobox(
                        form_frame, 
                        values=self.get_categories(),
                        height=10,  # Show more items in dropdown
                        width=30    # Wider combobox
                    )
                    combo_widget.grid(
                        row=grid_row_index, 
                        column=1, 
                        sticky="ew", 
                        pady=6
                    )
                    self.fields[lbl] = combo_widget
                    
                elif lbl == "Hotkey":
                    # Special handling for hotkey entry with improved styling
                    hotkey_frame = ttk.Frame(form_frame)
                    hotkey_frame.grid(
                        row=grid_row_index, 
                        column=1, 
                        sticky="ew", 
                        pady=6
                    )
                    hotkey_frame.columnconfigure(0, weight=1)
                    
                    hotkey_entry = ttk.Entry(
                        hotkey_frame, 
                        state='readonly',  # Make it readonly
                        width=25
                    )
                    hotkey_entry.grid(
                        row=0, 
                        column=0, 
                        sticky="ew", 
                        padx=(0, 5)
                    )
                    
                    # Add clear button next to hotkey field
                    clear_btn = ttk.Button(
                        hotkey_frame, 
                        text="Clear", 
                        width=8,
                        command=self._clear_hotkey_field
                    )
                    clear_btn.grid(row=0, column=1)
                    
                    # Bind events for capturing hotkeys
                    hotkey_entry.bind("<FocusIn>", self._start_hotkey_capture)
                    hotkey_entry.bind("<FocusOut>", self._stop_hotkey_capture)
                    hotkey_entry.bind("<BackSpace>", self._clear_hotkey_field)
                    
                    self.fields[lbl] = hotkey_entry
                
                elif lbl == "Text Transformations":
                    # Create a frame for transformation checkboxes
                    transformations_frame = ttk.Frame(form_frame)
                    transformations_frame.grid(
                        row=grid_row_index, 
                        column=1, 
                        sticky="ew", 
                        pady=6
                    )
                    
                    # Create checkbox variables
                    self.uppercase_var = tk.BooleanVar(value=False)
                    self.lowercase_var = tk.BooleanVar(value=False)
                    self.remove_spaces_var = tk.BooleanVar(value=False)
                    self.remove_symbols_var = tk.BooleanVar(value=False)
                    self.keep_alphanumeric_spaces_var = tk.BooleanVar(value=False)
                    
                    # Create transformation checkboxes in two columns
                    ttk.Checkbutton(
                        transformations_frame, 
                        text="ALL UPPERCASE", 
                        variable=self.uppercase_var,
                        command=lambda: self._handle_case_option("uppercase")
                    ).grid(row=0, column=0, sticky="w", padx=(0, 10))
                    
                    ttk.Checkbutton(
                        transformations_frame, 
                        text="all lowercase", 
                        variable=self.lowercase_var,
                        command=lambda: self._handle_case_option("lowercase")
                    ).grid(row=0, column=1, sticky="w")
                    
                    ttk.Checkbutton(
                        transformations_frame, 
                        text="Remove spaces", 
                        variable=self.remove_spaces_var
                    ).grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(5, 0))
                    
                    ttk.Checkbutton(
                        transformations_frame, 
                        text="Remove symbols", 
                        variable=self.remove_symbols_var
                    ).grid(row=1, column=1, sticky="w", pady=(5, 0))
                    
                    ttk.Checkbutton(
                        transformations_frame, 
                        text="Keep only alphanumeric & spaces", 
                        variable=self.keep_alphanumeric_spaces_var
                    ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(5, 0))
                    
                    # Store the variables as a dictionary in the fields dictionary
                    self.fields[lbl] = {
                        "uppercase": self.uppercase_var,
                        "lowercase": self.lowercase_var,
                        "remove_spaces": self.remove_spaces_var,
                        "remove_symbols": self.remove_symbols_var,
                        "keep_alphanumeric_spaces": self.keep_alphanumeric_spaces_var
                    }
                    
                else:
                    # Standard entry fields with improved styling
                    entry_widget = ttk.Entry(
                        form_frame,
                        width=30 if lbl in ["Name"] else 15,
                        state='readonly' if lbl == "Name" else 'normal'
                    )
                    entry_widget.grid(
                        row=grid_row_index, 
                        column=1, 
                        sticky="ew", 
                        pady=6
                    )
                    self.fields[lbl] = entry_widget

                grid_row_index += 1

        # Add a help text for backspace simulation
        backspace_help_text = "Backspace simulation: When enabled, the app will occasionally delete characters and retype them to simulate human typing."
        backspace_help_label = ttk.Label(form_frame, text=backspace_help_text, font=("Segoe UI", 8), wraplength=400)
        backspace_help_label.grid(row=grid_row_index, column=0, columnspan=2, sticky="w", pady=(10, 0))

        # --- Button Bar ---
        button_frame = ttk.Frame(right_panel)
        button_frame.grid(row=1, column=0, sticky="ew", pady=(10, 5))
        button_frame.columnconfigure(0, weight=1)  # Let the frame expand

        # Create a centered inner frame for the buttons
        inner_button_frame = ttk.Frame(button_frame)
        inner_button_frame.grid(row=0, column=0)

        buttons = [
            ("Add / Save", self.on_save, "Action.TButton"),  # Primary action
            ("Delete", self.on_delete, "Danger.TButton"),    # Danger action
            ("Test Typing", self.on_test, "Test.TButton"),   # Test action
            ("Show History", self.on_history, "Info.TButton"), # Info action
            ("Clear Fields", self.clear_fields, "Secondary.TButton"), # Secondary action
        ]

        for i, (txt, cmd, style) in enumerate(buttons):
            button = ttk.Button(inner_button_frame, text=txt, command=cmd, style=style, width=12)
            button.grid(row=0, column=i, padx=8, pady=5)

        # --- Status Bar ---
        status_frame = ttk.Frame(self.master)
        status_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
        status_frame.columnconfigure(0, weight=1)
        
        self.status = ttk.Label(
            status_frame, 
            text="Ready", 
            relief="sunken", 
            anchor="w", 
            padding="10 6",
            font=("Segoe UI", 9)
        )
        self.status.grid(row=0, column=0, sticky="ew")

        # --- Footer ---
        footer_frame = ttk.Frame(self.master)
        footer_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        footer_frame.columnconfigure(0, weight=1)
        self.made_by_label = ttk.Label(footer_frame, text="Auto Typing App by Teja", font=("Segoe UI", 8), anchor="e")
        self.made_by_label.grid(row=0, column=0, sticky='e', padx=10)

    # --- Hotkey Capture Functions (Fixed for proper combination capture) ---

    def _start_hotkey_capture(self, event: Optional[tk.Event] = None) -> None:
        """Starts the global hotkey listener and prepares for capturing."""
        if self._hotkey_listener_handle is None:
            print("[frontend] Starting global hotkey capture...")
            self.set_status(
                "Press the desired hotkey combination now (e.g., Ctrl+Shift+A). Press Backspace to clear.",
                warning=True)
            # Clear the field visually when starting capture
            self._set_hotkey_field_text("")
            self._captured_hotkey_parts = set()  # Use a set to store pressed keys

            try:
                # Use keyboard.hook to capture any key event
                self._hotkey_listener_handle = keyboard.hook(self._on_global_key_event_monitor)

            except Exception as e:
                print(f"[frontend] Error starting global hotkey capture: {e}")
                self.set_status("Error starting hotkey capture.", error=True)
                self._stop_hotkey_capture()  # Ensure handle is cleared on error

    def _on_global_key_event_monitor(self, event: keyboard.KeyboardEvent) -> Optional[bool]:
        """Callback for the global keyboard listener - builds the hotkey string."""
        # Only process key down events to build the combination
        if event.event_type == keyboard.KEY_DOWN:
            name = event.name.lower() if event.name else "" # Get the key name
            
            # Handle backspace key specially
            if name == 'backspace':
                self._clear_hotkey_field()
                return False  # Stop event propagation
                
            # Skip modifier keys when they're released to avoid duplicates
            if name in ['ctrl', 'shift', 'alt', 'windows', 'ctrl_l', 'ctrl_r', 'shift_l', 'shift_r', 'alt_l', 'alt_r']:
                # For modifier keys, we only want to add them once
                self._captured_hotkey_parts.add(name)
            else:
                # For regular keys, we want to capture the current state of modifiers
                modifiers: List[str] = []
                if keyboard.is_pressed('ctrl'):
                    modifiers.append('ctrl')
                if keyboard.is_pressed('shift'):
                    modifiers.append('shift')
                if keyboard.is_pressed('alt'):
                    modifiers.append('alt')
                if keyboard.is_pressed('windows'):
                    modifiers.append('windows')
                
                # Create a clean hotkey string with modifiers + key
                self._captured_hotkey_parts = set(modifiers + [name])
                
            # Update the hotkey field display (sorted and joined with +)
            hotkey_display = normalize_hotkey("+".join(sorted(list(self._captured_hotkey_parts))))
            self._set_hotkey_field_text(hotkey_display)
            
            # Prevent the key event from being passed through to other applications while capturing
            return False  # Stop event propagation
        return None

    def _stop_hotkey_capture(self, event: Optional[tk.Event] = None) -> None:
        """Stops the global hotkey listener and finalizes the captured hotkey."""
        if self._hotkey_listener_handle:
            print("[frontend] Stopping global hotkey capture.")
            try:
                keyboard.unhook(self._hotkey_listener_handle)
                self._hotkey_listener_handle = None
                # Finalize the captured hotkey string from the set of pressed keys
                # Normalize the final captured string
                final_hotkey_str = normalize_hotkey("+".join(sorted(list(self._captured_hotkey_parts))))
                self._set_hotkey_field_text(final_hotkey_str)
                if final_hotkey_str:
                    self.set_status(f"Hotkey captured: {final_hotkey_str}")
                else:
                    self.set_status("Hotkey capture cancelled or empty.", warning=True)
            except Exception as e:
                print(f"[frontend] Error stopping global hotkey capture: {e}")
                self._set_hotkey_field_text("")  # Clear on error
                self.set_status("Error during hotkey capture.", error=True)
            finally:
                # Ensure status is reset if it was the capture prompt
                if self.status.cget("text").startswith("Press the desired hotkey combination now..."):
                    self.set_status("Ready")
                # Clear the captured parts set after finalizing
                self._captured_hotkey_parts = set()

    def _set_hotkey_field_text(self, text: str) -> None:
        """Thread-safe way to update the Hotkey entry field."""
        try:
            hotkey_entry = self.fields["Hotkey"]
            # Use master.after to schedule the update on the main Tkinter thread
            self.master.after(0, lambda: self._update_hotkey_entry_widget(hotkey_entry, text))
        except Exception as e:
            print(f"[frontend] Error scheduling hotkey field update: {e}")

    def _update_hotkey_entry_widget(self, widget: ttk.Entry, text: str) -> None:
        """Performs the actual update of the Hotkey entry widget."""
        try:
            widget.config(state='normal')  # Enable to modify
            widget.delete(0, tk.END)
            widget.insert(0, text)
            widget.config(state='readonly')  # Disable editing
        except Exception as e:
            print(f"[frontend] Error updating hotkey entry widget: {e}")

    def _clear_hotkey_field(self, event: Optional[tk.Event] = None) -> str:
        """Clears the hotkey field and stops listener when Backspace is pressed while focused."""
        if self._hotkey_listener_handle:
            keyboard.unhook(self._hotkey_listener_handle)
            self._hotkey_listener_handle = None
        
        self._captured_hotkey_parts = set()  # Clear the captured parts set
        self._set_hotkey_field_text("")  # Clear the field visually
        self.set_status("Hotkey field cleared.")
        return "break"  # Prevent default backspace
        
    def _handle_case_option(self, selected_option: str) -> None:
        """Handles the mutually exclusive uppercase/lowercase options."""
        if selected_option == "uppercase" and self.uppercase_var.get():
            self.lowercase_var.set(False)
        elif selected_option == "lowercase" and self.lowercase_var.get():
            self.uppercase_var.set(False)

    # --- Remaining Event Handlers & Actions (Same as before with value handling and TypeError fixes) ---

    def get_categories(self) -> List[str]:
        """Extracts unique categories from snippets."""
        categories: Set[str] = {""}  # Start with an empty category option
        for data in snippets.values():
            cat = data.get("category", "").strip()
            if cat:
                categories.add(cat)
        return sorted(list(categories))

    def refresh_list(self, select_name: Optional[str] = None) -> None:
        """Refreshes the snippet listbox, optionally selecting an item."""
        search_term = self.search_var.get().lower()
        self.listbox.delete(0, tk.END)
        for name, data in snippets.items():
            if search_term in name.lower():
                category = str(data.get("category", "")).strip()  # Get category, default to ""
                display_text: str = f"{name} ({category})" if category else name
                self.listbox.insert(tk.END, display_text)
        if select_name:
            size = int(self.listbox.size())  # type: ignore[no-untyped-call]
            for i in range(size):
                item_text = str(self.listbox.get(i))  # type: ignore[no-untyped-call]
                base_name = item_text.split(" (")[0]
                if select_name == base_name:  # Compare only the name part
                    self.listbox.selection_set(i)
                    break

    def on_listbox_select(self, event: Optional[tk.Event] = None) -> None:
        """Handles selection of a snippet from the listbox."""
        selection_raw = self.listbox.curselection()  # type: ignore[no-untyped-call]
        selection = cast(Sequence[int], selection_raw)
        if selection and len(selection) > 0:
            selected_index = int(selection[0])
            selected_item = str(self.listbox.get(selected_index))  # type: ignore[no-untyped-call]
            selected_name = selected_item.split(" (")[0]
            self.load_snippet_data(selected_name)

    def load_snippet_data(self, name: str) -> None:
        """Loads snippet data into the form."""
        snippet = snippets.get(name, {})
        if snippet:
            self.fields["Name"].config(state="normal")  # Make Name field editable temporarily
            self.fields["Name"].delete(0, tk.END)
            self.fields["Name"].insert(0, name)
            self.fields["Name"].config(state="readonly")  # Then make it readonly again

            self.fields["Category"].delete(0, tk.END)
            self.fields["Category"].insert(0, snippet.get("category", ""))

            self.fields["Text"].delete("1.0", tk.END)
            self.fields["Text"].insert(tk.END, snippet.get("text", ""))

            self.fields["Min Delay (s)"].delete(0, tk.END)
            self.fields["Min Delay (s)"].insert(0, str(snippet.get("min_delay", 0.01)))  # Default value

            self.fields["Max Delay (s)"].delete(0, tk.END)
            self.fields["Max Delay (s)"].insert(0, str(snippet.get("max_delay", 0.05)))  # Default value

            self.fields["Backspace Prob (0-1)"].delete(0, tk.END)
            self.fields["Backspace Prob (0-1)"].insert(0, str(snippet.get("backspace_probability", 0.0)))  # Default

            self.fields["Min Backspaces"].delete(0, tk.END)
            self.fields["Min Backspaces"].insert(0, str(snippet.get("min_backspaces", 1)))  # Default

            self.fields["Max Backspaces"].delete(0, tk.END)
            self.fields["Max Backspaces"].insert(0, str(snippet.get("max_backspaces", 3)))  # Default

            # Set text transformation checkboxes
            self.fields["Text Transformations"]["uppercase"].set(snippet.get("uppercase", False))
            self.fields["Text Transformations"]["lowercase"].set(snippet.get("lowercase", False))
            self.fields["Text Transformations"]["remove_spaces"].set(snippet.get("remove_spaces", False))
            self.fields["Text Transformations"]["remove_symbols"].set(snippet.get("remove_symbols", False))
            self.fields["Text Transformations"]["keep_alphanumeric_spaces"].set(snippet.get("keep_alphanumeric_spaces", False))

            self._set_hotkey_field_text(snippet.get("hotkey", "")) # Use helper to update

            self.set_status(f"Loaded snippet: {name}")
        else:
            self.clear_fields()
            self.set_status(f"Snippet not found: {name}", error=True)

    def on_save(self) -> None:
        """Adds or updates a snippet with the data from the form."""
        name = self.fields["Name"].get().strip()
        if not name:
            self.set_status("Snippet name cannot be empty.", error=True)
            return

        # Validate other fields before saving
        try:
            min_delay = float(self.fields["Min Delay (s)"].get())
            max_delay = float(self.fields["Max Delay (s)"].get())
            backspace_prob = float(self.fields["Backspace Prob (0-1)"].get())
            min_backspaces = int(self.fields["Min Backspaces"].get())
            max_backspaces = int(self.fields["Max Backspaces"].get())
        except ValueError:
            self.set_status("Invalid input in numerical fields. Please check your values.", error=True)
            return

        if not (0 <= min_delay <= max_delay):
            self.set_status("Invalid delay values. Min Delay must be <= Max Delay, and both must be >= 0.", error=True)
            return
        if not (0 <= backspace_prob <= 1):
            self.set_status("Invalid backspace probability. Must be between 0 and 1.", error=True)
            return
        if not (0 < min_backspaces <= max_backspaces):
            self.set_status("Invalid backspace counts. Min Backspaces must be > 0 and <= Max Backspaces.", error=True)
            return

        text = self.fields["Text"].get("1.0", tk.END).strip()
        category = self.fields["Category"].get().strip()
        hotkey = self.fields["Hotkey"].get().strip() # Get normalized hotkey string

        # Get text transformation settings
        uppercase = self.fields["Text Transformations"]["uppercase"].get()
        lowercase = self.fields["Text Transformations"]["lowercase"].get()
        remove_spaces = self.fields["Text Transformations"]["remove_spaces"].get()
        remove_symbols = self.fields["Text Transformations"]["remove_symbols"].get()
        keep_alphanumeric_spaces = self.fields["Text Transformations"]["keep_alphanumeric_spaces"].get()
        
        snippet_data: Dict[str, Any] = {
            "text": text,
            "min_delay": min_delay,
            "max_delay": max_delay,
            "backspace_probability": backspace_prob,
            "min_backspaces": min_backspaces,
            "max_backspaces": max_backspaces,
            "uppercase": uppercase,
            "lowercase": lowercase,
            "remove_spaces": remove_spaces,
            "remove_symbols": remove_symbols,
            "keep_alphanumeric_spaces": keep_alphanumeric_spaces,
            "hotkey": hotkey,
            "category": category,
            "history": [],
        }
        snippets[name] = snippet_data  # type: ignore[assignment]  # Add or update; extra UI keys not in backend SnippetData
        save_snippets(snippets)  # Save to file
        self.register_app_hotkeys()  # Update hotkey bindings
        self.refresh_list(name)  # Refresh and select the saved snippet
        self.set_status(f"Snippet '{name}' saved.")

    # Helper methods -------------------------------------------------
    def _get_selected_index(self) -> Optional[int]:
        sel_raw = self.listbox.curselection()  # type: ignore[no-untyped-call]
        try:
            selection = cast(Sequence[int], sel_raw)
            if selection:
                return int(selection[0])
        except Exception:
            return None
        return None

    def _get_selected_name(self) -> Optional[str]:
        idx = self._get_selected_index()
        if idx is None:
            return None
        item = str(self.listbox.get(idx))  # type: ignore[no-untyped-call]
        return item.split(" (")[0]

    def on_delete(self) -> None:
        """Deletes the selected snippet."""
        selected_name = self._get_selected_name()
        if selected_name:
            if messagebox.askyesno("Delete Snippet", f"Are you sure you want to delete snippet '{selected_name}'?"):
                del snippets[selected_name]
                save_snippets(snippets)
                self.register_app_hotkeys()  # Update hotkey bindings
                self.refresh_list()
                self.clear_fields()
                self.set_status(f"Snippet '{selected_name}' deleted.")
        else:
            self.set_status("Please select a snippet to delete.", warning=True)

    def on_test(self) -> None:
        """Tests the typing of the currently loaded snippet."""
        selected_name = self._get_selected_name()
        if selected_name:
            # Show info message to help the user prepare
            messagebox.showinfo(
                "Testing Snippet",
                "Click OK and focus your cursor where you want the text to be typed.\n\n"
                "You'll have 3 seconds to position your cursor after closing this dialog."
            )

            # Start a countdown thread for the typing
            def delayed_typing() -> None:
                # Countdown
                for i in range(3, 0, -1):
                    self.set_status(f"Typing will start in {i} seconds...", warning=True)
                    time.sleep(1)

                # Execute snippet
                self.set_status(f"Now typing '{selected_name}'...")
                execute_snippet(selected_name)
                # Update status when done
                self.master.after(1000, lambda: self.set_status(f"Typing test completed for: {selected_name}"))

            # Run the delayed typing in a separate thread
            threading.Thread(target=delayed_typing, daemon=True).start()
        else:
            self.set_status("Please select a snippet to test.", warning=True)

    def on_history(self) -> None:
        """Displays the typing history in a new window with improved layout and styling."""
        history_data = get_history()
        if not history_data:
            messagebox.showinfo("Typing History", "No typing history available.")
            return

        history_window = tk.Toplevel(self.master)
        history_window.title("Typing History")
        history_window.geometry("800x500")
        history_window.grab_set()
        history_window.focus_set()

        history_frame = ttk.Frame(history_window, padding="15 15 15 15")
        history_frame.pack(fill="both", expand=True)
        history_frame.rowconfigure(0, weight=0)
        history_frame.rowconfigure(1, weight=1)
        history_frame.rowconfigure(2, weight=0)
        history_frame.columnconfigure(0, weight=1)

        header_label = ttk.Label(
            history_frame,
            text="Typing History",
            font=("Segoe UI", 14, "bold"),
            padding="0 0 0 10"
        )
        header_label.grid(row=0, column=0, sticky="w", pady=(0, 15))

        table_frame = ttk.Frame(history_frame)
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        columns = ("snippet", "timestamp", "text")
        history_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )
        history_tree.heading("snippet", text="Snippet Name")
        history_tree.heading("timestamp", text="Timestamp")
        history_tree.heading("text", text="Typed Text")
        history_tree.column("snippet", width=150, minwidth=100)
        history_tree.column("timestamp", width=150, minwidth=150)
        history_tree.column("text", width=450, minwidth=200)

        y_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=history_tree.yview)  # type: ignore[arg-type]
        x_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=history_tree.xview)  # type: ignore[arg-type]
        history_tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        history_tree.grid(row=0, column=0, sticky="nsew")
        y_scrollbar.grid(row=0, column=1, sticky="ns")
        x_scrollbar.grid(row=1, column=0, sticky="ew")

        for i, entry in enumerate(history_data):
            timestamp_str = entry['timestamp']
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
                formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                formatted_timestamp = timestamp_str
            snippet_name = entry['snippet_name']
            typed_text = entry['typed_text']
            tag = "even" if i % 2 == 0 else "odd"
            history_tree.insert("", tk.END, values=(snippet_name, formatted_timestamp, typed_text), tags=(tag,))

        history_tree.tag_configure("even", background="#f5f5f5" if self.theme_mode == "light" else "#3c3f41")
        history_tree.tag_configure("odd", background="white" if self.theme_mode == "light" else "#313335")

        button_frame = ttk.Frame(history_frame)
        button_frame.grid(row=2, column=0, pady=(15, 0), sticky="e")
        export_button = ttk.Button(
            button_frame,
            text="Export History",
            style="Info.TButton",
            command=lambda: self._export_history(history_data)
        )
        export_button.grid(row=0, column=0, padx=(0, 10))
        clear_button = ttk.Button(
            button_frame,
            text="Clear History",
            style="Danger.TButton",
            command=self.on_clear_history
        )
        clear_button.grid(row=0, column=1)
    
    def _export_history(self, history_data: Sequence[Any]) -> None:
        """Export history to a text file."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write("Auto Typer - Typing History\n")
                    f.write("=========================\n\n")
                    
                    for entry in history_data:
                        timestamp_str = entry.get('timestamp', 'Unknown time')
                        snippet_name = entry.get('snippet_name', 'Unknown snippet')
                        typed_text = entry.get('typed_text', '')
                        
                        f.write(f"Snippet: {snippet_name}\n")
                        f.write(f"Timestamp: {timestamp_str}\n")
                        f.write(f"Text: {typed_text}\n")
                        f.write("---------------------------\n\n")
                
                self.set_status(f"History exported to {os.path.basename(filepath)}")
            except Exception as e:
                self.set_status(f"Error exporting history: {e}", error=True)
                messagebox.showerror("Export Error", f"Failed to export history: {e}")

    def on_clear_history(self) -> None:
        """Clears the typing history."""
        if messagebox.askyesno("Clear History", "Are you sure you want to clear the entire typing history?"):
            if clear_history():
                self.set_status("Typing history cleared successfully.")
                messagebox.showinfo("History Cleared", "The typing history has been cleared.")
                # Close the history window if it's open
                for widget in self.master.winfo_children():
                    if isinstance(widget, tk.Toplevel) and widget.title() == "Typing History":
                        widget.destroy()
                        break
            else:
                self.set_status("Failed to clear typing history.", error=True)
                messagebox.showerror("Error", "Failed to clear typing history.")

    def clear_fields(self) -> None:
        """Clears the input fields in the form."""
        self.fields["Name"].config(state="normal")  # Make editable to clear
        self.fields["Name"].delete(0, tk.END)
        self.fields["Name"].config(state="readonly")  # Make it readonly again
        
        self.fields["Category"].delete(0, tk.END)
        self.fields["Text"].delete("1.0", tk.END)
        
        # Clear numerical fields with defaults
        self.fields["Min Delay (s)"].delete(0, tk.END)
        self.fields["Min Delay (s)"].insert(0, "0.01")  # Set default
        
        self.fields["Max Delay (s)"].delete(0, tk.END)
        self.fields["Max Delay (s)"].insert(0, "0.05")  # Set default
        
        self.fields["Backspace Prob (0-1)"].delete(0, tk.END)
        self.fields["Backspace Prob (0-1)"].insert(0, "0.0")  # Set default
        
        self.fields["Min Backspaces"].delete(0, tk.END)
        self.fields["Min Backspaces"].insert(0, "1")  # Set default
        
        self.fields["Max Backspaces"].delete(0, tk.END)
        self.fields["Max Backspaces"].insert(0, "3")  # Set default
        
        # Clear text transformation checkboxes
        self.fields["Text Transformations"]["uppercase"].set(False)
        self.fields["Text Transformations"]["lowercase"].set(False)
        self.fields["Text Transformations"]["remove_spaces"].set(False)
        self.fields["Text Transformations"]["remove_symbols"].set(False)
        self.fields["Text Transformations"]["keep_alphanumeric_spaces"].set(False)
        
        # Clear hotkey
        self._set_hotkey_field_text("")
        
        self.set_status("Fields cleared.")

    def on_import(self) -> None:
        """Imports snippets from a JSON file."""
        filepath = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if filepath:
            imported_snippets = import_snippets(filepath)  # Call the import function
            if imported_snippets is not None:
                global snippets  # Access the global snippets variable
                snippets.update(imported_snippets)  # Merge imported snippets
                save_snippets(snippets)  # Save the updated snippets
                self.register_app_hotkeys()  # Update hotkeys
                self.refresh_list()  # Refresh the list
                self.set_status(f"Imported snippets from '{os.path.basename(filepath)}'.")
            else:
                self.set_status("Import failed. Invalid file or format.", error=True)

    def on_export(self) -> None:
        """Exports snippets to a JSON file."""
        if not snippets:
            messagebox.showinfo("No Snippets", "There are no snippets to export.")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if filepath:
            if export_snippets(filepath, snippets):  # Call the export function
                self.set_status(f"Exported snippets to '{os.path.basename(filepath)}'.")
            else:
                self.set_status("Export failed.", error=True)

    def on_clear_all(self) -> None:
        """Clears all snippets after confirmation."""
        if messagebox.askyesno("Clear All", "Are you sure you want to clear ALL snippets? This action cannot be undone."):
            if clear_all_snippets():
                global snippets
                snippets = {}  # Clear the global variable
                self.register_app_hotkeys()
                self.refresh_list()
                self.clear_fields()
                self.set_status("All snippets cleared.")
            else:
                self.set_status("Failed to clear all snippets.", error=True)

    def toggle_theme(self) -> None:
        """Toggles between dark and light themes."""
        self.theme_mode = "dark" if self.theme_mode == "light" else "light"
        self.configure_styles()  # Re-apply styles
        self.set_status(f"Switched to {self.theme_mode} mode.")

    def register_app_hotkeys(self) -> None:
        """Registers all snippet hotkeys using the backend function."""
        register_hotkeys(snippets)  # Call the register_hotkeys function from backend.py

    def _check_updates_thread(self) -> None:
        """Checks for updates in a separate thread."""
        try:
            # This is a placeholder. A real implementation would involve network requests.
            time.sleep(2)  # Simulate a delay
            update_message = check_for_update()
            if update_message:
                # Use thread-safe method to update UI from a background thread
                self.master.after(0, lambda: self.set_status(update_message))  # Use master.after
        except Exception as e:
            # Silently handle errors in update check - don't disrupt user experience
            print(f"[frontend] Error checking for updates: {e}")
            # Do not show error to user as this is a background task

    def set_status(self, message: str, warning: bool = False, error: bool = False) -> None:
        """Sets the text and color of the status bar."""
        self.status.config(text=message)
        if warning:
            self.status.config(foreground="#E65100")  # Orange/Amber
        elif error:
            self.status.config(foreground="red" if self.theme_mode == "light" else "#F44336")
        else:
            # Reset to default status color
            default_fg = "#333333" if self.theme_mode == "light" else "#cccccc"
            self.status.config(foreground=default_fg)
        # print(f"[Status] {message}") # Optional: log status messages

    def show_about(self) -> None:
        """Displays the About window."""
        messagebox.showinfo("About Auto Typing App",
                            "Auto Typing App v1.2\n\n"
                            "Features:\n"
                            "- Create text snippets\n"
                            "- Assign global hotkeys\n"
                            "- Adjustable typing delay\n"
                            "- Backspace simulation\n"
                            "- Import/Export snippets\n\n"
                            "Developed by Teja")

    def on_close(self) -> None:
        """Handles window closing event and unhooks global listener."""
        print("[frontend] Application closing.")
        self._stop_hotkey_capture()  # Ensure the global listener is stopped
        # keyboard.unhook_all() # This would unhook *all* listeners, including backend. Be careful.
        self.master.destroy()


if __name__ == "__main__":
    # Print current working directory for debugging
    print(f"[frontend] Current working directory: {os.getcwd()}")
    
    # Create and run the application
    root = tk.Tk()
    app = AutoTypingApp(root)
    
    # The protocol for WM_DELETE_WINDOW is how you hook into the window close event
    # (This is already handled in the AutoTypingApp class's on_close method)
    root.mainloop()
