### ----------------------------- BEAT CONTROL -----------------------------

PACKETS_PER_SECOND = 30

MUSIC_DIRECTORY = "music"
BEAT_DIRECTORY = "cue_lists"
BUILDER_DIRECTORY = "beat_recorder"

START_DELAY = 5 # How many seconds to give all of the processes to sync up before starting the music

# song -> Location of music file
# start_early -> How many seconds the previous song has left before it starts playing. Reduces downtime in show
# seek -> How many seconds into the song should the audio playback begin. Helpful for testing
# beat_delay -> How many seconds to push back beats from the audio. Helps them sync up (both testing AND live)
SONGS = [
    {'song': f'{MUSIC_DIRECTORY}/unbroken.mp3', 'start_early': 0, 'seek': 0.0, 'beat_delay': 0.180},
    {'song': f'{MUSIC_DIRECTORY}/kairo.mp3', 'start_early': 6.495, 'seek': 0.0, 'beat_delay': 0.120},
    {'song': f'{MUSIC_DIRECTORY}/doruksen_song1.mp3', 'start_early': 0.774, 'seek': 0.0, 'beat_delay': -0.085},
    {'song': f'{MUSIC_DIRECTORY}/doruksen_song2_1.mp3', 'start_early': 0.59, 'seek': 0.0, 'beat_delay': 0.046},
    {'song': f'{MUSIC_DIRECTORY}/doruksen_song2_2.mp3', 'start_early': 1.736, 'seek': 0.0, 'beat_delay': -0.060}
]

MAX_BRIGHTNESS = 100 # 0 - 100%

### ----------------------------- ARTNET -----------------------------
ARTNET_IP = "127.0.0.1"  # IP of your USB DMX controller
ARTNET_PORT = 6454