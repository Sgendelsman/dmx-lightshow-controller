import soundfile as sf

from utils.project_config import *

def get_song_duration(song_path):
    return sf.info(song_path).duration
