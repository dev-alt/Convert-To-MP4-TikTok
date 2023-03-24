import os
import sys
import subprocess
from threading import Thread
from queue import Queue
from tqdm import tqdm
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QComboBox, QPushButton, QProgressBar, QFileDialog
from PyQt5.QtCore import QStandardPaths, QThread, pyqtSignal


def browse_input_dir():
    input_dir = QFileDialog.getExistingDirectory(
        None, "Select input file folders")
    return input_dir


def browse_output_dir():
    output_dir = QFileDialog.getExistingDirectory(
        None, "Select output file folders")
    return output_dir


def get_ffmpeg_path():
    default_path = os.path.join(QStandardPaths.standardLocations(
        QStandardPaths.AppLocalDataLocation)[0], 'ffmpeg.exe')
    if os.path.exists(default_path):
        return default_path
    else:
        ffmpeg_path, _ = QFileDialog.getOpenFileName(
            None, "Select FFmpeg executable", "", "Executable Files (*.exe);;All Files (*)")
        if ffmpeg_path:
            return ffmpeg_path
        else:
            print("No FFmpeg executable selected. Exiting.")
            sys.exit(1)


def convert_videos(codec, input_dir, output_dir, progress_bar):

    if not os.path.exists(input_dir):
        print(f"Input directory '{input_dir}' does not exist.")
        sys.exit(1)

    if not os.path.exists(output_dir):
        print(f"Output directory '{output_dir}' does not exist.")
        sys.exit(1)

    ffmpeg_path = get_ffmpeg_path()
    max_buffer_size = 102400

    video_files = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(('.avi', '.mkv', '.wmv', '.flv', '.webm')):
                video_files.append(os.path.join(root, file))

    def process_video(input_file, output_file, progress_bar):
        command = [ffmpeg_path, '-i', input_file, '-map_metadata', '-1', '-map_chapters', '-1', '-c:v', codec, '-crf', '18', '-preset',
                   'medium', '-c:a', 'aac', '-b:a', '128k', '-bufsize', f"{max_buffer_size}", '-an', output_file]
        try:
            subprocess.run(command, check=True,
                           stderr=subprocess.PIPE, universal_newlines=True)
            progress_bar.setValue(progress_bar.value() + 1)
            progress_bar.update(1)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error converting '{input_file}': {e.stderr}")
            return False

    def worker():
        while True:
            item = q.get()
            if item is None:
                break
            input_file, output_file, progress_bar = item
            success = process_video(input_file, output_file, progress_bar)
            if not success:
                failed_files.append(input_file)
            q.task_done()

    num_worker_threads = 4
    q = Queue()
    failed_files = []

    for _ in range(num_worker_threads):
        threads = []
    for _ in range(num_worker_threads):
        t = Thread(target=worker)
        t.start()
        threads.append(t)

    with tqdm(total=len(video_files), ncols=100) as pbar:
        for input_file in video_files:
            output_file = os.path.join(output_dir, os.path.splitext(
                os.path.basename(input_file))[0] + '.mp4')
            if os.path.exists(output_file):
                pbar.write(
                    f"Output file '{output_file}' already exists, skipping conversion of '{input_file}'.")
                pbar.update(1)
            else:
                q.put((input_file, output_file, progress_bar))
                pbar.update(1)

    q.join()
    for _ in range(num_worker_threads):
        q.put(None)
    for t in threads:
        t.join()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.comboBox = QComboBox()
        self.comboBox.addItem("libx264")
        self.comboBox.addItem("mpeg4")
        layout.addWidget(self.comboBox)

        self.label = QLabel("Selected Codec: libx264")
        layout.addWidget(self.label)

        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_codec)
        layout.addWidget(self.apply_button)
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.comboBox.currentTextChanged.connect(self.update_label)

    def update_label(self, text):
        if text == "mpeg4":
            self.label.setText(
                "Selected Codec: mpeg4 (with mpeg4_unpack_bframes if needed)")
        else:
            self.label.setText(f"Selected Codec: {text}")

    def apply_codec(self):
        codec = self.comboBox.currentText()
        print(f"Applying codec: {codec}")

        input_dir = browse_input_dir()
        output_dir = browse_output_dir()

        if not os.path.exists(input_dir):
            print(f"Input directory '{input_dir}' does not exist.")
            return

        if not os.path.exists(output_dir):
            print(f"Output directory '{output_dir}' does not exist.")
            return

        # Conditionally add 'mpeg4_unpack_bframes' filter for 'mpeg4' codec if needed
        # if codec == "mpeg4":
            # Check if the 'mpeg4_unpack_bframes' filter is needed and add it here

        convert_videos(codec, input_dir, output_dir, self.progress_bar)


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
sys.exit(app.exec_())
