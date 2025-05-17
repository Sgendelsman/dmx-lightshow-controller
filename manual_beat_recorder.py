from project_config import *

import soundfile as sf
import sounddevice as sd
import time
import json
import os
import keyboard
import sys

AUDIO_FILE = sys.argv[1]
os.makedirs(DETECTED_BEATS_OUTPUT_DIR, exist_ok=True)

# --- BEAT RECORDING ---
def record_beats(audio_file):
    print(f"\n🎧 Press SPACE to mark beats while '{audio_file}' plays.")
    print("🛑 Press ESC to cancel.\n")

    beat_times = []
    start_time = time.perf_counter()

    def on_space(e):
        timestamp = time.perf_counter() - start_time
        beat_times.append(timestamp)
        print(f"🔘 Beat at {timestamp:.3f} sec")

    keyboard.on_press_key("space", on_space)

    # Start audio
    data, fs = sf.read(audio_file, dtype='float32')
    sd.play(data, fs)

    # Wait for playback to finish or ESC
    while sd.get_stream().active:
        if keyboard.is_pressed("esc"):
            print("Recording canceled.")
            return None
        if keyboard.is_pressed("enter"):
            print("Recording complete!")
            break
        time.sleep(0.01)

    keyboard.unhook_all()
    return beat_times

# --- MAIN ---
if __name__ == "__main__":
    if not os.path.exists(AUDIO_FILE):
        print(f"❌ File not found: {AUDIO_FILE}")
        exit(1)

    beats = record_beats(AUDIO_FILE)
    if beats:
        outfile = os.path.join(DETECTED_BEATS_OUTPUT_DIR, os.path.basename(AUDIO_FILE) + ".manualbeats.json")
        with open(outfile, "w") as f:
            json.dump(beats, f)
        print(f"\n✅ Saved {len(beats)} manual beats to '{outfile}'")