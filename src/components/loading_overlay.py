from PyQt6.QtWidgets import QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMovie

class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(parent.size())
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        layout = QVBoxLayout(self)
        label = QLabel(self)
        movie = QMovie("loading_spinner.gif")  # Make sure to have this GIF in your resources
        label.setMovie(movie)
        layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
        movie.start()

        self.setStyleSheet("background-color: rgba(0, 0, 0, 150);")
        self.hide()
