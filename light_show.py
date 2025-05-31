import subprocess
import sys
import soundfile as sf
import time

from utils.project_config import *

def get_song_duration(song_path):
    return sf.info(song_path).duration

def run_light_show(song_path, start_offset=0.0, sleep_time=0.0):
    return subprocess.Popen([sys.executable, "worker.py", song_path, str(start_offset), str(sleep_time)])

def run_playlist(song_paths):
    subprocs = []
    try:
        for i, song_path in enumerate(song_paths):
            sleep_time = 0
            if i > 0:
                prev_song_duration = get_song_duration(song_paths[i - 1]['song'])
                sleep_time = max(0, prev_song_duration - song_path['start_offset'])
            subprocs.append(run_light_show(song_path['song'], song_path['start_offset'], sleep_time))
        
        # Wait for all subprocesses to complete
        for proc in subprocs:
            proc.wait()
    except KeyboardInterrupt:
        print("🛑 Cancelled light show!")
        for proc in subprocs:
            proc.terminate()
            proc.wait()

if __name__ == "__main__":
    songs = [
        {'song': f'{MUSIC_DIRECTORY}/unbroken.mp3', 'start_offset': 0.0},
        {'song': f'{MUSIC_DIRECTORY}/kairo.mp3', 'start_offset': 6.995},
    ]

    run_playlist(songs)