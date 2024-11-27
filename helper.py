import os
import json
from collections import defaultdict

# Load sources from JSON file
with open("data_sources.json", "r") as f:
    sources = json.load(f)

set_counts = defaultdict(int)

for file, info in sources["processed_files"].items():
    if len(info["processed_filenames"]) != 0:
        if "music" in info["full_path"]:
            set_counts["music"] += 1
        elif "environmental" in info["full_path"]:
            set_counts["environmental"] += 1
        else:
            set_counts["speech"] += 1

print(f"Number of files in each set: {set_counts}")


path = r"C:\Users\hranw\Dropbox (MIT)\6.5940 Audio Codecs Project\datasets\raw\speech\VCTK-Corpus-0.92\wav48_silence_trimmed"

# Get all directories in the path
directories = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

# print(f"\nNumber of directories in VCTK corpus: {len(directories)}")

# print("\nFull paths in VCTK corpus:")
# for directory in sorted(directories):
#     full_path = f'"{path}/{directory}"'
#     print(full_path.replace("\\", "/") + ",")
