import json
import os
import sys

from utils.project_config import *

def load_beat_times(audio_file):
    base = os.path.basename(audio_file)
    manual_file = os.path.join(BEAT_DIRECTORY, base + ".manualbeats.json")
    auto_file = os.path.join(BEAT_DIRECTORY, base + ".beats.json")

    if os.path.exists(manual_file):
        with open(manual_file, "r") as f:
            return json.load(f), manual_file
    elif os.path.exists(auto_file):
        with open(auto_file, "r") as f:
            return json.load(f), auto_file
    else:
        raise FileNotFoundError(f"No beat file found for: {base}")

def program_cue_template(audio_file):
    beat_times, _ = load_beat_times(audio_file)
    template = {
        "audio_file": audio_file,
        "cues": [
            {"time": t, "channels": {}} for t in beat_times
        ]
    }

    cue_py_path = os.path.join(BEAT_DIRECTORY, os.path.basename(audio_file) + ".cue_template.py")
    with open(cue_py_path, "w") as f:
        f.write("# Fill in the DMX values for each beat in the 'cues' list\n")
        f.write("cue_data = ")
        f.write(json.dumps(template, indent=2))

    print(f"\n📝 Edit this file to define your cues:\n{cue_py_path}")
    print("Then run `compile_cue_template.py` to convert it into a .cue.json file.")

if __name__ == "__main__":
    filename = sys.argv[1]
    program_cue_template(filename)