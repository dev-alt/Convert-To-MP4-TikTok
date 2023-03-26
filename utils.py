from PyQt5.QtWidgets import QFileDialog
from settings import Settings


def browse_input_dir(main_window):
    settings = main_window.settings
    if settings.input_dir:
        return settings.input_dir

    options = QFileDialog.Options()
    options |= QFileDialog.ShowDirsOnly
    input_dir = QFileDialog.getExistingDirectory(
        main_window, "Select Input Directory", "", options=options)
    if input_dir:
        settings.input_dir = input_dir
        return input_dir
    return ""


def browse_output_dir(parent=None):
    options = QFileDialog.Options()
    options |= QFileDialog.ReadOnly
    output_dir = QFileDialog.getExistingDirectory(
        parent, "Select Output Directory", "", options=options)
    return output_dir


def format_time(seconds):
    """Formats time in seconds to HH:MM:SS string format."""
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def get_ffmpeg_path():
    # Return the path to the ffmpeg executable
    return "ffmpeg"
