import logging

from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout

from ltrt.system.path_utilities import create_new_recording_folder

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        widget = QWidget()
        self.setMinimumSize(1080, 720)
        self.setWindowTitle("Let's Try Real Time")

        widget.setLayout(layout)
        self.setCentralWidget(widget)
        

def main():
    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exec()
    win.close()



if __name__ == "__main__":
    main()