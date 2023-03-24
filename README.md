Convert Video Files to MP4 Format

his Python script can be used to convert all video files in a specified directory to the MP4 format. The script uses the ffmpeg library to perform the conversion and supports the following input formats: .avi, .mkv, .wmv, .flv, and .webm. The output files are saved to a specified directory with the .mp4 extension.

This script requires the following libraries:

    os
    sys
    subprocess
    threading
    queue
    PyQt5
    PyQt5.QtCore
    PyQt5.QtWidgets

In addition, you must have ffmpeg installed on your system and the ffmpeg executable must be located at C:\\Users\\andre\\Desktop\\Libraries\\ffmpeg.exe.
Usage

    Run the script in a Python environment (e.g., IDLE, VS Code, or the command line).
    When prompted, select the input directory containing the video files you want to convert.
    When prompted, select the output directory where the converted files will be saved.
    The script will convert each video file in the input directory to the MP4 format and save the output files to the specified output directory.
    A progress bar will be displayed to show the status of the conversion process, along with the current file being converted, its percent completion, and the estimated time to completion.
    If the output file for a particular video already exists, the script will skip that file and move on to the next one.
    When the script has finished, it will display a list of any files that failed to convert, along with their input and output file locations.

Update:

Convert Video Files to MP4 Format

This Python script can be used to convert all video files in a specified directory to the MP4 format. The script uses the ffmpeg library to perform the conversion and supports the following input formats: .avi, .mkv, .wmv, .flv, and .webm. The output files are saved to a specified directory with the .mp4 extension.

Prerequisites:

This script requires the following libraries:

c

os
sys
subprocess
threading
queue
tqdm
tkinter

In addition, you must have ffmpeg installed on your system and the ffmpeg executable must be located at C:\Users\andre\Desktop\Libraries\ffmpeg.exe.

Usage:
Run the script in a Python environment (e.g., IDLE, VS Code, or the command line).
When prompted, select the input directory containing the video files you want to convert.
When prompted, select the output directory where the converted files will be saved.
The script will convert each video file in the input directory to the MP4 format and save the output files to the specified output directory.
A progress bar will be displayed to show the status of the conversion process, along with the current file being converted, its percent completion, and the estimated time to completion.
If the output file for a particular video already exists, the script will skip that file and move on to the next one.
When the script has finished, it will display a list of any files that failed to convert, along with their input and output file locations.

To-do List: 1. Implement a feature to allow the user to select the codec to be used in the conversion process. 2. Add support for more input and output formats. 3. Implement a feature to allow the user to specify additional ffmpeg parameters. 4. Improve error handling and provide more detailed error messages. 5. Add support for multithreading to speed up the conversion process. 6. Improve the user interface by using a more modern and intuitive design. 7. Add support for drag-and-drop functionality to select input and output directories. 8. Allow the user to cancel the conversion process if needed.

Troubleshooting

If the script fails to convert any video files, the error message will be displayed in the console output. Some common reasons for conversion failure include:

    Input file is not a supported video format.
    Output file already exists and is not writable.
    Insufficient disk space or system resources.

License

This project is licensed under the MIT License - see the LICENSE file for details.
