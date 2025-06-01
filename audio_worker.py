import sys
import soundfile as sf
import sounddevice as sd
import time

if len(sys.argv) < 3:
    print("Usage: audio_worker.py <song_path> [start_time] [begin_audio_time]")
    sys.exit(1)

song_path = sys.argv[1]
start_time = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
begin_audio_time = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0

data, samplerate = sf.read(song_path, dtype='float32')

if start_time > 0:
    start_sample = int(start_time * samplerate)
    data = data[start_sample:]

print(f'📋 {song_path} will play in {(begin_audio_time - time.time()):.1f} seconds...')

# Play audio once it's ready.
while time.time() < begin_audio_time:
    time.sleep(0.001)
    
sd.play(data, samplerate)
sd.wait()
