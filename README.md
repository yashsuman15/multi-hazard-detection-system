# Multi Hazard Detection System

## Overview

The Multi Hazard Detection System is an advanced computer vision application that utilizes deep learning models to detect various hazards and objects in video streams. The system is built using Python and incorporates multiple YOLO (You Only Look Once) models for different detection tasks.

## Features

- **Unified Detection System**: Incorporates multiple detection models in a single application.
- **GUI Interface**: User-friendly graphical interface for easy operation and visualization.
- **Multiple Detection Modes**:
  - Crowd Detection
  - Fire Detection
  - Smoking Detection
  - Vehicle Detection
  - Weapon Detection
- **Real-time Processing**: Capable of processing video streams in real-time.
- **System Monitoring**: Displays RAM usage, GPU usage, and CPU temperature.
- **Video Controls**: Play, pause, seek, and restart video playback.
- **Screenshot Capture**: Ability to capture and save screenshots during video playback.

## Requirements

- Python 3.x
- OpenCV (cv2)
- CustomTkinter
- Ultralytics YOLO
- cvzone
- Pillow (PIL)
- psutil
- GPUtil (optional, for GPU monitoring)
- wmi (optional, for temperature monitoring on Windows)

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/multi-hazard-detection-system.git
   cd multi-hazard-detection-system
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Download the YOLO model files and place them in the `models/` directory:
   - crowd-density-model.pt
   - fire-detection-model.pt
   - smoking-detection-model.pt
   - vehicle-detection-model.pt
   - weapon-detection-model.pt

## Usage

1. Run the main application:
   ```
   python protoGUI-5.py
   ```

2. Use the GUI to:
   - Select a video file
   - Choose a detection mode
   - Control video playback
   - Start/stop detection
   - Capture screenshots

## File Structure

- `protoGUI-5.py`: Main GUI application
- `prototype1.py`: Core detection system implementation
- `models/`: Directory containing YOLO model files
- `screenshots/`: Directory where screenshots are saved

## Detection Modes

1. **Crowd Detection**: Counts and marks individuals in the frame.
2. **Fire Detection**: Identifies and outlines areas with fire or smoke.
3. **Smoking Detection**: Detects individuals smoking.
4. **Vehicle Detection**: Identifies various types of vehicles.
5. **Weapon Detection**: Detects the presence of firearms.

## Notes

- The system's performance may vary depending on the hardware specifications.
- Ensure proper lighting and video quality for optimal detection results.
- The application is currently in development, and some features may be experimental.

## Credits

Created by: Yash Raj Suman

## License

[Include your license information here]

