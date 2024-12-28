from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

def set_dark_mode(app):
   palette = QPalette()
   
   # Window background
   palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, QColor(30, 30, 30))
   palette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, QColor(30, 30, 30))
   palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, QColor(30, 30, 30))
   
   # Window text
   palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, QColor(200, 200, 200))
   palette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, QColor(200, 200, 200))
   palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(80, 80, 80))
   
   # Base background
   palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, QColor(45, 45, 45))
   palette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, QColor(45, 45, 45))
   palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, QColor(35, 35, 35))
   
   # Alternate background
   palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
   palette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
   palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.AlternateBase, QColor(43, 43, 43))
   
   # Tooltips
   palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipBase, QColor(65, 65, 65))
   palette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipBase, QColor(65, 65, 65))
   palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipBase, QColor(55, 55, 55))
   
   palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipText, QColor(200, 200, 200))
   palette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipText, QColor(200, 200, 200))
   palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipText, QColor(80, 80, 80))
   
   # Text
   palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, QColor(200, 200, 200))
   palette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, QColor(200, 200, 200))
   palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(80, 80, 80))
   
   # Buttons
   palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, QColor(53, 53, 53))
   palette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, QColor(53, 53, 53))
   palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, QColor(50, 50, 50))

   # Button text
   palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, QColor(200, 200, 200))
   palette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, QColor(200, 200, 200))
   palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(100, 100, 100))
   
   # Bright text
   palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
   palette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
   palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.BrightText, Qt.GlobalColor.darkRed)
   
   # Links
   palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Link, QColor(42, 130, 218))
   palette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Link, QColor(42, 130, 218))
   palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Link, QColor(22, 100, 178))
   
   # Highlight
   palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Highlight, QColor(42, 130, 218))
   palette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Highlight, QColor(42, 130, 218))
   palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, QColor(22, 100, 178))
   
   # Highlighted text
   palette.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
   palette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
   palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText, QColor(40, 40, 40))
   
   app.setPalette(palette)
   app.setStyleSheet(
    """
        QPushButton:disabled {
            background-color: rgb(50, 50, 50);
            color: rgb(100, 100, 100);
        }
    """
   )