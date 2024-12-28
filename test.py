from PyQt6.QtWidgets import QApplication, QMainWindow
from src.widgets.gradient_editor import GradientEditor
import sys

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gradient Editor Test")
        self.gradient_editor = GradientEditor(self)
        self.setCentralWidget(self.gradient_editor)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())