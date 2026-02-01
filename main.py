import sys
from PyQt6.QtWidgets import QApplication
from interface import GitarTakipApp

DARK_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}

QTabWidget::pane {
    border: 1px solid #333;
    background-color: #1e1e1e;
}
QTabBar::tab {
    background: #2b2b2b;
    color: #888;
    padding: 10px 25px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    font-weight: bold;
}
QTabBar::tab:selected {
    background: #3c3c3c;
    color: #40a7e3;
    border-bottom: 2px solid #40a7e3;
}

QPushButton {
    background-color: #546e7a; 
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 5px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #607d8b; 
}
QPushButton:pressed {
    background-color: #37474f;
}

#btn_success { background-color: #2e7d32; } 
#btn_success:hover { background-color: #388e3c; }

#btn_warning { background-color: #f57f17; color: white; }
#btn_warning:hover { background-color: #fbc02d; }

#btn_danger { background-color: #c62828; }
#btn_danger:hover { background-color: #d32f2f; }

#btn_info { background-color: #1565c0; } 
#btn_info:hover { background-color: #1976d2; }

QLineEdit, QComboBox {
    background-color: #2b2b2b;
    border: 1px solid #444;
    color: white;
    padding: 6px;
    border-radius: 4px;
}
QLineEdit:focus, QComboBox:focus {
    border: 1px solid #40a7e3;
    background-color: #333;
}

QTreeWidget, QTableWidget {
    background-color: #2b2b2b;
    border: 1px solid #444;
    color: white;
    alternate-background-color: #323232;
}
QHeaderView::section {
    background-color: #444;
    color: white;
    padding: 6px;
    border: none;
    font-weight: bold;
}
"""

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLESHEET)
    
    window = GitarTakipApp()
    window.show()
    sys.exit(app.exec())