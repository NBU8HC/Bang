import tkinter as tk
from tkinter import messagebox
import sys
import os

# Import tool GUIs
sys.path.append(os.path.join(os.path.dirname(__file__), 'Add new parameter'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'Split parameter tool'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'update_parameter'))

# Import main classes/functions from each tool
try:
    from Add_new_parameter.add_new_parameter import ParameterAdditionTool
except ImportError:
    ParameterAdditionTool = None
try:
    from Split_parameter_tool.split_parameter import ParameterClonerApp
except ImportError:
    ParameterClonerApp = None
try:
    from update_parameter.dcm_parameter_tool import MultiDirectoryDialog
except ImportError:
    MultiDirectoryDialog = None

class HomeScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Tool Home")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Chọn công cụ để sử dụng", font=("Arial", 14, "bold"), pady=20).pack()
        btn1 = tk.Button(self.root, text="Add New Parameter", width=25, height=2, command=self.open_add_new_parameter, bg='lightblue')
        btn1.pack(pady=10)
        btn2 = tk.Button(self.root, text="Split Parameter Tool", width=25, height=2, command=self.open_split_parameter, bg='lightgreen')
        btn2.pack(pady=10)
        btn3 = tk.Button(self.root, text="Update Parameter Tool", width=25, height=2, command=self.open_update_parameter, bg='lightyellow')
        btn3.pack(pady=10)

    def open_add_new_parameter(self):
        if ParameterAdditionTool:
            win = tk.Toplevel(self.root)
            ParameterAdditionTool(win)
        else:
            messagebox.showerror("Error", "Không tìm thấy tool Add New Parameter")

    def open_split_parameter(self):
        if ParameterClonerApp:
            # Mở tool trong cửa sổ mới
            win = tk.Toplevel(self.root)
            win.withdraw()  # Ẩn cửa sổ tạm thời nếu tool tự tạo root
            ParameterClonerApp(win)
        else:
            messagebox.showerror("Error", "Không tìm thấy tool Split Parameter")

    def open_update_parameter(self):
        if MultiDirectoryDialog:
            win = tk.Toplevel(self.root)
            win.withdraw()
            MultiDirectoryDialog(win)
        else:
            messagebox.showerror("Error", "Không tìm thấy tool Update Parameter")

def main():
    root = tk.Tk()
    app = HomeScreen(root)
    root.mainloop()

if __name__ == "__main__":
    main()
