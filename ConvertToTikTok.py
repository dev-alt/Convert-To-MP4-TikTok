import os
import sys
import subprocess
from threading import Thread
from queue import Queue
from tqdm import tqdm
import tkinter as tk
from tkinter import filedialog


def browse_input_dir():
    input_dir = filedialog.askdirectory()
    return input_dir


def browse_output_dir():
    output_dir = filedialog.askdirectory()
    return output_dir


root = tk.Tk()
root.withdraw()

input_dir = browse_input_dir()
output_dir = browse_output_dir()

if not os.path.exists(input_dir):
    print(f"Input directory '{input_dir}' does not exist.")
    sys.exit(1)

if not os.path.exists(output_dir):
    print(f"Output directory '{output_dir}' does not exist.")
    sys.exit(1)

ffmpeg_path = 'C:\\Users\\andre\\Desktop\\Libraries\\ffmpeg.exe'
max_buffer_size = 102400
logfile = 'conversion_log.txt'

video_files = []
for root, _, files in os.walk(input_dir):
    for file in files:
        if file.lower().endswith(('.avi', '.mkv', '.wmv', '.flv', '.webm')):
            video_files.append(os.path.join(root, file))


def process_video(input_file, output_file, progress_bar):
    command = [ffmpeg_path, '-i', input_file, '-map_metadata', '-1', '-map_chapters', '-1', '-c:v', 'libx264', '-crf', '18', '-preset',
               'medium', '-c:a', 'aac', '-b:a', '128k', '-bufsize', f"{max_buffer_size}", '-an', output_file]
    try:
        subprocess.run(command, check=True,
                       stderr=subprocess.PIPE, universal_newlines=True)
        progress_bar.set_description(f"Converted '{input_file}'")
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
    t = Thread(target=worker)
    t.start()

with tqdm(total=len(video_files), ncols=100) as pbar:
    for input_file in video_files:
        output_file = os.path.join(output_dir, os.path.splitext(
            os.path.basename(input_file))[0] + '.mp4')
        if os.path.exists(output_file):
            pbar.write(
                f"Output file '{output_file}' already exists, skipping conversion of '{input_file}'.")
            pbar.update(1)
        else:
            q.put((input_file, output_file, pbar))

q.join()
for _ in range(num_worker_threads):
    q.put(None)
for t in q.queue:
    t.join()

if failed_files:
    print("Failed to convert the following files:")
    for file in failed_files:
        print(file)
