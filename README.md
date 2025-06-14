# dmx-lightshow-controller

## Making a new light show for a song

* Configure scenes in `cue_lists/helpers/channel_configs.json`
* Configure chasers that occur across beats in `cue_lists/helpers/patterns.yaml`
* Create a placements file in the `cue_lists` directory for each song:
  * Example: `cue_lists/unbroken.mp3.placements.md`

## Running the light show

`python light_show.py`

## Beat recording

All beats get saved in `cue_lists`. Run all of these from the root directory.

### Automatic

`python -m beat_recorder.auto`

### Manual

`python -m beat_recorder.manual path/to/audio.file`

There are instructions while you're recording beats.
