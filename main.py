import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLabel
from PyQt6.QtGui import QIcon, QFont, QPalette, QColor
from PyQt6.QtCore import Qt

import database
from ui_data_entry import DataEntryTab
from ui_dashboard import DashboardTab

class AttendanceApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Attendance Report Generator")
        self.setMinimumSize(900, 600)

        # Initialize App Database
        database.init_db()

        self.init_ui()

    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main Layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # Title Label
        title = QLabel("Attendance Report Generator")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #4CAF50; margin: 10px 0px 20px 0px;")
        layout.addWidget(title)

        # Tabs
        self.tabs = QTabWidget()
        self.data_entry_tab = DataEntryTab()
        self.dashboard_tab = DashboardTab()

        self.tabs.addTab(self.data_entry_tab, "Data Entry")
        self.tabs.addTab(self.dashboard_tab, "Analytics Dashboard")
        
        # Make tabs slightly larger and modern
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                background: #2d2d30;
                color: #ffffff;
                padding: 10px 20px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #3e3e42;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background: #3e3e42;
                border-bottom: 2px solid #4CAF50;
            }
            QTabBar::tab:hover {
                background: #4a4a4f;
            }
            QTabWidget::pane {
                border: 1px solid #3e3e42;
                background: #1e1e1e;
            }
        """)

        layout.addWidget(self.tabs)

def main():
    app = QApplication(sys.argv)
    
    # Apply a global dark theme style
    app.setStyle("Fusion")
    
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
    dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(45, 45, 45))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(30, 30, 30))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    app.setPalette(dark_palette)
    
    app.setStyleSheet("""
        QToolTip { 
            color: #ffffff; 
            background-color: #2a82da; 
            border: 1px solid white; 
        }
        QPushButton {
            background-color: #3e3e42;
            border: 1px solid #555;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #4CAF50;
            border: 1px solid #4CAF50;
        }
        QPushButton:pressed {
            background-color: #45a049;
        }
        QPushButton:checked {
            background-color: #4CAF50;
            color: white;
            border: 1px solid #4CAF50;
        }
        QPushButton#actionButton {
            background-color: #2196F3;
            color: white;
            font-weight: bold;
            border: none;
        }
        QPushButton#actionButton:hover {
            background-color: #1e88e5;
        }
        QLineEdit, QComboBox, QDateEdit {
            background-color: #3e3e42;
            color: white;
            border: 1px solid #555;
            padding: 6px;
            border-radius: 4px;
        }
        QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
            border: 1px solid #4CAF50;
        }
        QGroupBox {
            font-weight: bold;
            border: 1px solid #555;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 15px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            color: #ccc;
        }
    """)

    window = AttendanceApp()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
