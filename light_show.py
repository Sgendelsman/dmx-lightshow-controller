import subprocess
import sys
import soundfile as sf
import time

from utils.project_config import *
import utils.audio_utils as audio_utils

def run_light_show(song_path, song_duration, start_offset=0.0, seek=0.0, sleep_time=0.0):
    return subprocess.Popen([
        sys.executable, 
        "light_show_worker.py", 
        song_path, 
        str(song_duration), 
        str(start_offset), 
        str(seek), 
        str(sleep_time)
    ])

def run_playlist(song_paths):
    subprocs = []
    try:
        for i, song_path in enumerate(song_paths):
            sleep_time = 0
            if i > 0:
                sleep_time = max(0, prev_song_duration - song_path['start_offset'] - prev_song_seek)

            seek = 0 if not 'seek' in song_path else song_path['seek']
            song_duration = audio_utils.get_song_duration(song_path['song'])
            subprocs.append(run_light_show(song_path['song'], song_duration, song_path['start_offset'], seek, sleep_time))
            
            prev_song_seek = seek
            prev_song_duration = song_duration
        
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
        {'song': f'{MUSIC_DIRECTORY}/unbroken.mp3', 'start_offset': 0.0, 'seek': 180.0},
        {'song': f'{MUSIC_DIRECTORY}/kairo.mp3', 'start_offset': 6.995, 'seek': 0.0},
    ]

    run_playlist(songs)