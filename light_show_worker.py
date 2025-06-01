import sys
import time
import json
import os
import soundfile as sf
import subprocess
import yaml

from utils.project_config import *
import utils.artnet_utils as artnet_utils

def load_beat_times(song_path):
    base = os.path.basename(song_path)
    manual_file = os.path.join(BEAT_DIRECTORY, base + '.manualbeats.json')
    auto_file = os.path.join(BEAT_DIRECTORY, base + '.beats.json')
    if os.path.exists(manual_file):
        with open(manual_file, 'r') as f:
            return json.load(f)
    elif os.path.exists(auto_file):
        with open(auto_file, 'r') as f:
            return json.load(f)
    else:
        raise FileNotFoundError(f'No beat file found for: {base}')

def load_patterns():
    def has_nested_patterns(patterns):
        return any('pattern' in val for pattern in patterns.values() for val in pattern)
    def expand_patterns(patterns):
        for key in list(patterns.keys()):
            expanded = []
            for val in patterns[key]:
                if 'pattern' in val:
                    nested = val['pattern']
                    if nested in patterns:
                        expanded.extend(patterns[nested])
                else:
                    expanded.append(val)
            patterns[key] = expanded
        return patterns

    with open(os.path.join(BEAT_DIRECTORY, 'helpers/patterns.yaml'), 'r') as f:
        patterns = yaml.safe_load(f)
    while has_nested_patterns(patterns):
        patterns = expand_patterns(patterns)
    return patterns

def load_channel_configs():
    with open(os.path.join(BEAT_DIRECTORY, 'helpers/channel_configs.json'), 'r') as f:
        return json.load(f)

def load_placements(song_path, patterns):
    base = os.path.basename(song_path)
    placements = []            
    with open(os.path.join(BEAT_DIRECTORY, base + '.placements.md'), 'r') as f:
        last_index = 0
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if ':' in line:
                idx, pattern_key = line.split(':', 1)
                last_index = int(idx.strip()) - 1
            else:
                pattern_key = line.strip('"')
            pattern_key = pattern_key.strip().strip('"')
            placements.append((last_index, pattern_key))
            if ' ' in pattern_key:
                pattern_key = pattern_key.split(' ')[0]
            for step in patterns.get(pattern_key, []):
                last_index += step.get('beats', 1)
    return placements

def beat_index_to_time(beat_times, i):
    if i >= len(beat_times):
        return i
    lower = int(i)
    upper = min(lower + 1, len(beat_times) - 1)
    return beat_times[lower] + (beat_times[upper] - beat_times[lower]) * (i - lower)

def resolve_cues(beat_times, placements, patterns, channel_configs):
    cues = []
    for index, key in placements:
        key = key.strip()
        args = []
        # If there are args in the placement key, pass them to the pattern
        if ' ' in key:
            args = key.split(' ')
            key = args[0]
            args = args[1:]

        pattern = patterns.get(key, [])

        offset = 0.0
        for step in pattern:
            duration = step.get('beats', 1.0)
            start_i = index + offset
            end_i = start_i + duration
            start = min(len(beat_times), beat_index_to_time(beat_times, start_i))
            end = min(len(beat_times), beat_index_to_time(beat_times, end_i))
            if start == len(beat_times):
                break
            if 'fade' in step:
                f = step['fade']
                from_val, to_val = f['from'], f['to']
                for i in range(len(args)):
                    color_placeholder = f'color{i+1}'
                    if color_placeholder in from_val:
                        from_val = from_val.replace(color_placeholder, args[i])
                    if color_placeholder in to_val:
                        to_val = to_val.replace(color_placeholder, args[i])
                from_vals = channel_configs.get(from_val, {})
                to_vals = channel_configs.get(to_val, {})
                cues.append((start, end, from_vals, to_vals, key))
            elif 'value' in step:
                val = step['value']
                for i in range(len(args)):
                    color_placeholder = f'color{i+1}'
                    if color_placeholder in val:
                        val = val.replace(color_placeholder, args[i])
                vals = channel_configs.get(val, {})
                cues.append((start, end, vals, vals, key))
            offset += duration
    return cues

def play_audio(song_path, start_time=0.0, begin_audio_time=0.0):
    return subprocess.Popen([sys.executable, 'audio_worker.py', song_path, str(start_time), str(begin_audio_time)])

def main(song_path, song_duration, start_delay, start_offset, seek, start_time, beat_delay):
    beat_times = load_beat_times(song_path)
    beat_times = [bt + beat_delay - seek for bt in beat_times]
    channel_configs = load_channel_configs()
    patterns = load_patterns()
    placements = load_placements(song_path, patterns)
    cues = resolve_cues(beat_times, placements, patterns, channel_configs)    

    begin_audio_time = start_time + start_delay - start_offset

    try:
        audio_proc = play_audio(song_path, seek, begin_audio_time)
        # Play audio once it's ready.
        while time.time() < begin_audio_time:
            time.sleep(0.001)

        log_str = f'🎵 Starting {path}'
        if start_offset > 0.0:
            log_str = log_str + f' {start_offset} seconds early'
        if seek > 0.0:
            seek_min = int(seek / 60)
            seek_sec = int(seek % 60)
            log_str = log_str + f' at {seek_min}:{seek_sec:02}'
        
        print(f'{log_str}...')
    
        start_time = time.time()
        last_frame = {}
        last_cue = None
        now = 0
        while audio_proc.poll() is None:
            now = time.time() - start_time
            frame = {}
            for cue in cues:
                start, end, from_vals, to_vals, key = cue
                if start > now:
                    break
                elif start <= now <= end:
                    # Trim the end of any cues to the end of the song so fades work as expected
                    # end = min(end, song_duration - seek)
                    t = (now - start) / (end - start) if start != end else 0
                    for ch in set(from_vals) | set(to_vals):
                        frame[ch] = min(255, int(from_vals.get(ch, 0) + (to_vals.get(ch, 0) - from_vals.get(ch, 0)) * t))
                    if last_cue != cue:
                        print(f'[{(now + seek):.3f}s/{song_duration:.3f}s] DMX -> {key}')
                        last_cue = cue
                    break
            if frame != last_frame:
                artnet_utils.send_dmx(frame)
                last_frame = frame
            time.sleep(1 / PACKETS_PER_SECOND)
        audio_proc.wait()
    except KeyboardInterrupt:
        audio_proc.terminate()
        audio_proc.wait()

if __name__ == '__main__':
    try:
        path = sys.argv[1]
        song_duration = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
        start_offset = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
        seek = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
        start_delay = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
        start_time = float(sys.argv[6]) if len(sys.argv) > 6 else 0.0
        beat_delay = float(sys.argv[7]) if len(sys.argv) > 7 else 0.0

        main(path, song_duration, start_delay, start_offset, seek, start_time, beat_delay)
    except KeyboardInterrupt:
        pass