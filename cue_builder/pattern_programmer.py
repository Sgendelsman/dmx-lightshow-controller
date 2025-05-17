import json
import os
import sys

from utils.project_config import *

PATTERN_FILE = "cue_builder/patterns.json"

def load_beat_times(audio_file):
    base = os.path.basename(audio_file)
    manual = os.path.join(BEAT_DIRECTORY, base + ".manualbeats.json")
    auto = os.path.join(BEAT_DIRECTORY, base + ".beats.json")

    if os.path.exists(manual):
        with open(manual, "r") as f:
            return json.load(f)
    elif os.path.exists(auto):
        with open(auto, "r") as f:
            return json.load(f)
    else:
        raise FileNotFoundError("No beat file found.")

def load_patterns():
    if not os.path.exists(PATTERN_FILE):
        raise FileNotFoundError(f"Pattern file not found: {PATTERN_FILE}")
    with open(PATTERN_FILE, "r") as f:
        return json.load(f)

def load_placements(audio_file):
    base = os.path.basename(audio_file)
    placements_path = os.path.join(BEAT_DIRECTORY, base + ".placements.json")
    if not os.path.exists(placements_path):
        raise FileNotFoundError(f"No placements file found: {placements_path}")
    with open(placements_path, "r") as f:
        return {int(k): v for k, v in json.load(f).items()}

def apply_patterns(beat_times, patterns, placements):
    cues = []
    total_beats = len(beat_times)
    cue_map = {}  # beat_index -> cue

    for beat_index, pattern_key in placements.items():
        if pattern_key not in patterns:
            print(f"⚠️ Pattern '{pattern_key}' not found. Skipping beat {beat_index}.")
            continue
        pattern = patterns[pattern_key]
        for offset, cue in enumerate(pattern):
            idx = beat_index + offset - 1  # convert to 0-based
            if idx < total_beats:
                cue_map[idx] = cue

    for i, t in enumerate(beat_times):
        cue = cue_map.get(i, {})  # fallback to blackout
        cues.append((t, cue))

    return cues

def main():
    audio_file = sys.argv[1]

    beat_times = load_beat_times(audio_file)
    patterns = load_patterns()
    placements = load_placements(audio_file)

    cues = apply_patterns(beat_times, patterns, placements)

    out_path = os.path.join(BEAT_DIRECTORY, os.path.basename(audio_file) + ".cue.json")
    with open(out_path, "w") as f:
        json.dump(cues, f, indent=2)

    print(f"✅ Saved cue file to: {out_path}")

if __name__ == "__main__":
    main()