import os
import subprocess
import time
import threading
from threading import Thread
from queue import Queue
from PyQt5.QtCore import QThread, pyqtSignal
import json


class ConvertThread(QThread):
    progress_signal = pyqtSignal(str, str, float)
    time_remaining_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, codec, input_dir, output_dir, video_files, ffmpeg_path, num_worker_threads, logger):
        super().__init__()
        self.logger = logger
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
        with self.cond:
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
            self.total_duration = self.get_video_duration(input_file)
            success = self.process_video(input_file, output_file)
            if not success:
                failed_files.append(input_file)
            converted_files += 1
            self.progress_signal.emit(
                input_file, output_file, converted_files / self.total_files * 100)

            elapsed_time = time.time() - start_time
            remaining_time = (self.total_files - converted_files) * \
                (elapsed_time / converted_files)
            self.time_remaining_signal.emit(remaining_time)
            q.task_done()

    def process_video(self, input_file, output_file):
        command = [self.ffmpeg_path, '-i', input_file, '-map_metadata', '-1', '-map_chapters', '-1', '-c:v', self.codec, '-crf', '18', '-preset',
                   'medium', '-c:a', 'aac', '-b:a', '128k', '-bufsize', '102400', '-an', output_file]
        try:
            process = subprocess.Popen(
                command, stderr=subprocess.PIPE, universal_newlines=True)

            while True:
                line = process.stderr.readline()
                if not line:
                    break
                # Parse the line to get the progress percentage
                progress = self.parse_progress(line)
                if progress is not None:
                    self.progress_signal.emit(
                        input_file, output_file, progress)

            process.wait()
            if process.returncode == 0:
                self.logger.info(
                    f"Successfully converted '{input_file}' to '{output_file}'.")
                return True
            else:
                self.logger.error(
                    f"Error converting '{input_file}': Non-zero return code")
                return False
        except Exception as e:
            self.logger.error(f"Error converting '{input_file}': {e}")
            return False

    def parse_progress(self, line):
        # Parse FFmpeg output to get the progress percentage
        if 'frame=' in line:
            parts = line.split()
            for part in parts:
                if 'time=' in part:
                    current_time = part.split('=')[-1]
                    h, m, s = map(float, current_time.split(':'))
                    current_seconds = h * 3600 + m * 60 + s
                    if self.total_duration > 0:
                        progress = (current_seconds /
                                    self.total_duration) * 100
                        return progress
        return None

    def get_video_duration(self, input_file):
        command = [os.path.join(os.path.dirname(self.ffmpeg_path), "ffprobe"), "-v", "error", "-show_entries", "format=duration", "-of",
                   "json", input_file]
        try:
            output = subprocess.check_output(command, universal_newlines=True)
            metadata = json.loads(output)
            duration = float(metadata["format"]["duration"])
            return duration
        except Exception as e:
            self.logger.error(f"Error getting duration of '{input_file}': {e}")
            return None
