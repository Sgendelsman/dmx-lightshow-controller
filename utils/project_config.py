
### ----------------------------- SONGS/AUDIO -----------------------------
MUSIC_DIRECTORY = "music"
AUDIO_FILES = [
    "unbroken.WAV",
    "helena.WAV"
]
SONG_LIST = ["{0}/{1}".format(MUSIC_DIRECTORY, song) for song in AUDIO_FILES]

SKIP_HOTKEY = 'shift+n'  # 🔄 Skip to next song

### ----------------------------- BEAT CONTROL -----------------------------

BEAT_DIRECTORY = "beat_cache"

DMX_LATENCY = 0.015  # ~15 ms compensation for DMX/ArtNet delay

FADE_DURATION = 1.5   # seconds
FADE_STEPS = 20

BEAT_DELAY_ADJUSTMENT = -0.100 # Offset of beats to sync up to audio playback

### ----------------------------- ARTNET -----------------------------
ARTNET_IP = "127.0.0.1"  # IP of your USB DMX controller
ARTNET_PORT = 6454
UNIVERSE = 0