import json
import os
import sys
import re

from utils.project_config import *

PATTERN_FILE = "cue_builder/patterns.json"

def expand_fade_step_by_beats(fade):
    start = fade.get("from", {})
    end = fade.get("to", {})
    steps = fade.get("beats", 1)
    result = []

    all_channels = set(start.keys()) | set(end.keys())
    for i in range(steps):
        t = i / max(steps - 1, 1)
        step = {}
        for ch in all_channels:
            start_val = start.get(ch, 0)
            end_val = end.get(ch, 0)
            val = int(start_val + (end_val - start_val) * t)
            step[ch] = val
        result.append(step)

    return result

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

def parse_placement_lines(lines, patterns):
    placements = {}  # beat index -> pattern key
    current_index = 1

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue  # skip empty lines or comments

        match = re.match(r'(\d+):\s*"([^"]+)"', line)
        if match:
            index = int(match.group(1))
            current_index = index

            pattern_key = match.group(2)
            placements[index] = pattern_key

            for pattern in patterns.get(pattern_key, []):
                if isinstance(pattern, dict) and 'fade' in pattern:
                    current_index = current_index + pattern['fade']['beats']
                else:
                    current_index = current_index + 1
        else:
            match = re.match(r'"([^"]+)"', line)
            if match:
                pattern_key = match.group(1)
                placements[current_index] = pattern_key
                for pattern in patterns.get(pattern_key, []):
                    if isinstance(pattern, dict) and 'fade' in pattern:
                        current_index = current_index + pattern['fade']['beats']
                    else:
                        current_index = current_index + 1
            else:
                print(f"⚠️ Skipping invalid line: {line}")

    return placements

def load_placements(audio_file, patterns):
    base = os.path.basename(audio_file)
    placements_path = os.path.join(BEAT_DIRECTORY, base + ".placements.txt")
    if not os.path.exists(placements_path):
        raise FileNotFoundError(f"No placements file found: {placements_path}")
    with open(placements_path, "r") as f:
        lines = f.readlines()
    return parse_placement_lines(lines, patterns)

def apply_patterns(beat_times, patterns, placements):
    cues = []
    total_beats = len(beat_times)
    cue_map = {}  # beat_index -> cue

    idx = 0

    for beat_index, pattern_key in placements.items():
        if pattern_key not in patterns:
            print(f"⚠️ Pattern '{pattern_key}' not found. Skipping beat {beat_index}.")
            continue

        raw_steps = patterns[pattern_key]
        expanded_steps = []

        for step in raw_steps:
            if isinstance(step, dict) and "fade" in step:
                fade = step["fade"]
                expanded_steps.extend(expand_fade_step_by_beats(fade))
            else:
                expanded_steps.append(step)

        for offset, cue in enumerate(expanded_steps):
            idx = beat_index + offset - 1  # 0-based index
            if idx < len(beat_times):
                cue_map[idx] = cue

    for i, t in enumerate(beat_times):
        cue = cue_map.get(i, {})  # fallback to blackout
        cues.append((i + 1, t, cue))

    return cues

def main():
    audio_file = sys.argv[1]

    beat_times = load_beat_times(audio_file)
    patterns = load_patterns()
    placements = load_placements(audio_file, patterns)

    cues = apply_patterns(beat_times, patterns, placements)

    out_path = os.path.join(BEAT_DIRECTORY, os.path.basename(audio_file) + ".cue.json")
    with open(out_path, "w") as f:
        json.dump(cues, f, indent=2)

    print(f"✅ Saved cue file to: {out_path}")

if __name__ == "__main__":
    main()