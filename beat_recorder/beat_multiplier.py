import sys
import os
import json

from utils.project_config import *

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

# --- MAIN ---
if __name__ == "__main__":
    
    audio_file = sys.argv[1]
    multiplier = int(sys.argv[2])

    if not os.path.exists(audio_file):
        print(f"❌ File not found: {audio_file}")
        exit(1)

    beats = load_beat_times(audio_file)

    if beats and len(beats) >= 1:    
        new_beats = []
        prev_beat = beats[0]
        new_beats.append(prev_beat)
        for i in range(1, len(beats)):
            beat = beats[i]
            diff = beat - prev_beat
            
            new_beats_in_between = [prev_beat + (diff * j / multiplier) for j in range(1, multiplier)]
 
            new_beats.extend(new_beats_in_between)
            new_beats.append(beat)

            prev_beat = beat

        outfile = os.path.join(BEAT_DIRECTORY, os.path.basename(audio_file) + ".multipliedbeats.json")
        with open(outfile, "w") as f:
            json.dump(new_beats, f)
        print(f"\n✅ Turned {len(beats)} beats into {len(new_beats)} beats and wrote them to '{outfile}'")