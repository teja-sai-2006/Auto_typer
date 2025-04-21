# Ensure backend.py is in the same directory as this file.
from datetime import datetime
import os
import random
import threading
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font as tkfont  # Import font module
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

# --- Global Snippet Data ---
# Load snippets at the start, handle potential errors during loading
try:
    snippets = load_snippets() or {}

    # --- Add a default snippet if none are loaded ---
    if not snippets:
        print("[frontend] No snippets found or error loading. Adding a sample snippet.")
        # Define a sample snippet
        sample_snippet_name = "Welcome Message"
        sample_snippet_data = {
            "text": "Hello! This is a sample snippet. You can edit or delete it.",
            "min_delay": 0.02,
            "max_delay": 0.08,
            "backspace_probability": 0.1,
            "min_backspaces": 1,
            "max_backspaces": 2,
            "hotkey": "",  # No default hotkey assigned, user can set one
            "category": "Samples",
            "history": []
        }
        snippets[sample_snippet_name] = sample_snippet_data
        # Uncomment the line below if you want the sample snippet to be saved to snippets.json automatically on first run
        # save_snippets(snippets)
    else:
        print(f"[frontend] Loaded {len(snippets)} snippets from file.")
    # --- End default snippet logic ---

except Exception as e:
    messagebox.showerror("Load Error", f"Failed to load or initialize snippets:\n{e}\n\nStarting with an empty set.")
    snippets = {}


class AutoTypingApp(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master  # Store master window reference

        # --- Basic Window Setup ---
        master.title("Auto Typing App v1.1")
        master.geometry("950x650")  # Slightly larger for new fields
        master.minsize(700, 500)  # Set a minimum size
        # Configure resizing behavior
        master.rowconfigure(0, weight=1)  # Main content row
        master.columnconfigure(0, weight=1, minsize=200)  # Left panel (List)
        master.columnconfigure(1, weight=3, minsize=400)  # Right panel (Form)
        master.rowconfigure(2, weight=0)  # Status bar row

        self.grid(row=0, column=0, columnspan=2, sticky="nsew")  # Make main frame fill window

        # --- Widget Creation ---
        self._hotkey_listener_handle = None  # To store the temporary global hotkey listener handle
        self._captured_hotkey_parts = set()  # To store the parts of the captured hotkey combination
        # Create widgets BEFORE configuring their styles
        self.create_widgets()  # THIS CALL IS MOVED UP

        # --- Style and Theme ---
        self.style = ttk.Style()
        self.available_themes = self.style.theme_names()
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

        # Apply styles
        self.style.configure(".", background=bg_color, foreground=fg_color)
        self.style.configure("TFrame", background=bg_color)
        self.style.configure("TLabel", background=bg_color, foreground=fg_color)
        self.style.configure("TButton", background=button_bg, foreground=button_fg, padding=5)
        self.style.map("TButton", background=[('active', '#c0c0c0' if self.theme_mode == 'light' else '#6a6a6a')])
        self.style.configure("TEntry", fieldbackground=entry_bg, foreground=entry_fg, insertcolor=fg_color)
        self.style.configure("TCombobox", fieldbackground=entry_bg, foreground=entry_fg, insertcolor=fg_color)
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
        self.master.config(menu=menubar)

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
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.listbox.yview)
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

        # Define form fields
        # Added Backspace fields
        labels = ["Name", "Category", "Text", "Min Delay (s)", "Max Delay (s)",
                  "Backspace Prob (0-1)", "Min Backspaces", "Max Backspaces", "Hotkey"]
        self.fields = {}
        grid_row_index = 0

        for lbl in labels:
            ttk.Label(form_frame, text=f"{lbl}:").grid(row=grid_row_index, column=0, sticky="nw", pady=3, padx=(0, 10))

            if lbl == "Text":
                # Text widget with its own scrollbar
                text_frame = ttk.Frame(form_frame)
                text_frame.grid(row=grid_row_index, column=1, sticky="nsew", pady=2)
                text_frame.rowconfigure(0, weight=1)
                text_frame.columnconfigure(0, weight=1)
                form_frame.rowconfigure(grid_row_index, weight=1)  # Allow text area to expand vertically

                txt_widget = tk.Text(text_frame, height=8, width=40, wrap="word",
                                     undo=True)  # Start with reasonable size, add undo
                txt_widget.grid(row=0, column=0, sticky="nsew")
                txt_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=txt_widget.yview)
                txt_scrollbar.grid(row=0, column=1, sticky="ns")
                txt_widget.config(yscrollcommand=txt_scrollbar.set)
                self.fields[lbl] = txt_widget
            elif lbl == "Category":
                # Combobox for categories
                combo_widget = ttk.Combobox(form_frame, values=self.get_categories())
                combo_widget.grid(row=grid_row_index, column=1, sticky="ew", pady=2)
                self.fields[lbl] = combo_widget
            elif lbl == "Hotkey":
                # Special handling for hotkey entry - Now uses global capture on FocusOut
                hotkey_entry = ttk.Entry(form_frame, state='readonly')  # Make it readonly, we'll update it
                hotkey_entry.grid(row=grid_row_index, column=1, sticky="ew", pady=2)
                # Bind events for capturing hotkeys using global listener
                hotkey_entry.bind("<FocusIn>", self._start_hotkey_capture)
                hotkey_entry.bind("<FocusOut>", self._stop_hotkey_capture)
                # Bind Backspace directly for clearing when focused
                hotkey_entry.bind("<BackSpace>", self._clear_hotkey_field)

                self.fields[lbl] = hotkey_entry
            else:
                # Standard entry for other fields
                entry_widget = ttk.Entry(form_frame)
                entry_widget.grid(row=grid_row_index, column=1, sticky="ew", pady=2)
                self.fields[lbl] = entry_widget

            grid_row_index += 1

        # Add a help text for backspace simulation
        backspace_help_text = "Backspace simulation: When enabled, the app will occasionally delete characters and retype them to simulate human typing."
        backspace_help_label = ttk.Label(form_frame, text=backspace_help_text, font=("Segoe UI", 8), wraplength=400)
        backspace_help_label.grid(row=grid_row_index, column=0, columnspan=2, sticky="w", pady=(10, 0))

        # --- Button Bar ---
        button_frame = ttk.Frame(right_panel)
        button_frame.grid(row=1, column=0, sticky="ew")

        buttons = [
            ("Add / Save", self.on_save),  # Combined Add/Save
            ("Delete", self.on_delete),
            ("Test Typing", self.on_test),
            ("Show History", self.on_history),
            ("Clear Fields", self.clear_fields),
        ]

        for i, (txt, cmd) in enumerate(buttons):
            button = ttk.Button(button_frame, text=txt, command=cmd)
            button.grid(row=0, column=i, padx=5, pady=5)
            # button_frame.columnconfigure(i, weight=1) # Distribute buttons evenly (optional)

        # --- Status Bar ---
        self.status = ttk.Label(self.master, text="Ready", relief="sunken", anchor="w", padding="5 2")
        self.status.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(5, 0))

        # --- Footer ---
        footer_frame = ttk.Frame(self.master)
        footer_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        footer_frame.columnconfigure(0, weight=1)
        self.made_by_label = ttk.Label(footer_frame, text="Auto Typing App by Teja", font=("Segoe UI", 8), anchor="e")
        self.made_by_label.grid(row=0, column=0, sticky='e', padx=10)

    # --- Hotkey Capture Functions (Fixed for proper combination capture) ---

    def _start_hotkey_capture(self, event=None):
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

    def _on_global_key_event_monitor(self, event):
        """Callback for the global keyboard listener - builds the hotkey string."""
        # Only process key down events to build the combination
        if event.event_type == keyboard.KEY_DOWN:
            name = event.name.lower()  # Get the key name
            
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
                modifiers = []
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

    def _stop_hotkey_capture(self, event=None):
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

    def _set_hotkey_field_text(self, text):
        """Thread-safe way to update the Hotkey entry field."""
        try:
            hotkey_entry = self.fields["Hotkey"]
            # Use master.after to schedule the update on the main Tkinter thread
            self.master.after(0, lambda: self._update_hotkey_entry_widget(hotkey_entry, text))
        except Exception as e:
            print(f"[frontend] Error scheduling hotkey field update: {e}")

    def _update_hotkey_entry_widget(self, widget, text):
        """Performs the actual update of the Hotkey entry widget."""
        try:
            widget.config(state='normal')  # Enable to modify
            widget.delete(0, tk.END)
            widget.insert(0, text)
            widget.config(state='readonly')  # Disable editing
        except Exception as e:
            print(f"[frontend] Error updating hotkey entry widget: {e}")

    def _clear_hotkey_field(self, event=None):
        """Clears the hotkey field and stops listener when Backspace is pressed while focused."""
        if self._hotkey_listener_handle:
            keyboard.unhook(self._hotkey_listener_handle)
            self._hotkey_listener_handle = None
        
        self._captured_hotkey_parts = set()  # Clear the captured parts set
        self._set_hotkey_field_text("")  # Clear the field visually
        self.set_status("Hotkey field cleared.")
        return "break"  # Prevent default backspace

    # --- Remaining Event Handlers & Actions (Same as before with value handling and TypeError fixes) ---

    def get_categories(self):
        """Extracts unique categories from snippets."""
        categories = {""}  # Start with an empty category option
        for data in snippets.values():
            cat = data.get("category", "").strip()
            if cat:
                categories.add(cat)
        return sorted(list(categories))

    def refresh_list(self, select_name=None):
        """Refreshes the snippet listbox, optionally selecting an item."""
        search_term = self.search_var.get().lower()
        self.listbox.delete(0, tk.END)
        for name, data in snippets.items():
            if search_term in name.lower():
                category = data.get("category", "").strip()  # Get category, default to ""
                display_text = f"{name} ({category})" if category else name
                self.listbox.insert(tk.END, display_text)
        if select_name:
            for i in range(self.listbox.size()):
                if select_name == self.listbox.get(i).split(" (")[0]:  # Compare only the name part
                    self.listbox.selection_set(i)
                    break

    def on_listbox_select(self, event=None):
        """Handles selection of a snippet from the listbox."""
        if self.listbox.curselection():
            selected_index = self.listbox.curselection()[0]
            selected_item = self.listbox.get(selected_index)
            selected_name = selected_item.split(" (")[0]  # Extract snippet name
            self.load_snippet_data(selected_name)

    def load_snippet_data(self, name):
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

            self._set_hotkey_field_text(snippet.get("hotkey", "")) # Use helper to update

            self.set_status(f"Loaded snippet: {name}")
        else:
            self.clear_fields()
            self.set_status(f"Snippet not found: {name}", error=True)

    def on_save(self):
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

        snippet_data = {
            "text": text,
            "min_delay": min_delay,
            "max_delay": max_delay,
            "backspace_probability": backspace_prob,
            "min_backspaces": min_backspaces,
            "max_backspaces": max_backspaces,
            "hotkey": hotkey,
            "category": category,
            "history": [],
        }

        snippets[name] = snippet_data  # Add or update
        save_snippets(snippets)  # Save to file
        self.register_app_hotkeys()  # Update hotkey bindings
        self.refresh_list(name)  # Refresh and select the saved snippet
        self.set_status(f"Snippet '{name}' saved.")

    def on_delete(self):
        """Deletes the selected snippet."""
        if self.listbox.curselection():
            selected_index = self.listbox.curselection()[0]
            selected_item = self.listbox.get(selected_index)
            selected_name = selected_item.split(" (")[0]  # Extract snippet name

            if messagebox.askyesno("Delete Snippet", f"Are you sure you want to delete snippet '{selected_name}'?"):
                del snippets[selected_name]
                save_snippets(snippets)
                self.register_app_hotkeys()  # Update hotkey bindings
                self.refresh_list()
                self.clear_fields()
                self.set_status(f"Snippet '{selected_name}' deleted.")
        else:
            self.set_status("Please select a snippet to delete.", warning=True)

    def on_test(self):
        """Tests the typing of the currently loaded snippet."""
        if self.listbox.curselection():
            selected_index = self.listbox.curselection()[0]
            selected_item = self.listbox.get(selected_index)
            selected_name = selected_item.split(" (")[0]  # Extract snippet name
            # Call the execute_snippet function from the backend
            execute_snippet(selected_name)
            self.set_status(f"Typing test started for snippet: {selected_name}")
        else:
            self.set_status("Please select a snippet to test.", warning=True)

    def on_history(self):
        """Displays the typing history in a new window."""
        history_data = get_history()
        if not history_data:
            messagebox.showinfo("Typing History", "No typing history available.")
            return

        history_window = tk.Toplevel(self.master)
        history_window.title("Typing History")
        history_window.geometry("600x400")
        history_window.transient(self.master)  # Make it a transient window

        history_frame = ttk.Frame(history_window, padding="10 10 10 10")
        history_frame.pack(fill="both", expand=True)
        history_frame.rowconfigure(0, weight=1)
        history_frame.columnconfigure(0, weight=1)

        history_listbox = tk.Listbox(history_frame, exportselection=False, activestyle='none')
        history_listbox.grid(row=0, column=0, sticky="nsew")
        history_scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=history_listbox.yview)
        history_scrollbar.grid(row=0, column=1, sticky="ns")
        history_listbox.config(yscrollcommand=history_scrollbar.set)

        for entry in history_data:
            timestamp_str = entry['timestamp']
            try:
                # Attempt to parse the timestamp string
                timestamp = datetime.fromisoformat(timestamp_str)
                # Format the datetime object for display
                formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                # Handle the case where the timestamp is not in ISO format
                formatted_timestamp = timestamp_str  # Use the original string
            snippet_name = entry['snippet_name']
            typed_text = entry['typed_text']
            history_listbox.insert(tk.END, f"Snippet: {snippet_name}, Timestamp: {formatted_timestamp}, Text: {typed_text[:50]}...")  # Limit displayed text

        clear_button = ttk.Button(history_frame, text="Clear History", command=self.on_clear_history)
        clear_button.grid(row=1, column=0, pady=10, sticky="ew")

    def on_clear_history(self):
        """Clears the typing history."""
        if messagebox.askyesno("Clear History", "Are you sure you want to clear the entire typing history?"):
            if clear_history():  # Call the clear_history function from backend.py
                messagebox.showinfo("History Cleared", "Typing history cleared successfully.")
            else:
                messagebox.showerror("Error", "Failed to clear typing history.")

    def clear_fields(self):
        """Clears the input fields in the form."""
        self.fields["Name"].config(state="normal")  # Make editable to clear
        self.fields["Name"].delete(0, tk.END)
        self.fields["Name"].config(state="readonly")  # Make it readonly again
        self.fields["Category"].delete(0, tk.END)
        self.fields["Text"].delete("1.0", tk.END)
        self.fields["Min Delay (s)"].delete(0, tk.END)
        self.fields["Max Delay (s)"].delete(0, tk.END)
        self.fields["Backspace Prob (0-1)"].delete(0, tk.END)
        self.fields["Min Backspaces"].delete(0, tk.END)
        self.fields["Max Backspaces"].delete(0, tk.END)
        self._set_hotkey_field_text("")
        self.set_status("Fields cleared.")

    def on_import(self):
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

    def on_export(self):
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

    def on_clear_all(self):
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

    def toggle_theme(self):
        """Toggles between dark and light themes."""
        self.theme_mode = "dark" if self.theme_mode == "light" else "light"
        self.configure_styles()  # Re-apply styles
        self.set_status(f"Switched to {self.theme_mode} mode.")

    def register_app_hotkeys(self):
        """Registers all snippet hotkeys using the backend function."""
        register_hotkeys(snippets)  # Call the register_hotkeys function from backend.py

    def _check_updates_thread(self):
        """Checks for updates in a separate thread."""
        # This is a placeholder.  A real implementation would involve network requests.
        time.sleep(2)  # Simulate a delay
        update_message = check_for_update()
        if update_message:
            self.master.after(0, lambda: self.set_status(update_message))  # Use master.after

    def set_status(self, message, warning=False, error=False):
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

    def show_about(self):
        """Displays the About window."""
        messagebox.showinfo("About Auto Typing App",
                            "Auto Typing App v1.1\n\n"
                            "Features:\n"
                            "- Create text snippets\n"
                            "- Assign global hotkeys\n"
                            "- Adjustable typing delay\n"
                            "- Backspace simulation\n"
                            "- Import/Export snippets\n\n"
                            "Developed by Teja")

    def on_close(self):
        """Handles window closing event and unhooks global listener."""
        print("[frontend] Application closing.")
        self._stop_hotkey_capture()  # Ensure the global listener is stopped
        # keyboard.unhook_all() # This would unhook *all* listeners, including backend. Be careful.
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = AutoTypingApp(root)
    email_part1 = tk.Label(root, text="tejasai13052006@gmail.com")
    email_part1.place(relx=0.0, rely=1.0, anchor='sw')
    # The protocol for WM_DELETE_WINDOW is how you hook into the window close event
    root.mainloop()
