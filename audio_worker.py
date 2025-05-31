import sys
import soundfile as sf
import sounddevice as sd

if len(sys.argv) < 2:
    print("Usage: audio_worker.py <song_path> [start_time]")
    sys.exit(1)

song_path = sys.argv[1]
start_time = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0

data, samplerate = sf.read(song_path, dtype='float32')

if start_time > 0:
    start_sample = int(start_time * samplerate)
    data = data[start_sample:]

sd.play(data, samplerate)
sd.wait()
