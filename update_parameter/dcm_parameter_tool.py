import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_multiple_directories_parallel(directories, config_parameters, file_extension=".dcm", max_workers=8):
    """Song song: tìm + cập nhật các file trong nhiều thư mục."""
    def work(d):
        matching = find_files_with_parameters(d, config_parameters, file_extension)
        updated = update_files_in_directory(d, config_parameters, file_extension)
        return d, matching, updated

    all_matching = []
    all_updated = []
    per_dir = []
    if not directories:
        return all_matching, all_updated, per_dir
    workers = min(max_workers, len(directories))
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(work, d): d for d in directories}
        for fut in as_completed(futures):
            d = futures[fut]
            try:
                dir_path, matching, updated = fut.result()
                per_dir.append((dir_path, matching, updated))
                all_matching.extend(matching)
                all_updated.extend(updated)
            except Exception as e:
                print(f"Error processing directory {d}: {e}")
                per_dir.append((d, [], []))
    return all_matching, all_updated, per_dir

def read_config_file(config_path):
    """Read the config file and extract parameters and their values."""
    parameters = {}
    try:
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
        except UnicodeDecodeError:
            with open(config_path, 'r', encoding='latin-1') as file:
                lines = file.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {config_path}")
    except Exception as e:
        raise Exception(f"Error reading config file: {e}")
    
    current_param = None
    keywords = ("KENNLINIE", "KENNFELD", "FESTWERT", "GRUPPENKENNLINIE")
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if line.startswith(keywords):
            parts = line.split()
            if len(parts) > 1:
                current_param = parts[1]
                print(f"Line {line_num}: Found parameter definition: {current_param}")
            else:
                print(f"Line {line_num}: Invalid parameter format: {line}")
        elif line.startswith('WERT') and current_param:
            parts = line.split()
            if len(parts) > 1:
                parameters[current_param] = parts[1]
                print(f"Line {line_num}: Found parameter: {current_param} with new value: {parameters[current_param]}")
            else:
                print(f"Line {line_num}: Invalid WERT format: {line}")
            current_param = None
        elif line.startswith('TEXT') and current_param:
            parts = line.split()
            if len(parts) > 1:
                parameters[current_param] = parts[1]
                print(f"Line {line_num}: Found parameter: {current_param} with new value: {parameters[current_param]}")
            else:
                print(f"Line {line_num}: Invalid TEXT format: {line}")
            current_param = None
    
    return parameters

def read_file(file_path):
    """Utility function to read file contents safely."""
    try:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""

def find_files_with_parameters(directory, parameters, file_extension=".dcm"):
    """Find files in the directory containing any of the specified parameters."""
    matching_files = []
    parameter_occurrences = {}
    
    all_files = [f for f in os.listdir(directory) if f.endswith(file_extension)]
    print(f"Found {len(all_files)} {file_extension} files in directory: {directory}")
    
    for filename in all_files:
        file_path = os.path.join(directory, filename)
        print(f"Checking file: {filename}")
        
        try:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
            except UnicodeDecodeError:
                with open(file_path, 'r', encoding='latin-1') as file:
                    lines = file.readlines()
        except Exception as e:
            print(f"Error reading file {filename}: {e}")
            continue
            
        found_params = []
        current_param = None
        keywords = ("KENNLINIE", "KENNFELD", "FESTWERT", "GRUPPENKENNLINIE")
        
        for line_num, line in enumerate(lines, 1):
            stripped_line = line.strip()
            if stripped_line.startswith(keywords):
                parts = stripped_line.split()
                if len(parts) > 1:
                    current_param = parts[1]
                    if current_param in parameters:
                        found_params.append(current_param)
                        print(f"  Found parameter {current_param} at line {line_num}")
        
        if found_params:
            matching_files.append(file_path)
            parameter_occurrences[file_path] = list(set(found_params))

    for file, params in parameter_occurrences.items():
        print(f"Parameters found in {os.path.basename(file)}: {', '.join(params)}")

    if not matching_files:
        print(f"No matching parameters found in any files in {directory}.")

    return matching_files

def update_files_in_directory(directory, config_parameters, file_extension=".dcm"):
    """Update parameters in files within the specified directory."""
    updated_files = []
    
    for filename in os.listdir(directory):
        if filename.endswith(file_extension):
            file_path = os.path.join(directory, filename)
            
            try:
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        lines = file.readlines()
                    encoding_used = 'utf-8'
                except UnicodeDecodeError:
                    with open(file_path, 'r', encoding='latin-1') as file:
                        lines = file.readlines()
                    encoding_used = 'latin-1'
            except Exception as e:
                print(f"Error reading file {filename}: {e}")
                continue

            updated_lines = []
            current_param = None
            keywords = ("KENNLINIE", "KENNFELD", "FESTWERT", "GRUPPENKENNLINIE")
            file_was_modified = False
            
            for i, line in enumerate(lines):
                stripped_line = line.strip()
                
                if stripped_line.startswith(keywords):
                    parts = stripped_line.split()
                    if len(parts) > 1:
                        current_param = parts[1]
                        print(f"Found parameter definition: {current_param} in {filename} at line {i+1}")
                
                elif stripped_line.startswith('WERT') and current_param and current_param in config_parameters:
                    new_value = config_parameters[current_param]
                    indentation = line[:len(line) - len(line.lstrip())]
                    line = f"{indentation}WERT {new_value}\n"
                    print(f"Updated {current_param} to {new_value} in {filename} at line {i+1}")
                    file_was_modified = True
                    current_param = None
                
                elif stripped_line.startswith('TEXT') and current_param and current_param in config_parameters:
                    new_value = config_parameters[current_param]
                    indentation = line[:len(line) - len(line.lstrip())]
                    line = f"{indentation}TEXT {new_value}\n"
                    print(f"Updated {current_param} to {new_value} in {filename} at line {i+1}")
                    file_was_modified = True
                    current_param = None
                
                updated_lines.append(line)
            
            if file_was_modified:
                try:
                    with open(file_path, 'w', encoding= encoding_used) as file:
                        file.writelines(updated_lines)
                    updated_files.append(file_path)
                    print(f"Successfully updated file: {filename}")
                except Exception as e:
                    print(f"Error writing to file {filename}: {e}")
    
    return updated_files

def process_multiple_directories(directories, config_parameters, file_extension=".dcm"):
    """Process multiple directories (tuần tự)."""
    all_matching_files = []
    all_updated_files = []
    
    for directory in directories:
        print(f"\nProcessing directory: {directory}")
        matching_files = find_files_with_parameters(directory, config_parameters, file_extension)
        all_matching_files.extend(matching_files)
        updated_files = update_files_in_directory(directory, config_parameters, file_extension)
        all_updated_files.extend(updated_files)
    
    return all_matching_files, all_updated_files

class MultiDirectoryDialog:
    def __init__(self, parent):
        self.parent = parent
        self.selected_directories = []
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Select Multiple Directories")
        self.dialog.geometry("700x800")
        self.dialog.grab_set()
        
        # Load parent folder history
        self.config_file = os.path.join(os.path.dirname(__file__), 'dcm_parameter_config.json')
        self.parent_folder_history = []
        self.load_parent_history()
        
        self.setup_dialog()
        
    def setup_dialog(self):
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        instruction_text = (
            "Select multiple directories:\n"
            "• Use 'Browse Parent Folder' to navigate to a parent directory\n"
            "• Use Ctrl+A to select all folders\n"
            "• Use Ctrl+Click or Shift+Click for multiple selection"
        )
        tk.Label(main_frame, text=instruction_text, font=('Arial', 10),
                 justify=tk.LEFT, fg="blue").pack(anchor='w', pady=(0, 15))
        
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
        
        tk.Label(main_frame, text="Available Folders in Parent Directory:",
                 font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 5))
        
        available_frame = tk.Frame(main_frame)
        available_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.available_listbox = tk.Listbox(available_frame, selectmode=tk.EXTENDED, height=8)
        available_scrollbar = tk.Scrollbar(available_frame, orient=tk.VERTICAL,
                                           command=self.available_listbox.yview)
        self.available_listbox.configure(yscrollcommand=available_scrollbar.set)
        self.available_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        available_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.available_listbox.bind('<Control-a>', self.select_all_available)
        self.available_listbox.bind('<Return>', self.add_selected_directories)
        self.available_listbox.bind('<Double-Button-1>', self.add_selected_directories)
        
        transfer_frame = tk.Frame(main_frame)
        transfer_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Button(transfer_frame, text="Add Selected Folders →", command=self.add_selected_directories,
                  width=20, bg='lightblue').pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(transfer_frame, text="Add All Folders →", command=self.add_all_directories,
                  width=15).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Label(main_frame, text="Selected Directories:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 5))
        
        selected_frame = tk.Frame(main_frame)
        selected_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.selected_listbox = tk.Listbox(selected_frame, selectmode=tk.EXTENDED, height=6)
        selected_scrollbar = tk.Scrollbar(selected_frame, orient=tk.VERTICAL,
                                          command=self.selected_listbox.yview)
        self.selected_listbox.configure(yscrollcommand=selected_scrollbar.set)
        self.selected_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        selected_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.selected_listbox.bind('<Control-a>', self.select_all_selected)
        self.selected_listbox.bind('<Delete>', self.remove_selected_directories)
        
        mgmt_frame = tk.Frame(main_frame)
        mgmt_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Button(mgmt_frame, text="Remove Selected", command=self.remove_selected_directories,
                  width=15).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(mgmt_frame, text="Clear All", command=self.clear_all, width=10).pack(side=tk.LEFT)
        
        self.count_label = tk.Label(mgmt_frame, text="Selected: 0 directories", fg="blue",
                                    font=('Arial', 10, 'bold'))
        self.count_label.pack(side=tk.RIGHT)
        
        dialog_button_frame = tk.Frame(main_frame)
        dialog_button_frame.pack(fill=tk.X, pady=(10, 0))
        tk.Button(dialog_button_frame, text="OK", command=self.ok_clicked,
                  width=10, bg='lightgreen', font=('Arial', 10, 'bold')).pack(side=tk.RIGHT, padx=(5, 0))
        tk.Button(dialog_button_frame, text="Cancel", command=self.cancel_clicked,
                  width=10, font=('Arial', 10)).pack(side=tk.RIGHT)
        
        self.center_dialog()
        
    def center_dialog(self):
        self.dialog.transient(self.parent)
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def load_parent_history(self):
        """Load parent folder history from config file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.parent_folder_history = config.get('parent_folder_history', [])
        except Exception as e:
            print(f"Error loading parent folder history: {e}")
            self.parent_folder_history = []
    
    def save_parent_history(self):
        """Save parent folder history to config file"""
        try:
            config = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            config['parent_folder_history'] = self.parent_folder_history
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving parent folder history: {e}")
    
    def on_path_selected(self, event=None):
        """Handle selection from dropdown"""
        selected_path = self.current_path_var.get()
        if selected_path and os.path.exists(selected_path):
            self.load_subdirectories(selected_path)
        
    def browse_parent_folder(self):
        parent_dir = filedialog.askdirectory(title="Select Parent Directory")
        if parent_dir:
            self.current_path_var.set(parent_dir)
            self.load_subdirectories(parent_dir)
            
            # Save to history
            if parent_dir not in self.parent_folder_history:
                self.parent_folder_history.insert(0, parent_dir)
                self.parent_folder_history = self.parent_folder_history[:10]  # Keep last 10
                self.path_combo['values'] = self.parent_folder_history
                self.save_parent_history()
            
    def load_subdirectories(self, parent_dir):
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
        self.available_listbox.select_set(0, tk.END)
        return 'break'
    
    def select_all_selected(self, event=None):
        self.selected_listbox.select_set(0, tk.END)
        return 'break'
        
    def add_selected_directories(self, event=None):
        selections = self.available_listbox.curselection()
        for index in selections:
            directory = self.available_listbox.get(index)
            if directory not in self.selected_directories:
                self.selected_directories.append(directory)
                self.selected_listbox.insert(tk.END, directory)
        self.update_count()
        
    def add_all_directories(self):
        for i in range(self.available_listbox.size()):
            directory = self.available_listbox.get(i)
            if directory not in self.selected_directories:
                self.selected_directories.append(directory)
                self.selected_listbox.insert(tk.END, directory)
        self.update_count()
        
    def remove_selected_directories(self, event=None):
        selections = self.selected_listbox.curselection()
        for index in reversed(selections):
            directory = self.selected_listbox.get(index)
            self.selected_listbox.delete(index)
            self.selected_directories.remove(directory)
        self.update_count()
        
    def clear_all(self):
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

class ParameterUpdateTool:
    def __init__(self, root):
        self.root = root
        self.root.title("DCM File Parameter Update Tool - Multi Directory")
        self.root.geometry("800x500")
        
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
        self.config_file = os.path.join(os.path.dirname(__file__), 'dcm_parameter_config.json')
        
        self.selected_directories = []
        self.config_file_history = []
        self._busy = False
        self._lock = threading.Lock()
        
        self.setup_gui()
        self.load_config()
        
        # Save config on window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _set_busy(self, value: bool):
        with self._lock:
            self._busy = value
        self.root.configure(cursor="watch" if value else "")
        self.root.update_idletasks()

    def setup_gui(self):
        main_frame = tk.Frame(self.root, bg=self.colors['bg'], padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure([1, 3, 6], weight=0)
        main_frame.rowconfigure(8, weight=3)

        tk.Label(main_frame, text="Select Parameter Config File:", font=('Segoe UI', 10, 'bold'),
                bg=self.colors['bg'], fg=self.colors['text']).grid(row=0, column=0, sticky='w', pady=(0, 5))
        file_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        file_frame.grid(row=1, column=0, columnspan=3, sticky='ew', pady=(0, 15))
        file_frame.columnconfigure(0, weight=1)
        self.list_file_combo = ttk.Combobox(file_frame, font=('Segoe UI', 9))
        self.list_file_combo.grid(row=0, column=0, sticky='ew', padx=(0, 10))
        tk.Button(file_frame, text="Browse", command=self.open_file,
                 bg=self.colors['primary'], fg='white', font=('Segoe UI', 9, 'bold'),
                 relief=tk.FLAT, padx=15, pady=6, cursor='hand2').grid(row=0, column=1)

        tk.Label(main_frame, text="Select Multiple Directories containing DCM files:", font=('Segoe UI', 10, 'bold'),
                bg=self.colors['bg'], fg=self.colors['text']).grid(row=2, column=0, sticky='w', pady=(0, 5))
        dir_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        dir_frame.grid(row=3, column=0, columnspan=3, sticky='ew', pady=(0, 15))
        dir_frame.columnconfigure(0, weight=1)

        listbox_frame = tk.Frame(dir_frame, bg=self.colors['panel'], relief=tk.SOLID, borderwidth=1)
        listbox_frame.grid(row=0, column=0, sticky='ew', padx=(0, 10))
        listbox_frame.columnconfigure(0, weight=1)
        self.directory_listbox = tk.Listbox(listbox_frame, height=4, font=('Segoe UI', 9),
                                           relief=tk.FLAT, bg=self.colors['panel'])
        self.directory_listbox.grid(row=0, column=0, sticky='ew')
        listbox_scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.directory_listbox.yview)
        listbox_scrollbar.grid(row=0, column=1, sticky='ns')
        self.directory_listbox.configure(yscrollcommand=listbox_scrollbar.set)

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

        ext_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        ext_frame.grid(row=4, column=0, columnspan=3, sticky='ew', pady=(0, 15))
        tk.Label(ext_frame, text="File Extension:", bg=self.colors['bg'],
                fg=self.colors['text'], font=('Segoe UI', 9)).grid(row=0, column=0, sticky='w')
        self.extension_var = tk.StringVar(value=".dcm")
        ext_combo = ttk.Combobox(ext_frame, textvariable=self.extension_var,
                                values=[".dcm", ".cfg", ".txt"], width=10, font=('Segoe UI', 9))
        ext_combo.grid(row=0, column=1, padx=(10, 0), sticky='w')
        self.dir_count_label = tk.Label(ext_frame, text="Selected directories: 0",
                                       bg=self.colors['bg'], fg=self.colors['primary'],
                                       font=('Segoe UI', 9, 'bold'))
        self.dir_count_label.grid(row=0, column=2, padx=(20, 0), sticky='w')

        button_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        button_frame.grid(row=5, column=0, columnspan=3, pady=(10, 0))
        tk.Button(button_frame, text="1. Preview Changes", command=self.preview_changes,
                  bg=self.colors['primary'], fg='white', width=16, font=('Segoe UI', 9, 'bold'),
                  relief=tk.FLAT, cursor='hand2', pady=6).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(button_frame, text="2. Update Files", command=self.start_update,
                  bg=self.colors['success'], fg='white', width=16, font=('Segoe UI', 9, 'bold'),
                  relief=tk.FLAT, cursor='hand2', pady=6).pack(side=tk.LEFT)

        tk.Label(main_frame, text="Results:", font=('Segoe UI', 10, 'bold'),
                bg=self.colors['bg'], fg=self.colors['text']).grid(row=6, column=0, sticky='w', pady=(20, 5))
        text_frame = tk.Frame(main_frame, bg=self.colors['panel'], relief=tk.SOLID, borderwidth=1)
        text_frame.grid(row=7, column=0, columnspan=3, sticky='nsew', pady=(0, 10))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        self.results_text = tk.Text(text_frame, height=12, wrap=tk.WORD, font=('Segoe UI', 9),
                                   relief=tk.FLAT, bg=self.colors['panel'])
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        self.results_text.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)

    def load_config(self):
        """Load saved configuration from JSON file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                # Load config file history
                if 'config_file_history' in config:
                    self.config_file_history = config['config_file_history']
                    self.list_file_combo['values'] = self.config_file_history
                    if self.config_file_history:
                        self.list_file_combo.set(self.config_file_history[0])
                
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
                    
                self.log_message(f"Loaded configuration: {len(self.selected_directories)} directories")
        except Exception as e:
            self.log_message(f"Could not load config: {e}")
    
    def save_config(self):
        """Save current configuration to JSON file."""
        try:
            # Update history list
            config_file_path = self.list_file_combo.get()
            if config_file_path and config_file_path not in self.config_file_history:
                self.config_file_history.insert(0, config_file_path)
                self.config_file_history = self.config_file_history[:10]  # Keep last 10
            
            config = {
                'config_file_history': self.config_file_history,
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

    def log_message(self, message):
        self.results_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.results_text.see(tk.END)

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Parameter Config File",
            filetypes=[("Text files", "*.txt"), ("Config files", "*.cfg"), ("All files", "*.*")]
        )
        if file_path:
            self.list_file_combo.set(file_path)
            # Add to history
            if file_path not in self.config_file_history:
                self.config_file_history.insert(0, file_path)
                self.config_file_history = self.config_file_history[:10]
                self.list_file_combo['values'] = self.config_file_history
            self.save_config()

    def select_multiple_directories(self):
        dialog = MultiDirectoryDialog(self.root)
        self.root.wait_window(dialog.dialog)
        for directory in dialog.selected_directories:
            if directory not in self.selected_directories:
                self.selected_directories.append(directory)
                self.directory_listbox.insert(tk.END, directory)
        self.update_directory_count()
        self.save_config()

    def add_single_directory(self):
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
        selection = self.directory_listbox.curselection()
        if selection:
            index = selection[0]
            self.directory_listbox.delete(index)
            del self.selected_directories[index]
            self.update_directory_count()
            self.save_config()

    def clear_directories(self):
        self.directory_listbox.delete(0, tk.END)
        self.selected_directories.clear()
        self.update_directory_count()
        self.save_config()

    def update_directory_count(self):
        count = len(self.selected_directories)
        self.dir_count_label.config(text=f"Selected directories: {count}")

    def validate_inputs(self):
        config_path = self.list_file_combo.get().strip()
        if not config_path:
            messagebox.showerror("Error", "Please select a config file.")
            return False
        if not self.selected_directories:
            messagebox.showerror("Error", "Please select at least one directory.")
            return False
        if not os.path.isfile(config_path):
            messagebox.showerror("Error", "Please select a valid config file.")
            return False
        invalid_dirs = [d for d in self.selected_directories if not os.path.isdir(d)]
        if invalid_dirs:
            messagebox.showerror("Error", f"Invalid directories found:\n{chr(10).join(invalid_dirs)}")
            return False
        return True

    def preview_changes(self):
        if self._busy:
            messagebox.showinfo("Info", "Task đang chạy, vui lòng đợi.")
            return
        if not self.validate_inputs():
            return
        self.results_text.delete(1.0, tk.END)
        self.log_message("Starting preview (multi-thread)...")
        self._set_busy(True)

        def worker():
            logs = []
            try:
                config_path = self.list_file_combo.get().strip()
                ext = self.extension_var.get()
                config_parameters = read_config_file(config_path)
                logs.append(f"Loaded {len(config_parameters)} parameters.")
                for p, v in config_parameters.items():
                    logs.append(f"  {p} -> {v}")

                logs.append(f"\nScanning {len(self.selected_directories)} directories in parallel...")
                all_matching = []

                def find_only(d):
                    return d, find_files_with_parameters(d, config_parameters, ext)

                workers = min(8, len(self.selected_directories) or 1)
                with ThreadPoolExecutor(max_workers=workers) as ex:
                    futures = {ex.submit(find_only, d): d for d in self.selected_directories}
                    for fut in as_completed(futures):
                        d, found = fut.result()
                        logs.append(f"\nDirectory: {d}")
                        if found:
                            logs.append(f"  Found {len(found)} matching files:")
                            for fp in found:
                                logs.append(f"    - {os.path.basename(fp)}")
                            all_matching.extend(found)
                        else:
                            logs.append("  No matching files")

                if not all_matching:
                    logs.append("\nNo files found with the specified parameters.")
                else:
                    logs.append(f"\nTotal: {len(all_matching)} files would be updated.")
            except Exception as e:
                logs.append(f"Error during preview: {e}")
            finally:
                self.root.after(0, lambda: self._apply_preview_logs(logs))

        threading.Thread(target=worker, daemon=True).start()

    def _apply_preview_logs(self, logs):
        for line in logs:
            self.log_message(line)
        self._set_busy(False)

    def start_update(self):
        if self._busy:
            messagebox.showinfo("Info", "Task đang chạy, vui lòng đợi.")
            return
        if not self.validate_inputs():
            return
        result = messagebox.askyesno(
            "Confirm Update",
            f"Update files in {len(self.selected_directories)} directories (multi-thread)?"
        )
        if not result:
            return

        self.results_text.delete(1.0, tk.END)
        self.log_message("Starting file update (multi-thread)...")
        self._set_busy(True)

        def worker():
            logs = []
            try:
                ext = self.extension_var.get()
                config_path = self.list_file_combo.get().strip()
                config_parameters = read_config_file(config_path)
                if not config_parameters:
                    logs.append("No valid parameters found in config file.")
                    self.root.after(0, lambda: self._finish_update(logs, [], []))
                    return

                logs.append(f"Loaded {len(config_parameters)} parameters:")
                for p, v in config_parameters.items():
                    logs.append(f"  {p} -> {v}")

                logs.append(f"\nProcessing {len(self.selected_directories)} directories in parallel...")
                all_matching, all_updated, per_dir = process_multiple_directories_parallel(
                    self.selected_directories, config_parameters, ext, max_workers=8
                )

                if not all_matching:
                    logs.append("No files found with the specified parameters.")
                    self.root.after(0, lambda: self._finish_update(logs, all_matching, all_updated))
                    return

                logs.append(f"\nFound {len(all_matching)} files containing target parameters.")
                if all_updated:
                    logs.append(f"\nUpdated {len(all_updated)} files:")
                    grouped = {}
                    for fp in all_updated:
                        grouped.setdefault(os.path.dirname(fp), []).append(os.path.basename(fp))
                    for d, files in grouped.items():
                        logs.append(f"\nDirectory: {d}")
                        for f in files:
                            logs.append(f"  - {f}")
                else:
                    logs.append("No files required changes (values already correct).")

                self.root.after(0, lambda: self._finish_update(logs, all_matching, all_updated))
            except Exception as e:
                logs.append(f"Error during update: {e}")
                self.root.after(0, lambda: self._finish_update(logs, [], []))

        threading.Thread(target=worker, daemon=True).start()

    def _finish_update(self, logs, all_matching, all_updated):
        for line in logs:
            self.log_message(line)
        if all_updated:
            messagebox.showinfo("Success", f"Updated {len(all_updated)} files.")
        else:
            messagebox.showinfo("Info", "No files updated.")
        self._set_busy(False)

if __name__ == "__main__":
    root = tk.Tk()
    app = ParameterUpdateTool(root)
    root.mainloop()