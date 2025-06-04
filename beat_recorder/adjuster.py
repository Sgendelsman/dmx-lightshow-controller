import sys
import os
import json

def load_beat_times(path):
    with open(path, "r") as f:
        return json.load(f)

if len(sys.argv) < 4:
    print("Usage: python -m beat_recorder.adjuster path/to/beat_file.json adjustment_float_in_seconds cutoff_max cutoff_min")
    exit

path = sys.argv[1]
adjustment = float(sys.argv[2])
cutoff_max = float(sys.argv[3])
cutoff_min = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0

beat_times = load_beat_times(path)
beat_times = [beat_time + adjustment if cutoff_min <= beat_time <= cutoff_max else beat_time for beat_time in beat_times]

with open(path, "w") as f:
    json.dump(beat_times, f)

print(f"\n✅ Shifted beats in {path} between [{cutoff_min:.3f}->{cutoff_max:.3f}] by {adjustment:.3f} seconds!")