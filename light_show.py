import time
import json
import os
import sounddevice as sd
import soundfile as sf
from threading import Thread
import pygame
import sys

from utils.project_config import *
import utils.artnet_utils as artnet_utils

def load_beat_times(song_path):
    base = os.path.basename(song_path)
    manual_file = os.path.join(BEAT_DIRECTORY, base + ".manualbeats.json")
    auto_file = os.path.join(BEAT_DIRECTORY, base + ".beats.json")

    if os.path.exists(manual_file):
        print(f"📥 Using manual beats for '{base}'")
        with open(manual_file, "r") as f:
            return json.load(f)
    elif os.path.exists(auto_file):
        print(f"📥 Using auto beats for '{base}'")
        with open(auto_file, "r") as f:
            return json.load(f)
    else:
        raise FileNotFoundError(f"No beat file found for: {base}")

def load_patterns():
    auto_file = os.path.join(BUILDER_DIRECTORY, "patterns.json")
    with open(auto_file, "r") as f:
        return json.load(f)

def load_placements(song_path, patterns):
    placements = []
    base = os.path.basename(song_path)
    manual_file = os.path.join(BEAT_DIRECTORY, base + ".placements.txt")
    with open(manual_file, "r") as f:
        last_index = 0
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if ":" in line:
                index_str, pattern_key = line.split(":", 1)
                last_index = int(index_str.strip()) - 1   # convert to 0-based index
            else:
                pattern_key = line.strip('"')
            
            pattern_key = pattern_key.strip().strip('"')

            placements.append((last_index, pattern_key))
            
            for pattern in patterns.get(pattern_key, []):
                if isinstance(pattern, dict) and 'fade' in pattern:
                    last_index = last_index + pattern['fade']['beats']
                else:
                    last_index = last_index + 1

    return placements

def resolve_cues(beat_times, placements, patterns):
    cues = []

    for index, pattern_key in placements:
        if pattern_key not in patterns:
            print(f"Warning: pattern '{pattern_key}' not found.")
            continue

        pattern = patterns[pattern_key]
        for step_offset, step in enumerate(pattern):
            step_index = index + step_offset
            if step_index >= len(beat_times):
                continue

            start_time = beat_times[step_index]
            end_index = min(step_index + 1, len(beat_times) - 1)
            end_time = beat_times[end_index]  # default for static

            if isinstance(step, dict) and "fade" in step:
                fade = step["fade"]
                beats = fade.get("beats", 1)
                end_index = min(step_index + beats - 1, len(beat_times) - 1)
                end_time = beat_times[end_index]

                from_vals = fade.get("from", {})
                to_vals = fade.get("to", {})
                cues.append((start_time, end_time, from_vals, to_vals, pattern_key))
            elif isinstance(step, dict):
                cues.append((start_time, end_time, step, step, pattern_key))
            else:
                print(f"Invalid pattern step: {step}")
    return cues

def play_audio(song_path):
    pygame.mixer.init()
    pygame.mixer.music.load(song_path)
    pygame.mixer.music.play()

def run_light_show(song_path):
    beat_times = load_beat_times(song_path)
    patterns = load_patterns()
    placements = load_placements(song_path, patterns)
    cues = resolve_cues(beat_times, placements, patterns)
    play_audio(song_path)

    start_time = time.time()
    last_frame = {}

    try:
        last_played_cue = None
        while True:
            now = time.time() - start_time
            frame = {}

            for cue in cues:
                (start, end, from_vals, to_vals, pattern_key) = cue
                # These are in order, so if we find an element that has a greater start than current time, skip the rest of the cues.
                if start > now:
                    break
                elif start <= now <= end:
                    t = 0 if start == end else (now - start) / (end - start)
                    for ch in set(from_vals.keys()) | set(to_vals.keys()):
                        from_val = from_vals.get(ch, 0)
                        to_val = to_vals.get(ch, 0)
                        frame[ch] = int(from_val + (to_val - from_val) * t)

                    if last_played_cue != cue:
                        last_played_cue = cue
                        print(f"[{start:.3f}s -> {end:.3f}s] DMX -> {pattern_key}")
                    break

            if frame != last_frame:
                artnet_utils.send_dmx(frame)
                last_frame = frame

            if not pygame.mixer.music.get_busy():
                # Song ended – fade to black
                artnet_utils.send_dmx({ch: 0 for ch in last_frame})
                break

            time.sleep(1 / PACKETS_PER_SECOND)

    except KeyboardInterrupt:
        artnet_utils.send_dmx({ch: 0 for ch in last_frame})
        print("Light show interrupted. All lights off.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python light_show.py path/to/audio/file")
    else:
        run_light_show(sys.argv[1])