from PyQt5.QtWidgets import QApplication
import sys
from main_window import MainWindow
from logger import setup_logger
from settings import Settings

logger = setup_logger()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    settings = Settings("settings.json")
    settings.load()

    main_window = MainWindow(logger)
    main_window.setWindowTitle("Video Converter")
    main_window.show()

    sys.exit(app.exec_())
