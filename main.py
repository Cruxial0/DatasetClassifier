import sys
from PyQt6.QtWidgets import QApplication
from src.windows.project_selection import ProjectSelectionWindow
from src.theme import set_dark_mode

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ProjectSelectionWindow()
    ex.show()
    # ex = DatasetClassifier()
    # ex.show()
    sys.exit(app.exec())