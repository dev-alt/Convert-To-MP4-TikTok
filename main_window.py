import os
from PyQt5.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QComboBox, QPushButton, QProgressBar, QFileDialog,
                             QMessageBox, QSpinBox, QGroupBox, QFormLayout)
from convert_thread import ConvertThread
from utils import browse_input_dir, browse_output_dir, get_ffmpeg_path, format_time
from settings import Settings
import re


class MainWindow(QMainWindow):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.settings = Settings('settings.json')
        self.init_converter()
        self.init_ui()
        self.conversion_ui = {}
        self.connect_signals()
        self.input_dir = ""
        self.output_dir = ""

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

        # Load and save settings buttons
        settings_group = QGroupBox("Settings")
        settings_layout = QFormLayout()
        self.load_settings_button = QPushButton("Load Settings")
        self.load_settings_button.clicked.connect(self.load_settings)
        settings_layout.addRow(
            QLabel("Load Settings:"), self.load_settings_button)
        self.save_settings_button = QPushButton("Save Settings")
        self.save_settings_button.clicked.connect(self.save_settings)
        settings_layout.addRow(
            QLabel("Save Settings:"), self.save_settings_button)
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def init_converter(self):
        self.converter = ConvertThread(self.logger)
        self.converter.new_conversion_signal.connect(
            lambda input_file, output_file: self.conversion_ui.update(
                {
                    output_file: self.create_new_conversion_ui(
                        input_file, output_file
                    )
                }
            )
        )
        self.converter.progress_signal.connect(self.update_progress)
        self.converter.time_remaining_signal.connect(
            self.update_time_remaining)
        print("Connected time_remaining_signal to update_time_remaining function.")
        self.converter.error_signal.connect(self.display_error)

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
        input_dir = browse_input_dir(self)
        output_dir = browse_output_dir(self)

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

        # Set the properties for the converter object
        self.converter.codec = codec
        self.converter.input_dir = input_dir
        self.converter.output_dir = output_dir
        self.converter.video_files = video_files  # Set video_files here
        self.converter.ffmpeg_path = ffmpeg_path
        self.converter.num_worker_threads = num_worker_threads

        # Update the total_files attribute for the ConvertThread object
        self.converter.total_files = len(video_files)

        # Update the time_remaining_label to display "Estimated time remaining: N/A"
        self.time_remaining_label.setText("Estimated time remaining: N/A")

        self.converter.start()
        self.input_dir = input_dir

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
        total_seconds = float(time_remaining)
        formatted_time = format_time(total_seconds)
        self.time_remaining_label.setText(
            f"Estimated time remaining: {formatted_time}")

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
        time_remaining_label = QLabel("Estimated time remaining: 0s")
        layout.addWidget(time_remaining_label)
        container = QWidget()
        container.setLayout(layout)
        self.layout().addWidget(container)
        return progress_bar, current_file_label, current_progress_label, time_remaining_label

    def display_error(self, error_msg):
        QMessageBox.critical(self, "Conversion Error", error_msg)

    def apply_settings(self):
        self.comboBox.setCurrentText(self.settings.codec)
        self.thread_spinbox.setValue(self.settings.num_worker_threads)

    def save_settings(self):
        self.settings.codec = self.comboBox.currentText()
        self.settings.input_dir = self.input_dir
        self.settings.output_dir = self.output_dir
        self.settings.num_worker_threads = self.thread_spinbox.value()
        self.settings.save()

    def load_settings(self):
        if self.settings.exists():
            self.settings.load()
            self.apply_settings()
            self.logger.info("Settings loaded successfully.")
        else:
            self.logger.info(
                "Settings file not found. Using default settings.")
