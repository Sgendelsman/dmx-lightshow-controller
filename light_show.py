from project_config import *

import time
import json
import os
import sounddevice as sd
import soundfile as sf
from threading import Thread
import artnet_utils

def load_beat_file(song_path):
    base = os.path.basename(song_path)
    manual_file = os.path.join(DETECTED_BEATS_OUTPUT_DIR, base + ".manualbeats.json")
    auto_file = os.path.join(DETECTED_BEATS_OUTPUT_DIR, base + ".beats.json")

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

def generate_cues(beat_times):
    return [
        (t, {
            1: 255 if i % 2 == 0 else 0,
            2: 255 if i % 2 == 1 else 0
        })
        for i, t in enumerate(beat_times)
    ]

def play_audio(file, done_flag):
    data, fs = sf.read(file, dtype='float32')
    sd.play(data, fs)
    while sd.get_stream().active:
        time.sleep(0.01)
    done_flag.append(True)  # signal playback is done

def fade_to_black(last_values):
    print("🌒 Fading to black...")
    for i in range(1, FADE_STEPS + 1):
        fade = {ch: int(val * (1 - i / FADE_STEPS)) for ch, val in last_values.items()}
        artnet_utils.send_dmx(UNIVERSE, fade)
        time.sleep(FADE_DURATION / FADE_STEPS)

def run_show(song_list):
    for i, song_path in enumerate(song_list):
        print(f"\n🎵 Playing '{song_path}'")
        beat_times = load_beat_file(song_path)
        
        # Modify beat times here to sync up to the audio playback!
        beat_times = [beat_time + BEAT_DELAY_ADJUSTMENT for beat_time in beat_times]
        
        cues = generate_cues(beat_times)
        
        # Start audio
        audio_done = []
        audio_thread = Thread(target=play_audio, args=(song_path, audio_done), daemon=True)
        audio_thread.start()

        start_time = time.perf_counter()
        cue_index = 0
        last_values = {}

        # Run until audio finishes
        while not audio_done:
            now = time.perf_counter() - start_time
            if cue_index < len(cues):
                cue_time, channel_values = cues[cue_index]
                if now >= cue_time - DMX_LATENCY:
                    artnet_utils.send_dmx(UNIVERSE, channel_values)
                    last_values = channel_values
                    cue_index += 1
            time.sleep(0.001)

        # After audio finishes, fade out
        fade_to_black(last_values)

    print("\n🏁 Show complete!")

if __name__ == "__main__":
    run_show(SONG_LIST)