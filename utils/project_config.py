### ----------------------------- BEAT CONTROL -----------------------------

PACKETS_PER_SECOND = 30

MUSIC_DIRECTORY = "music"
BEAT_DIRECTORY = "cue_lists"
BUILDER_DIRECTORY = "beat_recorder"

BEAT_DELAY_ADJUSTMENT = 0.120 # Offset of beats to sync up to audio playback (in seconds)
START_DELAY = 5 # How many seconds to give all of the processes to sync up before starting the music

# song -> Location of music file
# start_early -> How many seconds the previous song has left before it starts playing. Reduces downtime in show
# seek -> How many seconds into the song should the audio playback begin. Helpful for testing
SONGS = [
    {'song': f'{MUSIC_DIRECTORY}/unbroken.mp3', 'start_early': 0, 'seek': 0.0},
    {'song': f'{MUSIC_DIRECTORY}/kairo.mp3', 'start_early': 6.495, 'seek': 0.0},
    {'song': f'{MUSIC_DIRECTORY}/doruksen_song1.mp3', 'start_early': 0.774, 'seek': 0.0},
    {'song': f'{MUSIC_DIRECTORY}/doruksen_song2_1.mp3', 'start_early': 0.59, 'seek': 0.0},
    {'song': f'{MUSIC_DIRECTORY}/doruksen_song2_2.mp3', 'start_early': 1.636, 'seek': 0.0}
]

### ----------------------------- ARTNET -----------------------------
ARTNET_IP = "127.0.0.1"  # IP of your USB DMX controller
ARTNET_PORT = 6454