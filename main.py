import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QMessageBox
)
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt, QTimer


def resource_path(relative_path):
    """Lấy đường dẫn tuyệt đối, hỗ trợ cả chế độ PyInstaller onefile"""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class RedButton(QPushButton):
    def __init__(self, text, *args, **kwargs):
        super().__init__(text, *args, **kwargs)
        self.setFixedHeight(40)
        self.setStyleSheet("""
            QPushButton {
                color: white;
                font-weight: bold;
                font-size: 14px;
                border-radius: 6px;
                padding: 8px;
                background-color: #D32F2F;
            }
            QPushButton:hover {
                background-color: #B71C1C;
            }
        """)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Tool Home")
        self.resize(300, 700)
        self.setStyleSheet("background-color: yellow;")

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setSpacing(60)
        self.setLayout(self.layout)

        # Hiển thị GIF
        self.gif_label = QLabel(self)
        self.gif_label.setAlignment(Qt.AlignCenter)
        self.gif_label.setScaledContents(True)  # Cho phép co giãn
        self.layout.addWidget(self.gif_label)

        gif_path = resource_path("Drift.gif")
        self.movie = QMovie(gif_path)
        if self.movie.isValid():
            self.gif_label.setMovie(self.movie)
            self.movie.start()
        else:
            self.gif_label.setText("Không thể load Drift.gif")

        # Các nút và tool như cũ ...
        tools = [
            ("Add New Parameter", "Add_new_parameter/add_new_parameter.exe"),
            ("Split Parameter Tool", "Split_parameter_tool/ParameterClonerPro.exe"),
            ("Update Parameter Tool", "Update_parameter/dcm_parameter_tool.exe")
        ]

        for label, exe_path in tools:
            btn = RedButton(label)
            btn.clicked.connect(lambda checked, path=exe_path: self.run_tool(path))
            self.layout.addWidget(btn)

        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.status_label)

    def resizeEvent(self, event):
        if self.movie:
            label_size = self.gif_label.size()
            self.movie.setScaledSize(label_size)
        return super().resizeEvent(event)
    def flash_status(self, message):
        self.status_label.setText(message)
        QTimer.singleShot(1500, lambda: self.status_label.setText("Ready"))

    def run_tool(self, relative_exe_path):
        exe_path = resource_path(relative_exe_path)
        if not os.path.isfile(exe_path):
            QMessageBox.critical(self, "Error", f"File tool không tồn tại:\n{exe_path}")
            return
        try:
            subprocess.Popen([exe_path])
            self.flash_status(f"Đã mở tool: {os.path.basename(exe_path)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Không thể mở tool:\n{e}")


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
