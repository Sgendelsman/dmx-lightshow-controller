import time
import json
import os
import soundfile as sf
import pygame
import sys
from threading import Thread, Event

from utils.project_config import *
import utils.artnet_utils as artnet_utils

def load_beat_times(song_path):
    base = os.path.basename(song_path)
    manual_file = os.path.join(BEAT_DIRECTORY, base + ".manualbeats.json")
    auto_file = os.path.join(BEAT_DIRECTORY, base + ".beats.json")

    if os.path.exists(manual_file):
        print(f"📅 Using manual beats for '{base}'")
        with open(manual_file, "r") as f:
            return json.load(f)
    elif os.path.exists(auto_file):
        print(f"📅 Using auto beats for '{base}'")
        with open(auto_file, "r") as f:
            return json.load(f)
    else:
        raise FileNotFoundError(f"No beat file found for: {base}")

def load_patterns():
    def has_nested_patterns(patterns):
        for pattern_key in patterns:
            pattern_val_arr = patterns[pattern_key]
            for val in pattern_val_arr:
                if 'pattern' in val:
                    return True
        return False

    def expand_patterns(patterns):
        for pattern_key in patterns:
            pattern_val_arr = patterns[pattern_key]
            expanded_pattern_val_arr = []
            for val in pattern_val_arr:
                # If this is a nested pattern, look through patterns to see if it's in there already, 
                # and expand it into the current pattern
                if 'pattern' in val:
                    nested_pattern_key = val['pattern']
                    if nested_pattern_key in patterns:
                        expanded_pattern_val_arr = expanded_pattern_val_arr + patterns[nested_pattern_key]
                else:
                    expanded_pattern_val_arr.append(val)
            patterns[pattern_key] = expanded_pattern_val_arr
        return patterns
    
    patterns = []
    with open(os.path.join(BEAT_DIRECTORY, "helpers/patterns.json"), "r") as f:
        patterns = json.load(f)

    while has_nested_patterns(patterns):
        patterns = expand_patterns(patterns)

    return patterns

def load_channel_configs():
    with open(os.path.join(BEAT_DIRECTORY, "helpers/channel_configs.json"), "r") as f:
        return json.load(f)

def load_placements(song_path, patterns):
    placements = []
    base = os.path.basename(song_path)
    manual_file = os.path.join(BEAT_DIRECTORY, base + ".placements.md")
    with open(manual_file, "r") as f:
        last_index = 0
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                index_str, pattern_key = line.split(":", 1)
                last_index = int(index_str.strip()) - 1
            else:
                pattern_key = line.strip('"')
            pattern_key = pattern_key.strip().strip('"')
            placements.append((last_index, pattern_key))
            for pattern in patterns.get(pattern_key, []):
                last_index += pattern.get('beats', 1)
    return placements

def beat_index_to_time(beat_times, fractional_index):
    if fractional_index >= len(beat_times):
        return fractional_index
    lower = int(fractional_index)
    upper = min(lower + 1, len(beat_times) - 1)
    if lower == upper:
        return beat_times[lower]
    ratio = fractional_index - lower
    return beat_times[lower] + (beat_times[upper] - beat_times[lower]) * ratio

def resolve_cues(beat_times, placements, patterns, channel_configs):
    cues = []
    for index, pattern_key in placements:
        if pattern_key not in patterns:
            print(f"Warning: pattern '{pattern_key}' not found.")
            continue
        pattern = patterns[pattern_key]
        current_beat_offset = 0.0
        for step in pattern:
            duration_beats = step.get("beats", 1.0)
            start_index = index + current_beat_offset
            end_index = index + current_beat_offset + duration_beats
            start_time = min(len(beat_times), beat_index_to_time(beat_times, start_index))
            end_time = min(len(beat_times), beat_index_to_time(beat_times, end_index))
            if start_time == len(beat_times):
                break
            if "fade" in step:
                fade = step["fade"]
                from_vals = channel_configs.get(fade['from'], {})
                to_vals = channel_configs.get(fade['to'], {})
                cues.append((start_time, end_time, from_vals, to_vals, pattern_key))
            elif "value" in step:
                values = channel_configs.get(step["value"], {})
                cues.append((start_time, end_time, values, values, pattern_key))
            else:
                print(f"Invalid pattern step: {step}")
            current_beat_offset += duration_beats
    return cues

def play_audio(song_path):
    pygame.mixer.init()
    sound = pygame.mixer.Sound(song_path)
    sound.play()
    return sound

def get_song_duration(song_path):
    return sf.info(song_path).duration

def run_light_show(song_path, start_offset=0.0):
    def light_show_thread():
        beat_times = load_beat_times(song_path)
        beat_times = [bt + BEAT_DELAY_ADJUSTMENT for bt in beat_times]
        channel_configs = load_channel_configs()
        patterns = load_patterns()
        placements = load_placements(song_path, patterns)
        cues = resolve_cues(beat_times, placements, patterns, channel_configs)

        if start_offset > 0:
            time.sleep(start_offset)

        sound = play_audio(song_path)
        start_time = time.time()
        last_frame = {}

        last_played_cue = None
        while True:
            now = time.time() - start_time
            frame = {}
            for cue in cues:
                (start, end, from_vals, to_vals, pattern_key) = cue
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
            if not sound.get_num_channels():
                break
            time.sleep(1 / PACKETS_PER_SECOND)

        artnet_utils.send_dmx({ch: 0 for ch in last_frame})

    thread = Thread(target=light_show_thread)
    thread.start()
    return thread

def run_playlist(song_paths):
    previous_thread = None

    for i, song_path in enumerate(song_paths):
        if i > 0:
            prev_song_duration = get_song_duration(song_paths[i - 1]['song'])
            sleep_time = max(0, prev_song_duration - song_path['start_offset'])
            time.sleep(sleep_time)
            print(f"Starting {song_path['song']} {song_path['start_offset']} seconds early.")

        thread = run_light_show(song_path['song'])
        previous_thread = thread

    if previous_thread:
        previous_thread.join()

if __name__ == "__main__":
    songs = [
        {'song': f'{MUSIC_DIRECTORY}/unbroken.mp3', 'start_offset': 0},
    ]

    run_playlist(songs)