# Audio Codecs Project Data Processing

The data processing pipeline for preparing audio datasets for codec evaluation and calibration.

## Overview

This codebase provides the script to process audio files from different domains (speech, music, environmental) into standardized segments for the 6.5940 Audio Codecs Project. It handles resampling, segmentation, and energy-based filtering of audio files.

## Features

- Automatic audio resampling to 44.1 kHz
- Segmentation with configurable lengths
- Energy-based filtering to remove low-quality segments
- Organized output structure for calibration and evaluation datasets
- Comprehensive tracking of processed files

## Installation

1. Clone the repository:

```bash
git clone https://github.com/haoranwen0/6.5940-final-project-audio-codec-data-processing.git
cd 6.5940-final-project-audio-codec-data-processing
```

2. (Optional) Create and activate a python virtual environment:

```bash
python -m venv audio-codecs
source audio-codecs/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the processing script:

```bash
python data_processing.py
```

## Project Structure

```
.
├── data_processing.py       # Main processing script
├── audio_data_processor.py  # Audio data processor class
├── data_sources.json        # Configuration file for data sources
├── helper.py                # Helper script for data analysis
├── requirements.txt         # Project dependencies
└── processed/               # NOTE: This directory is not included in the repo. Created by the processing script.
    ├── calibration/         # Calibration dataset
    │   ├── speech/
    │   │   ├── speech_0000.wav
    │   │   └── ...
    │   ├── music/
    │   │   ├── music_0000.wav
    │   │   └── ...
    │   └── environmental/
    │       ├── environmental_0000.wav
    │       └── ...
    ├── evaluation/          # Evaluation dataset
    │   ├── speech/
    │   │   ├── speech_0000.wav
    │   │   └── ...
    │   ├── music/
    │   │   ├── music_0000.wav
    │   │   └── ...
    │   └── environmental/
    │       ├── environmental_0000.wav
    │       └── ...
    └── dataset_splits.json  # Dataset split configuration
```

## Configuration

### data_sources.json

```json
{
  "data_directories": {
    "speech": ["/path/to/speech/data"],
    "music": ["/path/to/music/data"],
    "environmental": ["/path/to/env/data"]
  },
  "processed_files": {
    "filename": {
      "full_path": "path/to/file",
      "processed_filenames": ["segment1.wav", "segment2.wav"],
      "processed_datetime": "2024-03-21T10:00:00"
    }
  }
}
```

### Dataset Splits

The `dataset_splits.json` file contains the paths to processed segments for each category:

- `*_calibration`: Paths to calibration segments
- `*_evaluation`: Paths to evaluation segments

## Processing Pipeline

1. **Resampling**: All audio files are resampled to 44.1 kHz
2. **Segmentation**: Files are split into 10-second segments with 2-second gaps
3. **Filtering**: Low-energy segments are removed
4. **Organization**: Segments are sorted into calibration and evaluation sets
