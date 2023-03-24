Convert Video Files to MP4 Format

This Python script can be used to convert all video files in a specified directory to the MP4 format. The script uses the ffmpeg library to perform the conversion and supports the following input formats: .avi, .mkv, .wmv, .flv, and .webm. The output files are saved to a specified directory with the .mp4 extension.
Prerequisites

This script requires the following libraries:

    os
    sys
    subprocess
    threading
    queue
    tqdm
    tkinter

In addition, you must have ffmpeg installed on your system and the ffmpeg executable must be located at C:\\Users\\andre\\Desktop\\Libraries\\ffmpeg.exe.
Usage

    Run the script in a Python environment (e.g., IDLE, VS Code, or the command line).

    When prompted, select the input directory containing the video files you want to convert.

    When prompted, select the output directory where the converted files will be saved.

    The script will convert each video file in the input directory to the MP4 format and save the output files to the specified output directory. A progress bar will be displayed to show the status of the conversion process.

    If the output file for a particular video already exists, the script will skip that file and move on to the next one.

    When the script has finished, it will display a list of any files that failed to convert.

Troubleshooting

If the script fails to convert any video files, the error message will be displayed in the console output. Some common reasons for conversion failure include:

    Input file is not a supported video format.
    Output file already exists and is not writable.
    Insufficient disk space or system resources.

License

This project is licensed under the MIT License - see the LICENSE file for details.
