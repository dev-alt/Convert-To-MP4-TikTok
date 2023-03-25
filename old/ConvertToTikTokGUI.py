import os
import sys
import subprocess
import time
import threading
from threading import Thread, Condition
from queue import Queue
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QComboBox, QPushButton, QProgressBar, QFileDialog,
                             QMessageBox, QSpinBox, QSlider, QHBoxLayout, QLineEdit, QGroupBox, QFormLayout)
from PyQt5.QtCore import QStandardPaths, QThread, pyqtSignal


class ConvertThread(QThread):
    progress_signal = pyqtSignal(str, str, float)
    time_remaining_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, codec, input_dir, output_dir, video_files, ffmpeg_path, num_worker_threads):
        super().__init__()
        self.codec = codec
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.video_files = video_files
        self.ffmpeg_path = ffmpeg_path
        self.num_worker_threads = num_worker_threads
        self.total_files = len(self.video_files)
        self.is_paused = False
        self.is_stopped = False
        self.cond = threading.Condition()

    def run(self):
        q = Queue()
        failed_files = []
        total_files = len(self.video_files)
        converted_files = 0

        threads = []
        for _ in range(self.num_worker_threads):
            t = Thread(target=self.worker, args=(q, failed_files))
            t.start()
            threads.append(t)

        start_time = time.time()
        for input_file in self.video_files:
            output_file = os.path.join(self.output_dir, os.path.splitext(
                os.path.basename(input_file))[0] + '.mp4')
            if os.path.exists(output_file):
                print(
                    f"Output file '{output_file}' already exists, skipping conversion of '{input_file}'.")
                self.progress_signal.emit(
                    input_file, output_file, converted_files / total_files * 100)
            else:
                q.put((input_file, output_file))

        q.join()
        for _ in range(self.num_worker_threads):
            q.put(None)
        for t in threads:
            t.join()

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False
        self.cond.notify_all()

    def stop(self):
        self.is_stopped = True
        self.is_paused = False
        self.cond.notify_all()

    def worker(self, q, failed_files):
        converted_files = 0
        start_time = time.time()
        while True:
            with self.cond:
                while self.is_paused:
                    self.cond.wait()
            item = q.get()
            if item is None:
                break
            input_file, output_file = item
            success = self.process_video(input_file, output_file)
            if not success:
                failed_files.append(input_file)
            converted_files += 1
            self.progress_signal.emit(
                input_file, output_file, converted_files / self.total_files * 100)

            elapsed_time = time.time() - start_time
            remaining_time = (self.total_files - converted_files) * \
                (elapsed_time / converted_files)
            self.time_remaining_signal.emit(str(remaining_time))
            q.task_done()

    def process_video(self, input_file, output_file):
        command = [self.ffmpeg_path, '-i', input_file, '-map_metadata', '-1', '-map_chapters', '-1', '-c:v', self.codec, '-crf', '18', '-preset',
                   'medium', '-c:a', 'aac', '-b:a', '128k', '-bufsize', '102400', '-an', output_file]
        try:
            subprocess.run(command, check=True,
                           stderr=subprocess.PIPE, universal_newlines=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error converting '{input_file}': {e.stderr}")
            return False


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.converter = None
        self.conversion_ui = {}
        self.connect_signals()

    def init_ui(self):
        layout = QVBoxLayout()

        # Pause button
        self.pause_resume_button = QPushButton("Pause")
        self.pause_resume_button.clicked.connect(self.pause_resume_conversion)
        layout.addWidget(self.pause_resume_button)

        # Stop button
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_conversion)
        layout.addWidget(self.stop_button)

        # Codec selection
        codec_group = QGroupBox("Codec Selection")
        codec_layout = QFormLayout()
        self.comboBox = QComboBox()
        self.comboBox.addItem("libx264")
        codec_layout.addRow(QLabel("Codec:"), self.comboBox)
        self.label = QLabel("Selected Codec: libx264")
        codec_layout.addWidget(self.label)
        self.comboBox.currentTextChanged.connect(self.update_label)
        codec_group.setLayout(codec_layout)
        layout.addWidget(codec_group)

        # Threads selection
        threads_group = QGroupBox("Thread Settings")
        threads_layout = QFormLayout()
        self.thread_spinbox = QSpinBox()
        self.thread_spinbox.setMinimum(1)
        self.thread_spinbox.setMaximum(8)
        self.thread_spinbox.setValue(4)
        threads_layout.addRow(
            QLabel("Number of Threads:"), self.thread_spinbox)
        threads_group.setLayout(threads_layout)
        layout.addWidget(threads_group)

        # Current file and progress
        self.current_file_label = QLabel("Current file: N/A")
        layout.addWidget(self.current_file_label)
        self.current_progress_label = QLabel("Progress: N/A")
        layout.addWidget(self.current_progress_label)

        # Estimated time remaining
        self.time_remaining_label = QLabel("Estimated time remaining: N/A")
        layout.addWidget(self.time_remaining_label)

        # Start process button
        self.start_process_button = QPushButton("Start Process")
        self.start_process_button.clicked.connect(self.apply_codec)
        layout.addWidget(self.start_process_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def connect_signals(self):
        if self.converter is None:
            return
        self.converter.new_conversion_signal.connect(lambda input_file, output_file: self.conversion_ui.update(
            {output_file: self.create_new_conversion_ui(input_file, output_file)}))

    def pause_resume_conversion(self):
        if not hasattr(self, 'converter') or self.converter is None:
            return
        if self.converter.is_paused:
            self.converter.resume()
            self.pause_resume_button.setText("Pause")
        else:
            self.converter.pause()
            self.pause_resume_button.setText("Resume")

    def stop_conversion(self):
        if not hasattr(self, 'converter') or self.converter is None:
            return

        self.converter.stop()
        self.pause_resume_button.setEnabled(False)
        self.stop_button.setEnabled(False)

    def update_label(self, text):
        if text == "mpeg4":
            self.label.setText(
                "Selected Codec: mpeg4 (with mpeg4_unpack_bframes if needed)")
        else:
            self.label.setText(f"Selected Codec: {text}")

    def apply_codec(self):
        codec = self.comboBox.currentText()
        print(f"Applying codec: {codec}")

        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        input_dir = QFileDialog.getExistingDirectory(
            self, "Select Input Directory", "", options=options)
        output_dir = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", "", options=options)

        if not os.path.exists(input_dir):
            QMessageBox.critical(
                self, "Error", f"Input directory '{input_dir}' does not exist.")
            return

        if not os.path.exists(output_dir):
            QMessageBox.critical(
                self, "Error", f"Output directory '{output_dir}' does not exist.")
            return

        video_files = []
        for root, _, files in os.walk(input_dir):
            for file in files:
                if file.lower().endswith(('.avi', '.mkv', '.wmv', '.flv', '.webm')):
                    video_files.append(os.path.join(root, file))

        ffmpeg_path = get_ffmpeg_path()
        num_worker_threads = self.thread_spinbox.value()

        self.converter = ConvertThread(
            codec, input_dir, output_dir, video_files, ffmpeg_path, num_worker_threads)
        self.converter.progress_signal.connect(self.update_progress)
        self.converter.time_remaining_signal.connect(
            self.update_time_remaining)
        if self.converter is not None:
            self.converter.error_signal.connect(self.display_error)
        self.converter.start()

    def update_progress(self, input_file, output_file, progress):
        self.current_file_label.setText(f"Current file: {input_file}")
        self.current_progress_label.setText(f"Progress: {progress}%")
        if output_file in self.conversion_ui:
            progress_bar, current_file_label, current_progress_label, time_remaining_label = self.conversion_ui[
                output_file]
            progress_bar.setValue(progress)
            current_file_label.setText(f"Current file: {input_file}")
            current_progress_label.setText(f"Progress: {progress}%")

    def update_time_remaining(self, time_remaining):
        self.time_remaining_label.setText(
            f"Estimated time remaining: {time_remaining} seconds")
        for progress_bar in self.conversion_ui.values():
            progress_bar[3].setText(
                f"Estimated time remaining: {time_remaining} seconds")

    def create_new_conversion_ui(self, input_file, output_file):
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Input file: {input_file}"))
        layout.addWidget(QLabel(f"Output file: {output_file}"))
        progress_bar = QProgressBar()
        layout.addWidget(progress_bar)
        current_file_label = QLabel("Current file: N/A")
        layout.addWidget(current_file_label)
        current_progress_label = QLabel("Progress: N/A")
        layout.addWidget(current_progress_label)
        time_remaining_label = QLabel("Estimated time remaining: N/A")
        layout.addWidget(time_remaining_label)
        container = QWidget()
        container.setLayout(layout)
        self.layout().addWidget(container)
        return progress_bar, current_file_label, current_progress_label, time_remaining_label

    def display_error(self, error_msg):
        QMessageBox.critical(self, "Conversion Error", error_msg)


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


def get_ffmpeg_path():
    # Return the path to the ffmpeg executable
    return "ffmpeg"


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.setWindowTitle("Video Converter")
    main_window.show()

    sys.exit(app.exec_())
