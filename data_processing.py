import os
from pathlib import Path
from typing import List
import json
from audio_data_processor import AudioDataProcessor

# Load sources from JSON file
with open("data_sources.json", "r") as f:
    sources = json.load(f)

ROOT_DIR = "C:/Users/hranw/Dropbox (MIT)/6.5940 Audio Codecs Project/datasets"


def collect_files(directory: str, extensions: List[str]) -> List[str]:
    """
    Recursively collect audio files from directory
    """
    files = []
    for ext in extensions:
        files.extend([str(p) for p in Path(directory).rglob(f"*.{ext}")])
    return files


def main():
    # Configuration
    AUDIO_EXTENSIONS = ["wav", "mp3", "flac", "mp4"]
    # OUTPUT_DIR = "datasets/processed"
    OUTPUT_DIR = f"{ROOT_DIR}/processed"

    # Data directories
    SPEECH_DIRS = sources["data_directories"].get("speech", [])
    MUSIC_DIRS = sources["data_directories"].get("music", [])
    ENV_DIRS = sources["data_directories"].get("environmental", [])

    # Collect files
    speech_files = []
    for directory in SPEECH_DIRS:
        if os.path.exists(directory):
            # Only add files that haven't been processed yet
            new_files = collect_files(directory, AUDIO_EXTENSIONS)
            speech_files.extend(
                [f for f in new_files if f not in sources["processed_files"]]
            )

    music_files = []
    for directory in MUSIC_DIRS:
        if os.path.exists(directory):
            # Only add files that haven't been processed yet
            new_files = collect_files(directory, AUDIO_EXTENSIONS)
            music_files.extend(
                [f for f in new_files if f not in sources["processed_files"]]
            )

    env_files = []
    for directory in ENV_DIRS:
        if os.path.exists(directory):
            # Only add files that haven't been processed yet
            new_files = collect_files(directory, AUDIO_EXTENSIONS)
            env_files.extend(
                [f for f in new_files if f not in sources["processed_files"]]
            )

    previously_processed_files = set(sources["processed_files"].keys())

    # Initialize processor with sequential sampling
    processor = AudioDataProcessor(
        target_sr=44100,
        target_duration=10.0,
        calibration_samples=300,
        eval_samples=1000,
        gap_duration=2.0,  # 2 second gap between consecutive samples
        previously_processed_files=previously_processed_files,
    )

    # Create dataset splits
    dataset_splits = processor.create_dataset_splits(
        speech_files=speech_files,
        music_files=music_files,
        env_files=env_files,
        output_dir=OUTPUT_DIR,
    )

    # Save dataset split information
    with open(os.path.join(OUTPUT_DIR, "dataset_splits.json"), "w") as f:
        json.dump(dataset_splits, f, indent=2)

    # Print statistics
    print("\nDataset Statistics:")
    for split_name, files in dataset_splits.items():
        print(f"{split_name}: {len(files)} files")

    # Update processed files
    for filename, file_info in processor.processed_files.items():
        sources["processed_files"][filename] = file_info

    with open("data_sources.json", "w") as f:
        json.dump(sources, f, indent=2)


if __name__ == "__main__":
    main()
