MUSIC_DIRECTORY = "music"
AUDIO_FILES = [
    # "unbroken.WAV",
    "helena.WAV"
]
SONG_LIST = ["{0}/{1}".format(MUSIC_DIRECTORY, song) for song in AUDIO_FILES]

DETECTED_BEATS_OUTPUT_DIR = "beat_cache"

SKIP_HOTKEY = 'shift+n'  # 🔄 Skip to next song

UNIVERSE = 0
DMX_LATENCY = 0.015  # ~15 ms compensation for DMX/ArtNet delay

FADE_DURATION = 1.5   # seconds
FADE_STEPS = 20

SONG_STARTUP_LATENCY = 0.050 # ~50ms compensation for startup of song audio playback