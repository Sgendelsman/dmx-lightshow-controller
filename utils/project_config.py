### ----------------------------- BEAT CONTROL -----------------------------

PACKETS_PER_SECOND = 30

MUSIC_DIRECTORY = "music"
BEAT_DIRECTORY = "cue_lists"
BUILDER_DIRECTORY = "beat_recorder"

DMX_LATENCY = 0.015  # ~15 ms compensation for DMX/ArtNet delay

FADE_DURATION = 1.5   # seconds
FADE_STEPS = 20

BEAT_DELAY_ADJUSTMENT = -0.100 # Offset of beats to sync up to audio playback

### ----------------------------- ARTNET -----------------------------
ARTNET_IP = "127.0.0.1"  # IP of your USB DMX controller
ARTNET_PORT = 6454
UNIVERSE = 0