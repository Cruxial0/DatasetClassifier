from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

def set_dark_mode(app):
    # app.setStyle("Windows")
    palette = QPalette()
    
    # Dark gray for window background
    palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
    
    # Light gray for text
    palette.setColor(QPalette.ColorRole.WindowText, QColor(200, 200, 200))
    
    # Darker gray for input fields and other base elements
    palette.setColor(QPalette.ColorRole.Base, QColor(45, 45, 45))
    
    # Mid-dark gray for alternate backgrounds
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    
    # Light gray for tooltips
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(200, 200, 200))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(200, 200, 200))
    
    # Light gray for text
    palette.setColor(QPalette.ColorRole.Text, QColor(200, 200, 200))
    
    # Dark gray for buttons
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    
    # Light gray for button text
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(200, 200, 200))
    
    # Keep bright text red for consistency
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    
    # You can adjust this blue color if needed
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    
    # Highlight color (for selections)
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    
    app.setPalette(palette)