# main.py
import sys
import os
from PyQt6.QtWidgets import QApplication
from ui.main_window import ImageApp

def main():
    # ---------------------------------------------------------
    # System Configuration
    # ---------------------------------------------------------
    # Suppress the benign Linux AT-SPI accessibility warning
    os.environ["QT_LOGGING_RULES"] = "qt.accessibility.atspi.warning=false"
    
    app = QApplication(sys.argv)
    
    # Set global application font for a clean, modern look
    font = app.font()
    font.setFamily("Segoe UI")
    app.setFont(font)
    
    window = ImageApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()