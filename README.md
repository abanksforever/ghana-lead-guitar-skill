# Ghana Lead Guitar: a Claude skill

A [Claude](https://claude.ai) skill that turns Claude into a senior Ghanaian lead guitarist and teacher. It covers local gospel (praise and worship), highlife, palm-wine, burger and Afro-highlife.

It does five things:

- **Finds the key and chords of a song.** You can send an audio clip, a WhatsApp voice note, a chord chart, sol-fa, or just the song's name. It gives the key three ways: the concert key, a capo plan, and Nashville numbers with tonic sol-fa for the band.
- **Writes licks, fills, intros, endings and rhythm parts** in tab, with the counts, the sol-fa and a practice tempo.
- **Coaches players.** It measures a recording of your playing (timing, notes out of tune, notes out of key, how much space you leave) and gives the top 3 fixes, each with a drill and a target.
- **Explains technique:** picking-hand feel (palm-wine thumb and index, hybrid picking for sixths), muting, syncopation, double stops and fretboard positions. It also picks the right scale flavour for each chord: major, pentatonic, mixolydian, harmonic minor, or gospel chromatic passing tones.
- **Prepares church services and gigs.** For each song: key, capo, intro, answer licks, ending, and transitions between songs, including key changes in a medley.

## What makes it different: every tab is checked

AI-written guitar tab often contains wrong frets. This skill ships with two scripts that Claude uses to check its own work before you see it:

| Script | What it does |
|---|---|
| `scripts/gtr.py` | Lines up tab columns and counts automatically, then checks every note against the key and the chord (chord tone, passing note, or out of key). Also does capo charts, transposing, Nashville numbers to chord names, tonic sol-fa, sixths/thirds ladders and fretboard maps (major, minor, pentatonic, mixolydian, major blues). Uses only the Python standard library. |
| `scripts/analyze_audio.py` | From a song clip: key candidates, tempo, a chord for each bar, and the tuning offset. From a recording of a player: notes, intonation in cents, timing against the beat in milliseconds, and how much space they leave. Uses librosa. |

Example: an original "sixths answer" lick from the built-in library, generated and checked by `gtr.py`:

```
  G                   C
e|-------------------|------------------|
B|---8---10-12-------|-10---8---7---5---|
G|-------------------|------------------|
D|---9---10-12-------|-10---9---7---5---|
A|-------------------|------------------|
E|-------------------|------------------|
   1 & 2 &  3  & 4 &   1  & 2 & 3 & 4 &
```

## What's inside

```
SKILL.md                 instructions Claude follows: workflows, style map, technique explainer, 11 original licks, templates
scripts/gtr.py           fretboard, transposition and tab verification
scripts/analyze_audio.py audio analysis for songs and for a player's lead
examples/                three sample conversations (voice note -> key, licks in Ab, coaching report)
```

## Install

**Claude Code**

```bash
git clone https://github.com/abanksforever/ghana-lead-guitar-skill ~/.claude/skills/ghana-lead-guitar
```

**Claude apps (claude.ai, desktop)**

1. On this page, click **Code -> Download ZIP**.
2. In Claude, open Settings, find the Skills section, and upload the ZIP as a custom skill.

Then just ask, for example: *"Our MD says we're in Ab, 1 4 1 5. Give me an intro lick and an ending."*

## Use the scripts on their own

```bash
python3 scripts/gtr.py key Bb                       # scale, chords, sol-fa, capo options
python3 scripts/gtr.py nashville "1 4 5 6m" --key Eb
python3 scripts/gtr.py doublestops G --interval 6 --strings DB
python3 scripts/gtr.py scale G --type mixolydian --frets 0-12
python3 scripts/gtr.py render "- D9+B8 - D10+B10 D12+B12 - - - | D10+B10 - D9+B8 - D7+B7 - D5+B5 -" --chords "G C" > lick.txt
python3 scripts/gtr.py check lick.txt --key G --chords "G C"

pip install librosa soundfile                       # for audio; ffmpeg is needed for mp3/m4a/opus
python3 scripts/analyze_audio.py song my_song.mp3
python3 scripts/analyze_audio.py lead my_take.wav --key Bb --bpm 100
```

## Notes

- **The audio analysis gives estimates.** The skill always tells you how to confirm the key by ear, and it never claims to have heard a song it didn't analyse.
- **It respects copyright.** It gives keys, chord progressions and style analysis, but it won't transcribe a recorded solo, melody or lyrics note for note. It writes original licks in the same style instead.
- **The examples were produced from test recordings** that were generated with known answers to check the analysis.

## License

[MIT](LICENSE)
