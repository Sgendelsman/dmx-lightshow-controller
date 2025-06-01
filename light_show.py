import subprocess
import sys
import soundfile as sf
import time

from utils.project_config import *
import utils.audio_utils as audio_utils

def run_light_show(song_path, song_duration, start_offset=0.0, seek=0.0, sleep_time=0.0, start_time=0.0):
    return subprocess.Popen([
        sys.executable, 
        "light_show_worker.py", 
        song_path, 
        str(song_duration), 
        str(start_offset), 
        str(seek), 
        str(sleep_time),
        str(start_time)
    ])

def run_playlist(song_paths):
    subprocs = []
    try:
        sleep_time = 0
        start_time = time.time() + START_DELAY
        
        print(f'Starting the light show in {START_DELAY} seconds...')

        for i, song_path in enumerate(song_paths):
            start_offset = 0
            if i > 0:
                start_offset = song_path['start_early']
                sleep_time = sleep_time + max(0, prev_song_duration - prev_song_seek - prev_start_offset)

            seek = 0 if not 'seek' in song_path else song_path['seek']
            song_duration = audio_utils.get_song_duration(song_path['song'])
            subprocs.append(run_light_show(song_path['song'], song_duration, start_offset, seek, sleep_time, start_time))
            
            prev_song_seek = seek
            prev_song_duration = song_duration
            prev_start_offset = start_offset
        
        # Wait for all subprocesses to complete
        for proc in subprocs:
            proc.wait()
    except KeyboardInterrupt:
        print("🛑 CANCELLED LIGHT SHOW 🛑")
        for proc in subprocs:
            proc.terminate()
            proc.wait()

if __name__ == "__main__":
    run_playlist(SONGS)