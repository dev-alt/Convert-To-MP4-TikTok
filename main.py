from PyQt5.QtWidgets import QApplication
import sys
from main_window import MainWindow
from logger import setup_logger

logger = setup_logger()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = MainWindow(logger)
    main_window.setWindowTitle("Video Converter")
    main_window.show()

    sys.exit(app.exec_())
