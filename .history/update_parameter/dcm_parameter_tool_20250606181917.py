import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime

def read_config_file(config_path):
    """Read the config file and extract parameters and their values."""
    parameters = {}
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
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
    
    return parameters

def read_file(file_path):
    """Utility function to read file contents safely."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""

def find_files_with_parameters(directory, parameters, file_extension=".dcm"):
    """Find files in the directory containing any of the specified parameters."""
    matching_files = []
    parameter_occurrences = {}
    
    # Get all files with the specified extension
    all_files = [f for f in os.listdir(directory) if f.endswith(file_extension)]
    print(f"Found {len(all_files)} {file_extension} files in directory: {directory}")
    
    for filename in all_files:
        file_path = os.path.join(directory, filename)
        print(f"Checking file: {filename}")
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                lines = file.readlines()
        except Exception as e:
            print(f"Error reading file {filename}: {e}")
            continue
            
        # Check for exact parameter matches in the context of the file structure
        found_params = []
        current_param = None
        keywords = ("KENNLINIE", "KENNFELD", "FESTWERT", "GRUPPENKENNLINIE")
        
        for line_num, line in enumerate(lines, 1):
            stripped_line = line.strip()
            
            # Look for parameter definitions
            if stripped_line.startswith(keywords):
                parts = stripped_line.split()
                if len(parts) > 1:
                    current_param = parts[1]
                    if current_param in parameters:
                        found_params.append(current_param)
                        print(f"  Found parameter {current_param} at line {line_num}")
        
        if found_params:
            matching_files.append(file_path)  # Store full path
            parameter_occurrences[file_path] = list(set(found_params))  # Remove duplicates

    # Print summary
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
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    lines = file.readlines()
            except Exception as e:
                print(f"Error reading file {filename}: {e}")
                continue

            updated_lines = []
            current_param = None
            keywords = ("KENNLINIE", "KENNFELD", "FESTWERT", "GRUPPENKENNLINIE")
            file_was_modified = False
            
            for i, line in enumerate(lines):
                stripped_line = line.strip()
                
                # Check for parameter definition
                if stripped_line.startswith(keywords):
                    parts = stripped_line.split()
                    if len(parts) > 1:
                        current_param = parts[1]
                        print(f"Found parameter definition: {current_param} in {filename} at line {i+1}")
                
                # Check for WERT line and update if parameter matches
                elif stripped_line.startswith('WERT') and current_param and current_param in config_parameters:
                    new_value = config_parameters[current_param]
                    # Preserve original indentation
                    indentation = line[:len(line) - len(line.lstrip())]
                    line = f"{indentation}WERT {new_value}\n"
                    print(f"Updated {current_param} to {new_value} in {filename} at line {i+1}")
                    file_was_modified = True
                    current_param = None  # Reset after updating
                
                updated_lines.append(line)
            
            # Only write if file was actually modified
            if file_was_modified:
                try:
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.writelines(updated_lines)
                    updated_files.append(file_path)  # Store full path
                    print(f"Successfully updated file: {filename}")
                except Exception as e:
                    print(f"Error writing to file {filename}: {e}")
    
    return updated_files

def process_multiple_directories(directories, config_parameters, file_extension=".dcm"):
    """Process multiple directories for finding and updating files."""
    all_matching_files = []
    all_updated_files = []
    
    for directory in directories:
        print(f"\nProcessing directory: {directory}")
        
        # Find files in this directory
        matching_files = find_files_with_parameters(directory, config_parameters, file_extension)
        all_matching_files.extend(matching_files)
        
        # Update files in this directory
        updated_files = update_files_in_directory(directory, config_parameters, file_extension)
        all_updated_files.extend(updated_files)
    
    return all_matching_files, all_updated_files

class MultiDirectoryDialog:
    def __init__(self, parent):
        self.parent = parent
        self.selected_directories = []
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Select Multiple Directories")
        self.dialog.geometry("700x500")
        self.dialog.grab_set()  # Make dialog modal
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
        
        tk.Label(path_frame, text="Current Path:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        self.current_path_var = tk.StringVar(value="No directory selected")
        tk.Label(path_frame, textvariable=self.current_path_var, font=('Arial', 9), 
                fg="green", wraplength=500).pack(side=tk.LEFT, padx=(10, 0))
        
        # Browse button
        tk.Button(main_frame, text="Browse Parent Folder", command=self.browse_parent_folder, 
                 width=20, bg='lightgreen').pack(pady=(0, 10))
        
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

class ParameterUpdateTool:
    def __init__(self, root):
        self.root = root
        self.root.title("DCM File Parameter Update Tool - Multi Directory")
        self.root.geometry("800x500")
        self.selected_directories = []
        self.setup_gui()

    def setup_gui(self):
        # Main frame
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # File selection
        tk.Label(main_frame, text="Select Parameter Config File:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        file_frame = tk.Frame(main_frame)
        file_frame.grid(row=1, column=0, columnspan=3, sticky='ew', pady=(0, 15))
        file_frame.columnconfigure(0, weight=1)
        
        self.list_file_entry = tk.Entry(file_frame, width=70)
        self.list_file_entry.grid(row=0, column=0, sticky='ew', padx=(0, 10))
        tk.Button(file_frame, text="Browse", command=self.open_file).grid(row=0, column=1)

        # Multiple directories selection
        tk.Label(main_frame, text="Select Multiple Directories containing DCM files:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=(0, 5))
        
        dir_frame = tk.Frame(main_frame)
        dir_frame.grid(row=3, column=0, columnspan=3, sticky='ew', pady=(0, 15))
        dir_frame.columnconfigure(0, weight=1)
        
        # Listbox to show selected directories
        listbox_frame = tk.Frame(dir_frame)
        listbox_frame.grid(row=0, column=0, sticky='ew', padx=(0, 10))
        listbox_frame.columnconfigure(0, weight=1)
        
        self.directory_listbox = tk.Listbox(listbox_frame, height=4)
        self.directory_listbox.grid(row=0, column=0, sticky='ew')
        
        # Scrollbar for listbox
        listbox_scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.directory_listbox.yview)
        listbox_scrollbar.grid(row=0, column=1, sticky='ns')
        self.directory_listbox.configure(yscrollcommand=listbox_scrollbar.set)
        
        # Buttons for directory management
        dir_buttons_frame = tk.Frame(dir_frame)
        dir_buttons_frame.grid(row=0, column=1, sticky='n')
        
        tk.Button(dir_buttons_frame, text="Select Folders", command=self.select_multiple_directories, 
                 width=15, bg='lightblue', font=('Arial', 9, 'bold')).pack(pady=(0, 5))
        tk.Button(dir_buttons_frame, text="Add Single Folder", command=self.add_single_directory, width=15).pack(pady=(0, 5))
        tk.Button(dir_buttons_frame, text="Remove Selected", command=self.remove_directory, width=15).pack(pady=(0, 5))
        tk.Button(dir_buttons_frame, text="Clear All", command=self.clear_directories, width=15).pack()

        # File extension selection
        ext_frame = tk.Frame(main_frame)
        ext_frame.grid(row=4, column=0, columnspan=3, sticky='ew', pady=(0, 15))
        
        tk.Label(ext_frame, text="File Extension:").grid(row=0, column=0, sticky='w')
        self.extension_var = tk.StringVar(value=".dcm")
        ext_combo = ttk.Combobox(ext_frame, textvariable=self.extension_var, values=[".dcm", ".cfg", ".txt"], width=10)
        ext_combo.grid(row=0, column=1, padx=(10, 0), sticky='w')

        # Directory count label
        self.dir_count_label = tk.Label(ext_frame, text="Selected directories: 0", fg="blue")
        self.dir_count_label.grid(row=0, column=2, padx=(20, 0), sticky='w')

        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=(10, 0))
        
        tk.Button(button_frame, text="Preview Changes", command=self.preview_changes, 
                 bg='lightblue', width=15).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(button_frame, text="Update Files", command=self.start_update, 
                 bg='lightgreen', width=15).pack(side=tk.LEFT)

        # Results text area
        tk.Label(main_frame, text="Results:", font=('Arial', 10, 'bold')).grid(row=6, column=0, sticky='w', pady=(20, 5))
        
        text_frame = tk.Frame(main_frame)
        text_frame.grid(row=7, column=0, columnspan=3, sticky='nsew', pady=(0, 10))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.results_text = tk.Text(text_frame, height=12, wrap=tk.WORD)
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)

    def log_message(self, message):
        """Add message to results text area."""
        self.results_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.results_text.see(tk.END)
        self.root.update()

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Parameter Config File",
            filetypes=[("Text files", "*.txt"), ("Config files", "*.cfg"), ("All files", "*.*")]
        )
        if file_path:
            self.list_file_entry.delete(0, tk.END)
            self.list_file_entry.insert(0, file_path)

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

    def add_single_directory(self):
        """Add a single directory to the list."""
        directory_path = filedialog.askdirectory(title="Select Directory containing DCM files")
        if directory_path and directory_path not in self.selected_directories:
            self.selected_directories.append(directory_path)
            self.directory_listbox.insert(tk.END, directory_path)
            self.update_directory_count()

    def remove_directory(self):
        """Remove selected directory from the list."""
        selection = self.directory_listbox.curselection()
        if selection:
            index = selection[0]
            self.directory_listbox.delete(index)
            del self.selected_directories[index]
            self.update_directory_count()

    def clear_directories(self):
        """Clear all selected directories."""
        self.directory_listbox.delete(0, tk.END)
        self.selected_directories.clear()
        self.update_directory_count()

    def update_directory_count(self):
        """Update the directory count label."""
        count = len(self.selected_directories)
        self.dir_count_label.config(text=f"Selected directories: {count}")

    def validate_inputs(self):
        """Validate user inputs."""
        config_path = self.list_file_entry.get().strip()
        
        if not config_path:
            messagebox.showerror("Error", "Please select a config file.")
            return False
        
        if not self.selected_directories:
            messagebox.showerror("Error", "Please select at least one directory.")
            return False
        
        if not os.path.isfile(config_path):
            messagebox.showerror("Error", "Please select a valid config file.")
            return False
        
        # Validate all directories exist
        invalid_dirs = [d for d in self.selected_directories if not os.path.isdir(d)]
        if invalid_dirs:
            messagebox.showerror("Error", f"Invalid directories found:\n{chr(10).join(invalid_dirs)}")
            return False
        
        return True

    def preview_changes(self):
        """Preview which files would be affected without making changes."""
        if not self.validate_inputs():
            return
        
        self.results_text.delete(1.0, tk.END)
        self.log_message("Starting preview...")
        
        try:
            config_path = self.list_file_entry.get().strip()
            file_extension = self.extension_var.get()
            
            config_parameters = read_config_file(config_path)
            self.log_message(f"Loaded {len(config_parameters)} parameters from config file")
            
            # Display parameters to be updated
            for param, value in config_parameters.items():
                self.log_message(f"  {param} -> {value}")
            
            self.log_message(f"\nSearching in {len(self.selected_directories)} directories...")
            
            total_matching_files = []
            for directory in self.selected_directories:
                self.log_message(f"\nChecking directory: {directory}")
                matching_files = find_files_with_parameters(
                    directory, config_parameters, file_extension
                )
                if matching_files:
                    self.log_message(f"  Found {len(matching_files)} matching files:")
                    for file_path in matching_files:
                        self.log_message(f"    - {os.path.basename(file_path)}")
                    total_matching_files.extend(matching_files)
                else:
                    self.log_message(f"  No matching files found")
            
            if not total_matching_files:
                self.log_message("\nNo files found with the specified parameters in any directory.")
            else:
                self.log_message(f"\nTotal: {len(total_matching_files)} files would be updated across all directories.")
                    
        except Exception as e:
            self.log_message(f"Error during preview: {str(e)}")
            messagebox.showerror("Error", f"Error during preview: {str(e)}")

    def start_update(self):
        if not self.validate_inputs():
            return
        
        # Confirm before updating
        result = messagebox.askyesno("Confirm Update", 
                                   f"Are you sure you want to update files in {len(self.selected_directories)} directories?\n"
                                   "This operation will modify the original files.")
        if not result:
            return
        
        self.results_text.delete(1.0, tk.END)
        self.log_message("Starting file update...")
        
        try:
            config_path = self.list_file_entry.get().strip()
            file_extension = self.extension_var.get()
            
            config_parameters = read_config_file(config_path)
            self.log_message(f"Loaded {len(config_parameters)} parameters from config file")
            
            # Display parameters to be updated
            for param, value in config_parameters.items():
                self.log_message(f"  {param} -> {value}")
            
            self.log_message(f"\nProcessing {len(self.selected_directories)} directories...")
            
            # Process all directories
            all_matching_files, all_updated_files = process_multiple_directories(
                self.selected_directories, config_parameters, file_extension
            )
            
            if not all_matching_files:
                self.log_message("No files found with the specified parameters in any directory.")
                messagebox.showinfo("Info", "No files found with the specified parameters.")
                return
            
            self.log_message(f"\nFound {len(all_matching_files)} files to update")
            
            if all_updated_files:
                self.log_message(f"Successfully updated {len(all_updated_files)} files:")
                
                # Group by directory for better display
                files_by_dir = {}
                for file_path in all_updated_files:
                    dir_name = os.path.dirname(file_path)
                    file_name = os.path.basename(file_path)
                    if dir_name not in files_by_dir:
                        files_by_dir[dir_name] = []
                    files_by_dir[dir_name].append(file_name)
                
                for directory, files in files_by_dir.items():
                    self.log_message(f"\nDirectory: {directory}")
                    for file in files:
                        self.log_message(f"  - {file}")
                
                messagebox.showinfo("Success", 
                                  f"Successfully updated {len(all_updated_files)} files "
                                  f"across {len(self.selected_directories)} directories!")
            else:
                self.log_message("No files required updates.")
                messagebox.showinfo("Info", "No files required updates.")
                
        except Exception as e:
            self.log_message(f"Error during update: {str(e)}")
            messagebox.showerror("Error", f"An error occurred during update: {str(e)}")

# Setup the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = ParameterUpdateTool(root)
    root.mainloop()