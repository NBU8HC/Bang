import os
import re
import sys
import json
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk
from threading import Thread
from datetime import datetime

class MultiDirectoryDialog:
    def __init__(self, parent):
        self.parent = parent
        self.selected_directories = []
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Select Multiple Directories")
        self.dialog.geometry("700x700")
        self.dialog.grab_set()  # Make dialog modal
        
        # Load parent folder history
        self.config_file = os.path.join(os.path.dirname(__file__), 'add_parameter_config.json')
        self.parent_folder_history = []
        self.load_parent_history()
        
        self.setup_dialog()
        
    def setup_dialog(self):
        # Main frame
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        instruction_text = "Select multiple directories:\n• Use 'Browse Parent Folder' to navigate to a parent directory\n• Use Ctrl+A to select all folders\n• Use Ctrl+Click or Shift+Click for multiple selection"
        tk.Label(main_frame, text=instruction_text, font=('Arial', 10), 
                justify=tk.LEFT, fg="blue").pack(anchor='w', pady=(0, 15))
        
        # Current path frame
        path_frame = tk.Frame(main_frame)
        path_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(path_frame, text="Parent Folder:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        
        # Combobox for parent folder with history
        path_combo_frame = tk.Frame(path_frame)
        path_combo_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 10))
        
        self.current_path_var = tk.StringVar(value="")
        self.path_combo = ttk.Combobox(path_combo_frame, textvariable=self.current_path_var, 
                                       font=('Arial', 9))
        self.path_combo['values'] = self.parent_folder_history
        if self.parent_folder_history:
            self.current_path_var.set(self.parent_folder_history[0])
            self.load_subdirectories(self.parent_folder_history[0])
        self.path_combo.pack(fill=tk.X)
        self.path_combo.bind('<<ComboboxSelected>>', self.on_path_selected)
        
        # Browse button
        tk.Button(path_frame, text="Browse", command=self.browse_parent_folder, 
                 width=10, bg='lightgreen').pack(side=tk.LEFT)
        
        # Directory listbox with folders from selected parent directory
        tk.Label(main_frame, text="Available Folders in Parent Directory:", 
                font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 5))
        
        # Frame for available directories
        available_frame = tk.Frame(main_frame)
        available_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.available_listbox = tk.Listbox(available_frame, selectmode=tk.EXTENDED, height=8)
        available_scrollbar = tk.Scrollbar(available_frame, orient=tk.VERTICAL, 
                                         command=self.available_listbox.yview)
        self.available_listbox.configure(yscrollcommand=available_scrollbar.set)
        
        self.available_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        available_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind keyboard shortcuts
        self.available_listbox.bind('<Control-a>', self.select_all_available)
        self.available_listbox.bind('<Return>', self.add_selected_directories)
        self.available_listbox.bind('<Double-Button-1>', self.add_selected_directories)
        
        # Transfer buttons
        transfer_frame = tk.Frame(main_frame)
        transfer_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Button(transfer_frame, text="Add Selected Folders →", command=self.add_selected_directories, 
                 width=20, bg='lightblue').pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(transfer_frame, text="Add All Folders →", command=self.add_all_directories, 
                 width=15).pack(side=tk.LEFT, padx=(0, 5))
        
        # Selected directories
        tk.Label(main_frame, text="Selected Directories:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 5))
        
        selected_frame = tk.Frame(main_frame)
        selected_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.selected_listbox = tk.Listbox(selected_frame, selectmode=tk.EXTENDED, height=6)
        selected_scrollbar = tk.Scrollbar(selected_frame, orient=tk.VERTICAL, 
                                        command=self.selected_listbox.yview)
        self.selected_listbox.configure(yscrollcommand=selected_scrollbar.set)
        
        self.selected_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        selected_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind keyboard shortcuts for selected list
        self.selected_listbox.bind('<Control-a>', self.select_all_selected)
        self.selected_listbox.bind('<Delete>', self.remove_selected_directories)
        
        # Management buttons
        mgmt_frame = tk.Frame(main_frame)
        mgmt_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Button(mgmt_frame, text="Remove Selected", command=self.remove_selected_directories, 
                 width=15).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(mgmt_frame, text="Clear All", command=self.clear_all, width=10).pack(side=tk.LEFT)
        
        # Count label
        self.count_label = tk.Label(mgmt_frame, text="Selected: 0 directories", fg="blue", 
                                   font=('Arial', 10, 'bold'))
        self.count_label.pack(side=tk.RIGHT)
        
        # Dialog buttons
        dialog_button_frame = tk.Frame(main_frame)
        dialog_button_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(dialog_button_frame, text="OK", command=self.ok_clicked, 
                 width=10, bg='lightgreen', font=('Arial', 10, 'bold')).pack(side=tk.RIGHT, padx=(5, 0))
        tk.Button(dialog_button_frame, text="Cancel", command=self.cancel_clicked, 
                 width=10, font=('Arial', 10)).pack(side=tk.RIGHT)
        
        # Center the dialog
        self.center_dialog()
    
    def load_parent_history(self):
        """Load parent folder history from config file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                if 'parent_folder_history' in config:
                    self.parent_folder_history = config['parent_folder_history']
        except Exception as e:
            pass
    
    def save_parent_history(self):
        """Save parent folder history to config file."""
        try:
            config = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            config['parent_folder_history'] = self.parent_folder_history
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            pass
    
    def on_path_selected(self, event=None):
        """Handle selection from dropdown."""
        selected_path = self.current_path_var.get()
        if selected_path and os.path.isdir(selected_path):
            self.load_subdirectories(selected_path)
        
    def center_dialog(self):
        self.dialog.transient(self.parent)
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
    def browse_parent_folder(self):
        """Browse for a parent directory and show its subdirectories."""
        parent_dir = filedialog.askdirectory(title="Select Parent Directory")
        if parent_dir:
            self.current_path_var.set(parent_dir)
            self.load_subdirectories(parent_dir)
            
            # Add to history
            if parent_dir not in self.parent_folder_history:
                self.parent_folder_history.insert(0, parent_dir)
                self.parent_folder_history = self.parent_folder_history[:10]  # Keep last 10
                self.path_combo['values'] = self.parent_folder_history
                self.save_parent_history()
            
    def load_subdirectories(self, parent_dir):
        """Load subdirectories of the parent directory."""
        self.available_listbox.delete(0, tk.END)
        try:
            items = os.listdir(parent_dir)
            directories = []
            for item in items:
                item_path = os.path.join(parent_dir, item)
                if os.path.isdir(item_path):
                    directories.append(item_path)
            
            directories.sort()
            for directory in directories:
                self.available_listbox.insert(tk.END, directory)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error reading directory: {str(e)}")
    
    def select_all_available(self, event=None):
        """Select all items in available listbox."""
        self.available_listbox.select_set(0, tk.END)
        return 'break'  # Prevent default behavior
    
    def select_all_selected(self, event=None):
        """Select all items in selected listbox."""
        self.selected_listbox.select_set(0, tk.END)
        return 'break'  # Prevent default behavior
        
    def add_selected_directories(self, event=None):
        """Add selected directories from available list to selected list."""
        selections = self.available_listbox.curselection()
        for index in selections:
            directory = self.available_listbox.get(index)
            if directory not in self.selected_directories:
                self.selected_directories.append(directory)
                self.selected_listbox.insert(tk.END, directory)
        self.update_count()
        
    def add_all_directories(self):
        """Add all directories from available list to selected list."""
        for i in range(self.available_listbox.size()):
            directory = self.available_listbox.get(i)
            if directory not in self.selected_directories:
                self.selected_directories.append(directory)
                self.selected_listbox.insert(tk.END, directory)
        self.update_count()
        
    def remove_selected_directories(self, event=None):
        """Remove selected directories from selected list."""
        selections = self.selected_listbox.curselection()
        for index in reversed(selections):  # Remove from end to avoid index issues
            directory = self.selected_listbox.get(index)
            self.selected_listbox.delete(index)
            self.selected_directories.remove(directory)
        self.update_count()
        
    def clear_all(self):
        """Clear all selected directories."""
        self.selected_listbox.delete(0, tk.END)
        self.selected_directories.clear()
        self.update_count()
        
    def update_count(self):
        count = len(self.selected_directories)
        self.count_label.config(text=f"Selected: {count} directories")
        
    def ok_clicked(self):
        self.dialog.destroy()
        
    def cancel_clicked(self):
        self.selected_directories.clear()
        self.dialog.destroy()

class SingleFolderDialog:
    """Dialog for selecting a single folder with dropdown history."""
    def __init__(self, parent, folder_history, config_file):
        self.parent = parent
        self.folder_history = folder_history
        self.config_file = config_file
        self.selected_folder = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Select Single Folder")
        self.dialog.geometry("600x200")
        self.dialog.grab_set()
        
        self.setup_dialog()
        
        # Center window
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self.dialog.wait_window()
    
    def setup_dialog(self):
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(main_frame, text="Select a folder:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 10))
        
        # Folder selection frame
        folder_frame = tk.Frame(main_frame)
        folder_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(folder_frame, text="Folder:", font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=(0, 10))
        
        # Combobox with history
        self.folder_var = tk.StringVar()
        self.folder_combo = ttk.Combobox(folder_frame, textvariable=self.folder_var, 
                                         font=('Segoe UI', 9), width=50)
        self.folder_combo['values'] = self.folder_history
        if self.folder_history:
            self.folder_var.set(self.folder_history[0])
        self.folder_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Browse button
        tk.Button(folder_frame, text="Browse", command=self.browse_folder,
                 bg='#2196F3', fg='white', font=('Segoe UI', 8, 'bold'),
                 relief=tk.FLAT, cursor='hand2', width=10).pack(side=tk.LEFT)
        
        # Action buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack()
        
        tk.Button(button_frame, text="OK", command=self.ok_clicked,
                 bg='#4CAF50', fg='white', font=('Segoe UI', 9, 'bold'),
                 relief=tk.FLAT, cursor='hand2', width=12, pady=6).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(button_frame, text="Cancel", command=self.cancel_clicked,
                 bg='#F44336', fg='white', font=('Segoe UI', 9, 'bold'),
                 relief=tk.FLAT, cursor='hand2', width=12, pady=6).pack(side=tk.LEFT)
    
    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Directory")
        if folder:
            self.folder_var.set(folder)
    
    def ok_clicked(self):
        folder = self.folder_var.get()
        if folder and os.path.exists(folder):
            self.selected_folder = folder
        self.dialog.destroy()
    
    def cancel_clicked(self):
        self.selected_folder = None
        self.dialog.destroy()
    
    def get_result(self):
        return self.selected_folder

class ParameterAdditionTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Parameter Addition Tool - Multi Directory")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Modern color scheme
        self.colors = {
            'bg': '#f0f0f0',
            'panel': '#ffffff',
            'primary': '#2196F3',
            'success': '#4CAF50',
            'warning': '#FF9800',
            'danger': '#F44336',
            'text': '#333333',
            'border': '#ddd'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Config file path
        self.config_file = os.path.join(os.path.dirname(__file__), 'add_parameter_config.json')
        
        self.selected_directories = []
        self.parameter_file_history = []
        self.search_term_history = []
        self.single_folder_history = []
        self.parameter_file = tk.StringVar(value="parameter_new")
        self.search_term = tk.StringVar(value="name of file need to find")
        self.found_files = []
        
        self.create_widgets()
        self.load_config()
        
        # Save config on window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def create_widgets(self):
        # Main frame with padding
        main_frame = tk.Frame(self.root, bg=self.colors['bg'], padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure([1, 3, 5, 7], weight=0)
        main_frame.rowconfigure(9, weight=3)
        
        # Parameter file selection
        tk.Label(main_frame, text="Select Parameter File:", font=('Segoe UI', 10, 'bold'),
                bg=self.colors['bg'], fg=self.colors['text']).grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        param_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        param_frame.grid(row=1, column=0, columnspan=3, sticky='ew', pady=(0, 15))
        param_frame.columnconfigure(0, weight=1)
        
        self.param_combo = ttk.Combobox(param_frame, textvariable=self.parameter_file, font=('Segoe UI', 9))
        self.param_combo.grid(row=0, column=0, sticky='ew', padx=(0, 10))
        tk.Button(param_frame, text="Browse", command=self.browse_parameter_file,
                 bg=self.colors['primary'], fg='white', font=('Segoe UI', 9, 'bold'),
                 relief=tk.FLAT, padx=15, pady=6, cursor='hand2').grid(row=0, column=1)
        
        # Search term
        tk.Label(main_frame, text="Filename Contains:", font=('Segoe UI', 10, 'bold'),
                bg=self.colors['bg'], fg=self.colors['text']).grid(row=2, column=0, sticky='w', pady=(0, 5))
        
        search_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        search_frame.grid(row=3, column=0, columnspan=3, sticky='ew', pady=(0, 15))
        search_frame.columnconfigure(0, weight=1)
        
        self.search_combo = ttk.Combobox(search_frame, textvariable=self.search_term, font=('Segoe UI', 9))
        self.search_combo.grid(row=0, column=0, sticky='ew', padx=(0, 10))
        
        # Multiple directories selection
        tk.Label(main_frame, text="Select Multiple Directories to Search:", font=('Segoe UI', 10, 'bold'),
                bg=self.colors['bg'], fg=self.colors['text']).grid(row=4, column=0, sticky='w', pady=(0, 5))
        
        dir_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        dir_frame.grid(row=5, column=0, columnspan=3, sticky='ew', pady=(0, 15))
        dir_frame.columnconfigure(0, weight=1)
        
        # Listbox to show selected directories
        listbox_frame = tk.Frame(dir_frame, bg=self.colors['panel'], relief=tk.SOLID, borderwidth=1)
        listbox_frame.grid(row=0, column=0, sticky='ew', padx=(0, 10))
        listbox_frame.columnconfigure(0, weight=1)
        
        self.directory_listbox = tk.Listbox(listbox_frame, height=4, font=('Segoe UI', 9),
                                           relief=tk.FLAT, bg=self.colors['panel'])
        self.directory_listbox.grid(row=0, column=0, sticky='ew')
        
        # Scrollbar for listbox
        listbox_scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.directory_listbox.yview)
        listbox_scrollbar.grid(row=0, column=1, sticky='ns')
        self.directory_listbox.configure(yscrollcommand=listbox_scrollbar.set)
        
        # Buttons for directory management
        dir_buttons_frame = tk.Frame(dir_frame, bg=self.colors['bg'])
        dir_buttons_frame.grid(row=0, column=1, sticky='n')
        
        tk.Button(dir_buttons_frame, text="Select Folders", command=self.select_multiple_directories, 
                 width=14, bg=self.colors['primary'], fg='white', font=('Segoe UI', 8, 'bold'),
                 relief=tk.FLAT, cursor='hand2', pady=4).pack(pady=(0, 5))
        tk.Button(dir_buttons_frame, text="Add Single Folder", command=self.add_single_directory,
                 width=14, bg=self.colors['success'], fg='white', font=('Segoe UI', 8, 'bold'),
                 relief=tk.FLAT, cursor='hand2', pady=4).pack(pady=(0, 5))
        tk.Button(dir_buttons_frame, text="Remove Selected", command=self.remove_directory,
                 width=14, bg=self.colors['warning'], fg='white', font=('Segoe UI', 8, 'bold'),
                 relief=tk.FLAT, cursor='hand2', pady=4).pack(pady=(0, 5))
        tk.Button(dir_buttons_frame, text="Clear All", command=self.clear_directories,
                 width=14, bg=self.colors['danger'], fg='white', font=('Segoe UI', 8, 'bold'),
                 relief=tk.FLAT, cursor='hand2', pady=4).pack()
        
        # Directory count label
        self.dir_count_label = tk.Label(main_frame, text="Selected directories: 0",
                                       bg=self.colors['bg'], fg=self.colors['primary'],
                                       font=('Segoe UI', 9, 'bold'))
        self.dir_count_label.grid(row=6, column=0, sticky='w', pady=(0, 15))
        
        # Action buttons
        button_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        button_frame.grid(row=7, column=0, columnspan=3, pady=(10, 0))
        
        tk.Button(button_frame, text="1. Find Files", command=self.find_files, 
                 bg=self.colors['primary'], fg='white', width=15, font=('Segoe UI', 9, 'bold'),
                 relief=tk.FLAT, cursor='hand2', pady=6).pack(side=tk.LEFT, padx=(0, 10))
        self.add_btn = tk.Button(button_frame, text="2. Add Parameters", command=self.add_parameters, 
                                state=tk.DISABLED, bg=self.colors['success'], fg='white',
                                width=15, font=('Segoe UI', 9, 'bold'),
                                relief=tk.FLAT, cursor='hand2', pady=6)
        self.add_btn.pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(button_frame, text="Exit", command=self.root.quit, width=10,
                 bg=self.colors['danger'], fg='white', font=('Segoe UI', 9, 'bold'),
                 relief=tk.FLAT, cursor='hand2', pady=6).pack(side=tk.RIGHT)
        
        # Results text area
        tk.Label(main_frame, text="Results:", font=('Segoe UI', 10, 'bold'),
                bg=self.colors['bg'], fg=self.colors['text']).grid(row=8, column=0, sticky='w', pady=(20, 5))
        
        text_frame = tk.Frame(main_frame, bg=self.colors['panel'], relief=tk.SOLID, borderwidth=1)
        text_frame.grid(row=9, column=0, columnspan=3, sticky='nsew', pady=(0, 10))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.log_display = tk.Text(text_frame, height=12, wrap=tk.WORD, font=('Segoe UI', 9),
                                   relief=tk.FLAT, bg=self.colors['panel'])
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.log_display.yview)
        self.log_display.configure(yscrollcommand=scrollbar.set)
        
        self.log_display.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(9, weight=1)
    
    def load_config(self):
        """Load saved configuration from JSON file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                # Load parameter file history
                if 'parameter_file_history' in config:
                    self.parameter_file_history = config['parameter_file_history']
                    self.param_combo['values'] = self.parameter_file_history
                    if self.parameter_file_history:
                        self.parameter_file.set(self.parameter_file_history[0])
                
                # Load search term history
                if 'search_term_history' in config:
                    self.search_term_history = config['search_term_history']
                    self.search_combo['values'] = self.search_term_history
                    if self.search_term_history:
                        self.search_term.set(self.search_term_history[0])
                
                # Load single folder history
                if 'single_folder_history' in config:
                    self.single_folder_history = config['single_folder_history']
                
                # Load directories
                if 'directories' in config:
                    for directory in config['directories']:
                        if os.path.isdir(directory) and directory not in self.selected_directories:
                            self.selected_directories.append(directory)
                            self.directory_listbox.insert(tk.END, directory)
                    self.update_directory_count()
                    
                self.log(f"Loaded configuration: {len(self.selected_directories)} directories")
        except Exception as e:
            self.log(f"Could not load config: {e}")
    
    def save_config(self):
        """Save current configuration to JSON file."""
        try:
            # Update history lists
            param_file = self.parameter_file.get()
            if param_file and param_file not in self.parameter_file_history:
                self.parameter_file_history.insert(0, param_file)
                self.parameter_file_history = self.parameter_file_history[:10]  # Keep last 10
            
            search_term = self.search_term.get()
            if search_term and search_term not in self.search_term_history:
                self.search_term_history.insert(0, search_term)
                self.search_term_history = self.search_term_history[:10]  # Keep last 10
            
            config = {
                'parameter_file_history': self.parameter_file_history,
                'search_term_history': self.search_term_history,
                'single_folder_history': self.single_folder_history,
                'directories': self.selected_directories
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Could not save config: {e}")
    
    def on_closing(self):
        """Handle window closing event."""
        self.save_config()
        self.root.destroy()
    
    def browse_parameter_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Parameter File",
            filetypes=(("Text files", "*.txt"), ("All Files", "*.*"))
        )
        if file_path:
            self.parameter_file.set(file_path)
            # Add to history
            if file_path not in self.parameter_file_history:
                self.parameter_file_history.insert(0, file_path)
                self.parameter_file_history = self.parameter_file_history[:10]
                self.param_combo['values'] = self.parameter_file_history
            self.save_config()
    
    def select_multiple_directories(self):
        """Open dialog to select multiple directories at once."""
        dialog = MultiDirectoryDialog(self.root)
        self.root.wait_window(dialog.dialog)
        
        # Add new directories to the existing list
        for directory in dialog.selected_directories:
            if directory not in self.selected_directories:
                self.selected_directories.append(directory)
                self.directory_listbox.insert(tk.END, directory)
        
        self.update_directory_count()
        self.save_config()

    def add_single_directory(self):
        """Add a single directory to the list."""
        # Show dialog with dropdown history
        dialog = SingleFolderDialog(self.root, self.single_folder_history, self.config_file)
        directory_path = dialog.get_result()
        
        if directory_path and directory_path not in self.selected_directories:
            self.selected_directories.append(directory_path)
            self.directory_listbox.insert(tk.END, directory_path)
            self.update_directory_count()
            
            # Update history
            if directory_path not in self.single_folder_history:
                self.single_folder_history.insert(0, directory_path)
                self.single_folder_history = self.single_folder_history[:10]
            
            self.save_config()

    def remove_directory(self):
        """Remove selected directory from the list."""
        selection = self.directory_listbox.curselection()
        if selection:
            index = selection[0]
            self.directory_listbox.delete(index)
            del self.selected_directories[index]
            self.update_directory_count()
            self.save_config()

    def clear_directories(self):
        """Clear all selected directories."""
        self.directory_listbox.delete(0, tk.END)
        self.selected_directories.clear()
        self.update_directory_count()
        self.save_config()

    def update_directory_count(self):
        """Update the directory count label."""
        count = len(self.selected_directories)
        self.dir_count_label.config(text=f"Selected directories: {count}")
    
    def log(self, message):
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_display.insert(tk.END, f"{timestamp} - {message}\n")
        self.log_display.see(tk.END)
        self.root.update_idletasks()
    
    def validate_inputs(self):
        """Validate user inputs."""
        search_term = self.search_term.get().strip()
        
        if not search_term:
            messagebox.showerror("Error", "Please enter a filename search term.")
            return False
        
        if not self.selected_directories:
            messagebox.showerror("Error", "Please select at least one directory.")
            return False
        
        # Validate all directories exist
        invalid_dirs = [d for d in self.selected_directories if not os.path.isdir(d)]
        if invalid_dirs:
            messagebox.showerror("Error", f"Invalid directories found:\n{chr(10).join(invalid_dirs)}")
            return False
        
        return True
    
    def find_files(self):
        if not self.validate_inputs():
            return
            
        self.log_display.delete(1.0, tk.END)
        self.found_files = []
        self.add_btn.config(state=tk.DISABLED)
        
        search_term = self.search_term.get().strip()
        
        # Add search term to history
        if search_term not in self.search_term_history:
            self.search_term_history.insert(0, search_term)
            self.search_term_history = self.search_term_history[:10]
            self.search_combo['values'] = self.search_term_history
        
        self.save_config()
        
        self.log(f"Searching for files with '{search_term}' in filename across {len(self.selected_directories)} directories...")
        
        # Do the search in a separate thread to keep UI responsive
        Thread(target=self.search_thread, args=(search_term,)).start()
    
    def search_thread(self, search_term):
        try:
            total_file_count = 0
            search_term_lower = search_term.lower()  # Case-insensitive search
            
            for directory in self.selected_directories:
                self.log(f"\nSearching in directory: {directory}")
                dir_file_count = 0
                dir_found_files = []
                
                for root, _, files in os.walk(directory):
                    for file in files:
                        try:
                            total_file_count += 1
                            dir_file_count += 1
                            
                            if total_file_count % 1000 == 0:
                                self.root.after(0, lambda: self.log(f"Scanned {total_file_count} files..."))
                            
                            # Check if search term is in filename
                            if search_term_lower in file.lower():
                                file_path = os.path.join(root, file)
                                self.found_files.append(file_path)
                                dir_found_files.append(file_path)
                                
                        except Exception as e:
                            self.root.after(0, lambda e=e, f=file: self.log(f"Error processing file {f}: {e}"))
                
                # Log results for this directory
                if dir_found_files:
                    self.root.after(0, lambda d=directory, c=len(dir_found_files): 
                                   self.log(f"  Found {c} matching files"))
                    for file_path in dir_found_files:
                        self.root.after(0, lambda fp=file_path: self.log(f"    - {os.path.basename(fp)}"))
                else:
                    self.root.after(0, lambda d=directory: self.log(f"  No matching files found"))
            
            # Update UI
            self.root.after(0, self.search_complete, total_file_count)
            
        except Exception as e:
            self.root.after(0, lambda: self.log(f"Error during search: {e}"))
    
    def search_complete(self, total_file_count):
        search_term = self.search_term.get()
        if self.found_files:
            self.log(f"\nSearch complete. Scanned {total_file_count} files across all directories.")
            self.log(f"Found {len(self.found_files)} files with '{search_term}' in their names")
            self.add_btn.config(state=tk.NORMAL)
        else:
            self.log(f"\nNo files with '{search_term}' in their names were found in any directory.")
    
    def add_parameters(self):
        param_file = self.parameter_file.get()
        
        if not os.path.isfile(param_file):
            messagebox.showerror("Error", f"Parameter file '{param_file}' not found")
            return
        
        # Read parameter file
        try:
            with open(param_file, 'r', encoding='utf-8') as f:
                new_params = f.read().strip()
                
            if not new_params:
                messagebox.showwarning("Warning", "Parameter file is empty")
                return
                
            # Ask for confirmation
            if not messagebox.askyesno("Confirm", 
                f"Add parameters to {len(self.found_files)} files across {len(self.selected_directories)} directories?\n\n"
                "This action cannot be undone."):
                return
                
            # Start parameter addition in a separate thread
            Thread(target=self.add_parameters_thread, args=(new_params,)).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read parameter file: {e}")
    
    def add_parameters_thread(self, new_params):
        try:
            self.log("\nAdding parameters to files...")
            
            success_count = 0
            files_by_dir = {}
            
            # Group files by directory for better logging
            for file_path in self.found_files:
                dir_name = os.path.dirname(file_path)
                if dir_name not in files_by_dir:
                    files_by_dir[dir_name] = []
                files_by_dir[dir_name].append(file_path)
            
            for directory, files in files_by_dir.items():
                self.root.after(0, lambda d=directory: self.log(f"\nProcessing directory: {d}"))
                
                for i, file_path in enumerate(files):
                    try:
                        # Try UTF-8 first, then fallback to latin-1 which preserves all bytes
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            encoding_used = 'utf-8'
                        except UnicodeDecodeError:
                            with open(file_path, 'r', encoding='latin-1') as f:
                                content = f.read()
                            encoding_used = 'latin-1'
                        # Add parameters at the end of the file
                        with open(file_path, 'w', encoding=encoding_used) as f:
                            f.write(content)
                            f.write("\n" + "\n" + new_params)
                        
                        success_count += 1
                        file_name = os.path.basename(file_path)
                        self.root.after(0, lambda fn=file_name: self.log(f"  - Added parameters to: {fn}"))
                        
                    except Exception as e:
                        self.root.after(0, lambda fp=file_path, e=e: self.log(f"  - Error updating {os.path.basename(fp)}: {e}"))
            
            # Update UI
            self.root.after(0, lambda: self.log(f"\nOperation completed: Added parameters to {success_count} out of {len(self.found_files)} files"))
            
            if success_count > 0:
                self.root.after(0, lambda: messagebox.showinfo("Success", 
                    f"Successfully added parameters to {success_count} files "
                    f"across {len(self.selected_directories)} directories!"))
            
        except Exception as e:
            self.root.after(0, lambda: self.log(f"Error during operation: {e}"))

def main():
    root = tk.Tk()
    app = ParameterAdditionTool(root)
    root.mainloop()

if __name__ == "__main__":
    main()