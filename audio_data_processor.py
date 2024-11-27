import os
import numpy as np
import librosa
import soundfile as sf
from typing import Dict, List, Tuple, Optional, Set
from pathlib import Path
from tqdm import tqdm
from moviepy.video.io.VideoFileClip import VideoFileClip
import datetime


class AudioDataProcessor:
    def __init__(
        self,
        target_sr: int = 44100,
        target_duration: float = 10.0,
        calibration_samples: int = 300,
        eval_samples: int = 1000,
        gap_duration: float = 2.0,
        previously_processed_files: Set[str] = set(),
    ):  # New parameter for gap between samples
        """
        Initialize the audio data processor with sequential sampling

        Args:
            target_sr: Target sampling rate
            target_duration: Target duration in seconds
            calibration_samples: Number of samples for calibration set
            eval_samples: Number of samples for evaluation set
            gap_duration: Gap between consecutive samples in seconds
        """
        self.target_sr = target_sr
        self.target_duration = target_duration
        self.target_samples = int(target_sr * target_duration)
        self.gap_samples = int(target_sr * gap_duration)
        self.calibration_samples = calibration_samples
        self.eval_samples = eval_samples

        # Track processed files
        self.processed_files = {}

        # Set of already processed audio files. For when we want to skip files that have already been processed from previous runs of this script.
        self.previously_processed_files = previously_processed_files

    def load_audio_file(self, file_path: str) -> Tuple[Optional[np.ndarray], int]:
        """Load audio from various file formats including MP4"""
        try:
            file_ext = Path(file_path).suffix.lower()

            if file_ext == ".mp4":
                with VideoFileClip(file_path) as video:
                    if video.audio is None:
                        print(f"No audio stream in {file_path}")
                        return None, 0
                    # Extract audio at target sample rate
                    audio_array = video.audio.to_soundarray(fps=self.target_sr)
                    # Convert stereo to mono if necessary
                    if len(audio_array.shape) > 1:
                        audio_array = np.mean(audio_array, axis=1)
                    return audio_array, self.target_sr
            else:
                # Use librosa for other audio formats
                return librosa.load(file_path, sr=self.target_sr)

        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            raise e

    def load_and_process_audio(
        self, file_path: str, set_type: str
    ) -> List[Tuple[Optional[np.ndarray], int]]:
        """
        Load and process audio file with sequential sampling

        Args:
            file_path: Path to audio file
            set_type: Either 'calibration' or 'evaluation'

        Returns:
            List of (processed_audio, sr) tuples or empty list if processing fails
        """
        try:
            # Load audio
            audio, sr = self.load_audio_file(file_path)

            if audio is None:
                return []

            # If audio is shorter than target duration, use entire clip
            if len(audio) < self.target_samples:
                # Calculate RMS energy to check if segment has sufficient content
                energy = np.sqrt(np.mean(audio**2))
                if energy >= 0.01:  # Same energy threshold as other segments
                    return [(audio, sr)]
                else:
                    print(f"Skipping {file_path}: insufficient energy in short clip")
                    return []

            # Basic preprocessing
            audio = librosa.util.normalize(audio)
            audio = audio - np.mean(audio)  # Remove DC offset

            segments = []
            current_pos = 0

            while current_pos + self.target_samples <= len(audio):
                # Extract segment
                segment = audio[current_pos : current_pos + self.target_samples]

                # Calculate RMS energy
                energy = np.sqrt(np.mean(segment**2))

                # Only keep segments with sufficient energy
                if energy >= 0.01:  # You can adjust this threshold
                    segments.append((segment, sr))

                # Move to next position (add gap)
                current_pos += self.target_samples + self.gap_samples

            return segments

        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
            raise e

    def process_domain_files(
        self, files: List[str], output_dir: str, domain: str, set_type: str
    ) -> Dict[str, List[str]]:
        """Process files for a specific domain and dataset split"""
        processed_files = []
        processed_count = 0
        target_count = (
            self.calibration_samples if set_type == "calibration" else self.eval_samples
        )

        # Create output directory
        out_path = Path(output_dir) / set_type / domain
        out_path.mkdir(parents=True, exist_ok=True)

        # Process files
        pbar = tqdm(files, desc=f"Processing {domain} files for {set_type}")
        for file_path in pbar:
            # Try to process file
            try:
                # Get filename
                filename = os.path.basename(file_path)

                # Skip if already processed from previous runs of this script
                if filename in self.previously_processed_files:
                    continue

                processed_filenames_for_file = []

                if len(processed_files) >= target_count:
                    break

                if filename in self.processed_files:
                    continue

                segments = self.load_and_process_audio(file_path, set_type)

                # Save processed segments
                for i, (segment, sr) in enumerate(segments):
                    if len(processed_files) >= target_count:
                        break

                    processed_filename = f"{domain}_{len(processed_files):04d}.wav"
                    processed_filenames_for_file.append(processed_filename)

                    output_file = out_path / processed_filename
                    sf.write(output_file, segment, sr)
                    processed_files.append(str(output_file))

                self.processed_files[filename] = {
                    "full_path": str(file_path),
                    "processed_datetime": datetime.datetime.now().isoformat(),
                    "processed_filenames": processed_filenames_for_file,
                }
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")

            processed_count += 1
            pbar.set_postfix({"processed": processed_count})

        return {f"{domain}_{set_type}": processed_files}

    def create_dataset_splits(
        self,
        speech_files: List[str],
        music_files: List[str],
        env_files: List[str],
        output_dir: str,
    ) -> Dict[str, List[str]]:
        """Create calibration and evaluation dataset splits"""
        dataset_splits = {}

        # Reset stats for each new dataset creation
        self.segment_stats = []
        self.processed_segments = set()

        # Process calibration sets first
        for domain, files in [
            ("speech", speech_files),
            ("music", music_files),
            ("environmental", env_files),
        ]:
            split_files = self.process_domain_files(
                files, output_dir, domain, "calibration"
            )
            dataset_splits.update(split_files)

        # Reset stats before evaluation set
        self.segment_stats = []

        # Process evaluation sets
        for domain, files in [
            ("speech", speech_files),
            ("music", music_files),
            ("environmental", env_files),
        ]:
            split_files = self.process_domain_files(
                files, output_dir, domain, "evaluation"
            )
            dataset_splits.update(split_files)

        return dataset_splits
