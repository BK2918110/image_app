# config.py

LIGHT_MODERN_STYLE = """
    QMainWindow {
        background-color: #F9FAFB;
    }
    
    QWidget#Sidebar {
        background-color: #FFFFFF;
        border-right: 1px solid #E5E7EB;
    }
    
    QLabel#ImageLabel {
        background-color: #FFFFFF;
        border: 2px dashed #D1D5DB;
        border-radius: 10px;
        color: #6B7280;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 16px;
    }
    
    /* Standard Button Styling */
    QPushButton {
        background-color: #FFFFFF;
        color: #374151;
        border: 1px solid #D1D5DB;
        border-radius: 6px;
        padding: 10px;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 13px;
        font-weight: 600;
        text-align: left;
        padding-left: 15px;
    }
    
    QPushButton:hover {
        background-color: #F3F4F6;
        border: 1px solid #9CA3AF;
    }
    
    QPushButton:pressed {
        background-color: #E5E7EB;
        border: 1px solid #6B7280;
    }
    
    /* Primary Action Button (Open Image) */
    QPushButton#PrimaryButton {
        background-color: #2563EB; /* Professional Blue */
        color: white;
        border: none;
    }
    
    QPushButton#PrimaryButton:hover {
        background-color: #1D4ED8;
    }
    
    QPushButton#PrimaryButton:pressed {
        background-color: #1E3A8A;
    }
    
    /* Section Headers */
    QLabel#SectionHeader {
        color: #9CA3AF;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 11px;
        font-weight: bold;
        text-transform: uppercase;
        margin-top: 10px;
        margin-bottom: 5px;
    }

    /* ---------------------------------------------------
       State Management & Success Actions 
       --------------------------------------------------- */
       
    /* Success Action Button (Save Image) */
    QPushButton#SuccessButton {
        background-color: #10B981; /* Modern Emerald Green */
        color: white;
        border: none;
    }
    
    QPushButton#SuccessButton:hover {
        background-color: #059669;
    }
    
    QPushButton#SuccessButton:pressed {
        background-color: #047857;
    }
    
    /* Disabled State for any button */
    QPushButton:disabled {
        background-color: #E5E7EB;
        color: #9CA3AF;
        border: 1px solid #D1D5DB;
    }

    /* Navigation Buttons */
    QPushButton#NavButton {
        background-color: #F3E8FF; /* Subtle Purple */
        color: #7E22CE;
        border: 1px solid #D8B4FE;
        font-weight: bold;
        text-align: center;
        padding-left: 0px;
    }
    QPushButton#NavButton:hover {
        background-color: #E9D5FF;
    }

    /* Danger Action Button (Clear/Delete) */
    QPushButton#DangerButton {
        background-color: #EF4444; /* Modern Red */
        color: white;
        border: none;
    }
    
    QPushButton#DangerButton:hover {
        background-color: #DC2626;
    }
    
    QPushButton#DangerButton:pressed {
        background-color: #B91C1C;
    }

    /* =========================================
       MODERN QSLIDER (SLICK & PERFECTLY ROUND)
       ========================================= */
    QSlider {
        min-height: 24px;
    }

    QSlider::groove:horizontal {
        border: none;
        height: 4px;
        background: #E5E7EB;
        border-radius: 2px;
        margin: 10px 0;
    }
    
    QSlider::sub-page:horizontal {
        background: #3B82F6;
        border-radius: 2px;
        margin: 10px 0;
        height: 4px;
    }
    
    QSlider::handle:horizontal {
        background: #2563EB;
        border: 3px solid #FFFFFF;
        width: 14px;
        height: 14px;
        margin: -8px 0;
        border-radius: 10px;
    }
    
    QSlider::handle:horizontal:hover {
        background: #1D4ED8;
        border: 3px solid #F3F4F6;
    }
    
    QSlider::handle:horizontal:pressed {
        background: #1E3A8A;
        border: 3px solid #E5E7EB;
    }

    /* =========================================
       MASTER NAVIGATION SIDEBAR
       ========================================= */
    QWidget#MasterNav {
        background-color: #1F2937; /* Dark Slate for heavy contrast */
    }
    
    QPushButton#MasterNavButton {
        background-color: transparent;
        color: #9CA3AF;
        border: none;
        border-radius: 0px;
        text-align: left;
        padding: 15px 20px;
        font-size: 14px;
        font-weight: bold;
    }
    
    QPushButton#MasterNavButton:hover {
        background-color: #374151;
        color: #FFFFFF;
    }
    
    QPushButton#MasterNavButton:checked {
        background-color: #2563EB;
        color: #FFFFFF;
        border-left: 4px solid #60A5FA; /* Blue indicator line */
    }

    /* =========================================
       CONVOLUTION & MATRIX INPUTS
       ========================================= */
    QComboBox {
        background-color: #FFFFFF;
        border: 1px solid #D1D5DB;
        border-radius: 6px;
        padding: 8px 15px;
        color: #374151;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 13px;
        font-weight: 600;
    }
    
    QComboBox::drop-down {
        border: none;
        width: 30px;
    }
    
    QLineEdit#MatrixInput {
        background-color: #F9FAFB;
        border: 1px solid #D1D5DB;
        border-radius: 4px;
        padding: 8px 2px;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 14px;
        font-weight: bold;
        color: #1F2937;
    }
    
    QLineEdit#MatrixInput:focus {
        border: 2px solid #2563EB;
        background-color: #FFFFFF;
    }
"""