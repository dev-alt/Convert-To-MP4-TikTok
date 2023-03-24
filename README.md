README for Video Converter program:

Overview:
This program is designed to convert video files to the .mp4 format using FFmpeg. The user can select the input and output directories, choose the codec, and select the number of worker threads to use. The program provides a simple UI that shows the progress of the conversion and estimates the time remaining.

Features:

    Codec selection: The user can choose between different codecs (e.g., libx264, mpeg4) to use for the conversion process.
    Thread settings: The user can select the number of worker threads to use for the conversion process.
    Progress indication: The program displays the progress of the conversion process using a progress bar.
    Estimated time remaining: The program estimates the time remaining for the conversion process and displays it to the user.
    Error handling: The program provides error messages for specific cases, such as when the input or output directories do not exist.
    Pause/resume and stop: The user can pause/resume or stop the conversion process at any time.
    Multiple file processing: The program can process multiple video files at once.

Upcoming features:

    UI responsiveness: The UI will be made more responsive by utilizing the QMutex and QMutexLocker classes to prevent race conditions when accessing shared resources from multiple threads.
    Progress bar update frequency: The progress bar will update more frequently during the conversion process by utilizing FFmpeg's -progress option and parsing its output to update the progress bar in real-time.
    File type filter: A filter will be added to the file dialog to only display video files, making it easier for users to select the correct files.
    Save settings: A way to save settings like the chosen codec and number of threads will be implemented, so the user doesn't need to reconfigure these settings each time they run the application.
    Time format: The estimated time remaining will be displayed in a more readable format, such as hours, minutes, and seconds (e.g., "1h 12m 30s").
    Canceling conversions: A way for users to cancel specific conversions instead of stopping the entire batch process will be implemented.
    Status indication: The program will show the status of each video file, such as "Queued", "In progress", "Completed", "Failed", or "Canceled".
    Logging: A logging mechanism will be added to save a detailed log of the conversion process.
    Code organization: The code will be organized by separating the UI, logic, and threading components into different classes or modules.

Requirements:

    Python 3.6+
    PyQt5
    FFmpeg

Installation:

    Install Python 3.6 or higher.
    Install PyQt5 using pip: "pip install PyQt5".
    Install FFmpeg: https://ffmpeg.org/download.html.

Usage:

    Run the program by running the script "video_converter.py".
    Select the codec, input directory, and output directory.
    Click on "Start Process" to begin the conversion process.
    Use the "Pause", "Resume", and "Stop" buttons to control the conversion process.
    The progress of the conversion process is displayed using a progress bar.
    The estimated time remaining for the conversion process is displayed.
    Once the conversion process is complete, the program will display a message indicating how many files were converted.

License:
This program is licensed under the MIT License. See LICENSE file for details.
