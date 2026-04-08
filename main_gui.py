import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel,
    QMessageBox, QGraphicsOpacityEffect, QHBoxLayout, QFrame
)
from PyQt5.QtGui import QMovie, QPixmap, QFont, QColor, QPalette
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

class ModernButton(QPushButton):
    def __init__(self, text, color="#2196F3", *args, **kwargs):
        super().__init__(text, *args, **kwargs)
        self.default_color = color
        self.hover_color = self.adjust_brightness(color, 1.2)
        self.setFixedHeight(50)
        self.setCursor(Qt.PointingHandCursor)
        self.update_style()

    def adjust_brightness(self, hex_color, factor):
        """Adjust color brightness"""
        color = QColor(hex_color)
        h, s, v, a = color.getHsv()
        v = min(255, int(v * factor))
        color.setHsv(h, s, v, a)
        return color.name()

    def update_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.default_color};
                color: white;
                font-family: 'Segoe UI';
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
            }}
            QPushButton:hover {{
                background-color: {self.hover_color};
            }}
            QPushButton:pressed {{
                background-color: {self.adjust_brightness(self.default_color, 0.8)};
            }}
        """)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Parameter Tool Suite")
        self.resize(500, 550)
        
        # Modern color scheme
        self.colors = {
            'bg': '#f5f5f5',
            'panel': '#ffffff',
            'primary': '#2196F3',
            'success': '#4CAF50',
            'warning': '#FF9800',
            'text': '#333333',
            'border': '#e0e0e0'
        }
        
        self.setStyleSheet(f"background-color: {self.colors['bg']};")

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(20)
        self.setLayout(self.layout)

        # GIF display at top
        self.gif_label = QLabel(self)
        self.gif_label.setAlignment(Qt.AlignCenter)
        self.gif_label.setMaximumHeight(180)
        gif_path = resource_path("Drift.gif")
        self.movie = QMovie(gif_path)
        if self.movie.isValid():
            self.gif_label.setMovie(self.movie)
            self.movie.start()
        else:
            self.gif_label.setStyleSheet(f"""
                background-color: {self.colors['panel']};
                border-radius: 8px;
                color: {self.colors['text']};
                padding: 20px;
                font-size: 48px;
            """)
            self.gif_label.setText("🔧")
        self.layout.addWidget(self.gif_label)

        # Title section
        title_frame = QFrame()
        title_frame.setStyleSheet(f"""
            background-color: {self.colors['panel']};
            border-radius: 12px;
            padding: 15px;
        """)
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(20, 10, 20, 10)
        
        title_label = QLabel("Parameter Tool Suite")
        title_font = QFont("Segoe UI", 14, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"color: {self.colors['primary']};")
        title_layout.addWidget(title_label)
        
        subtitle_label = QLabel("DCM Parameter Management Tools")
        subtitle_font = QFont("Segoe UI", 9)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet(f"color: {self.colors['text']};")
        title_layout.addWidget(subtitle_label)
        
        self.layout.addWidget(title_frame)

        # Buttons section
        button_frame = QFrame()
        button_frame.setStyleSheet(f"""
            background-color: {self.colors['panel']};
            border-radius: 12px;
        """)
        button_layout = QVBoxLayout(button_frame)
        button_layout.setContentsMargins(20, 20, 20, 20)
        button_layout.setSpacing(12)

        self.buttons = []
        button_configs = [
            ("Split Parameter Tool", self.colors['primary'], "✂️"),
            ("Update Parameter Tool", self.colors['warning'], "🔄")
        ]
        
        for text, color, icon in button_configs:
            btn = ModernButton(f"{icon}  {text}", color)
            button_layout.addWidget(btn)
            self.buttons.append(btn)

        self.layout.addWidget(button_frame)

        # Status bar
        status_frame = QFrame()
        status_frame.setStyleSheet(f"""
            background-color: {self.colors['panel']};
            border-radius: 8px;
            padding: 10px;
        """)
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(15, 10, 15, 10)
        
        status_icon = QLabel("●")
        status_icon.setStyleSheet(f"color: {self.colors['success']}; font-size: 16px;")
        status_layout.addWidget(status_icon)
        
        self.status_label = QLabel("Ready to launch tools")
        self.status_label.setFont(QFont("Segoe UI", 9))
        self.status_label.setStyleSheet(f"color: {self.colors['text']};")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        self.layout.addWidget(status_frame)

        # Nuclearbomb GIF at bottom (hidden by default, shown on maximize)
        self.nuclearbomb_label = QLabel(self)
        self.nuclearbomb_label.setAlignment(Qt.AlignCenter)
        self.nuclearbomb_label.setMinimumHeight(250)
        self.nuclearbomb_label.setVisible(False)  # Hidden by default
        nuclearbomb_path = resource_path("Nuclearbomb.gif")
        self.bg_movie = QMovie(nuclearbomb_path)
        if self.bg_movie.isValid():
            self.nuclearbomb_label.setMovie(self.bg_movie)
            self.bg_movie.start()
        self.layout.addWidget(self.nuclearbomb_label)

        self.layout.addStretch()

        # Track window state
        self._is_maximized = False

        # Kết nối nút
        self.buttons[0].clicked.connect(self.open_split_parameter)
        self.buttons[1].clicked.connect(self.open_update_parameter)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Show Nuclearbomb GIF only when window is large enough (maximized or expanded)
        is_large = self.width() > 600 and self.height() > 700
        self.nuclearbomb_label.setVisible(is_large)
        self.update()

    def run_tool_exe(self, exe_relative_path, tool_name="Tool"):
        """Chạy tool exe - tự động tìm exe trong nhiều vị trí"""
        # Danh sách các vị trí có thể tìm exe
        search_paths = []
        
        # 1. Thư mục của main_gui.exe (khi copy cùng thư mục với các tool)
        if getattr(sys, 'frozen', False):
            # Khi chạy như exe, sys.executable là path của exe
            exe_dir = os.path.dirname(sys.executable)
            search_paths.append(os.path.join(exe_dir, exe_relative_path))
        
        # 2. Embedded resource trong _MEIPASS (PyInstaller)
        if hasattr(sys, '_MEIPASS'):
            search_paths.append(os.path.join(sys._MEIPASS, exe_relative_path))
        
        # 3. Thư mục hiện tại (khi chạy từ source code)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        search_paths.append(os.path.join(script_dir, exe_relative_path))
        
        # Tìm exe trong các vị trí
        exe_path = None
        for path in search_paths:
            if os.path.isfile(path):
                exe_path = path
                break
        
        if not exe_path:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("File Not Found")
            msg.setText(f"Cannot find {tool_name}")
            msg.setInformativeText(f"Path: {exe_path}")
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #ffffff;
                }
                QLabel {
                    color: #333333;
                    font-family: 'Segoe UI';
                }
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            msg.exec_()
            return
        
        try:
            subprocess.Popen([exe_path])
            self.status_label.setText(f"✓ Launched {tool_name}")
            QTimer.singleShot(3000, lambda: self.status_label.setText("Ready to launch tools"))
        except Exception as e:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Launch Error")
            msg.setText(f"Failed to launch {tool_name}")
            msg.setInformativeText(str(e))
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #ffffff;
                }
                QLabel {
                    color: #333333;
                    font-family: 'Segoe UI';
                }
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            msg.exec_()

    def open_split_parameter(self):
        self.run_tool_exe("split_parameter_pro.exe", "Split Parameter Tool")

    def open_update_parameter(self):
        self.run_tool_exe("dcm_parameter_tool.exe", "Update Parameter Tool")

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()