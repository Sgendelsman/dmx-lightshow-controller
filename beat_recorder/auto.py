import librosa
import os
import json
import sys

from utils.project_config import *

os.makedirs(BEAT_DIRECTORY, exist_ok=True)

def save_beat_times(song_path):
    y, sr = librosa.load(song_path)
    _, beats = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beats, sr=sr).tolist()

    base = os.path.basename(song_path)
    beat_file = os.path.join(BEAT_DIRECTORY, base + ".beats.json")
    with open(beat_file, "w") as f:
        json.dump(beat_times, f)
    print(f"✅ Saved {len(beat_times)} beats for '{base}' to {beat_file}")

if __name__ == "__main__":
    song = sys.argv[1]
    if os.path.exists(song):
        save_beat_times(song)
    else:
        print(f"⚠️ File not found: {song}")