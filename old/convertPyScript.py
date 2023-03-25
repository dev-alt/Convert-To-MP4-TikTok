import os
import sys
import subprocess
from threading import Thread
from queue import Queue
from tqdm import tqdm

# Set up your input and output directories
input_dir = 'D:\\Other\\Jp\\'
output_dir = 'F:\\compiled\\'

# Check if the input and output directories exist
if not os.path.exists(input_dir):
    print(f"Input directory '{input_dir}' does not exist.")
    sys.exit(1)

if not os.path.exists(output_dir):
    print(f"Output directory '{output_dir}' does not exist.")
    sys.exit(1)

# Set up FFmpeg path and other settings
ffmpeg_path = 'C:\\Users\\andre\\Desktop\\Libraries\\ffmpeg.exe'
max_buffer_size = 102400
logfile = 'conversion_log.txt'

# Get a list of all video files in the input directory
video_files = []
for root, _, files in os.walk(input_dir):
    for file in files:
        if file.lower().endswith(('.avi', '.mkv', '.wmv', '.flv', '.webm')):
            video_files.append(os.path.join(root, file))

# Function to process videos


def process_video(input_file, output_file, progress_bar):
    command = [ffmpeg_path, '-i', input_file, '-map_metadata', '-1', '-map_chapters', '-1', '-c:v', 'libx264', '-crf', '18', '-preset',
               'medium', '-c:a', 'aac', '-b:a', '128k', '-bufsize', f"{max_buffer_size}", '-bsf:v', 'mpeg4_unpack_bframes', '-an', output_file]
    process = subprocess.Popen(
        command, stderr=subprocess.PIPE, universal_newlines=True)
    while True:
        output = process.stderr.readline()
        if output == '' or process.poll() is not None:
            break
        if 'frame=' in output:
            progress_bar.set_description(f"Converting '{input_file}'")
            progress_bar.update(1)
    return process.poll()

# Worker function for multi-threading


def worker():
    while True:
        item = q.get()
        if item is None:
            break
        input_file, output_file, progress_bar = item
        process_video(input_file, output_file, progress_bar)
        q.task_done()


# Create a queue and start worker threads
num_worker_threads = 4
q = Queue()
for _ in range(num_worker_threads):
    t = Thread(target=worker)
    t.start()

# Initialize a progress bar
with tqdm(total=len(video_files), ncols=100) as pbar:
    for input_file in video_files:
        # Check if the output file already exists
        output_file = os.path.join(output_dir, os.path.splitext(
            os.path.basename(input_file))[0] + '.mp4')
        if os.path.exists(output_file):
            pbar.write(
                f"Output file '{output_file}' already exists, skipping conversion of '{input_file}'.")
            pbar.update(1)
        else:
            # Add the item to the queue for processing
            q.put((input_file, output_file, pbar))

# Wait for all tasks to complete and stop the worker threads
q.join()
for _ in range(num_worker_threads):
    q.put(None)
for t in q.queue:
    t.join()
