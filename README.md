Video Converter

This program is designed to convert video files to the .mp4 format using FFmpeg. The user can select the input and output directories, choose the codec, and select the number of worker threads to use. The program provides a simple UI that shows the progress of the conversion and estimates the time remaining.

Installation
Requirements

    Python 3
    PyQt5
    FFmpeg

Instructions

    Install Python 3.6 or higher.
    Install PyQt5 using pip: "pip install PyQt5".
    Install FFmpeg: https://ffmpeg.org/download.html.
    Run main.py: python main.py

Usage

    Select input and output directories
    Choose codec and number of threads
    Click "Start Process"
    View progress and estimated time remaining
    Load/save settings to JSON file
    Logs will be written to conversion.log

Features

    Codec selection between libx264, mpeg4, etc.
    Number of threads can be set from 1 to 8
    Progress bar indicates conversion progress
    Time remaining is estimated and displayed
    Error messages for invalid input/output directories
    Pause, resume and stop conversion
    Multiple files can be converted at once

License

This program is licensed under the MIT License. See LICENSE file for details.


Files

    main.py - Entry point
    Logger.py - Logger configuration
    MainWindow.py - GUI definitions
    ConvertThread.py - Conversion logic
    settings.py - Settings class
    utils.py - Utility functions
