from PyQt5.QtWidgets import QFileDialog


def browse_input_dir():
    options = QFileDialog.Options()
    options |= QFileDialog.ReadOnly
    input_dir = QFileDialog.getExistingDirectory(
        None, "Select Input Directory", "", options=options)
    return input_dir


def browse_output_dir():
    options = QFileDialog.Options()
    options |= QFileDialog.ReadOnly
    output_dir = QFileDialog.getExistingDirectory(
        None, "Select Output Directory", "", options=options)
    return output_dir


def format_time(seconds):
    h, remainder = divmod(seconds, 3600)
    m, s = divmod(remainder, 60)
    return f"{int(h)}h {int(m)}m {int(s)}s"


def get_ffmpeg_path():
    # Return the path to the ffmpeg executable
    return "ffmpeg"
