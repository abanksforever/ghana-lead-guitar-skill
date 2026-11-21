# Example 1: Key and chords from a WhatsApp voice note

**Request:**

> Chale this is a voice note of the praise song we're doing on Sunday (praise_voicenote.opus). What key is it in and what are the chords? I like to play with capo.

**Response from the skill:**

I ran your voice note through the analyser. These are machine estimates, so confirm them by ear with the check below before Sunday.

```
Song: Sunday praise (voice note) | Concert key: Bb major | Do = Bb | Tempo ~118-120 BPM, straight 4/4 praise
Capo:  capo 3 -> play G shapes (easiest)   or   capo 1 -> play A shapes

Section     Numbers              Sol-fa (bass)     Concert chords        Capo-3 shapes
Part A      | 1 | 4 | 5 | 1 |    d  f  s  d       | Bb | Eb | F  | Bb |  | G  | C  | D  | G  |
Part B      | 6m| 4 | 5 | 1 |    l  f  s  d       | Gm | Eb | F  | Bb |  | Em | C  | D  | G  |
(A, B, A, B: each chord lasts one bar)

Confidence: high. Bb major led the next candidate (Eb major) clearly, 0.95 against 0.64,
and every bar matched a Bb-major chord. Tuning is A440 (+1 cent), so tune normally.
Guitar role: off-beat chops on the top strings in Part A; a sixths answer after each vocal line in Part B.
```

**30-second ear check:** with capo 3, hit an open G-shape chord on the last beat of the song. It should sound like "home". If an Em shape sounds more final, the song is in G minor. The analyser rated that unlikely (0.59).

**Starter part (capo 3, G shapes).** Praise chops: triads on the top three strings, struck on every "&" and muted on the beat.
```
  G                 C                 D                 G
e|---3---3---3---3-|---3---3---3---3-|---5---5---5---5-|---3---3---3---3-|
B|---3---3---3---3-|---5---5---5---5-|---7---7---7---7-|---3---3---3---3-|
G|---4---4---4---4-|---5---5---5---5-|---7---7---7---7-|---4---4---4---4-|
D|-----------------|-----------------|-----------------|-----------------|
A|-----------------|-----------------|-----------------|-----------------|
E|-----------------|-----------------|-----------------|-----------------|
   1 & 2 & 3 & 4 &   1 & 2 & 3 & 4 &   1 & 2 & 3 & 4 &   1 & 2 & 3 & 4 &
```
For Part B, use an Em shape (e3 B5 G4 = G, E, B) in place of the first G.
Verified with gtr.py check: 0 out-of-key notes.

Before the service, confirm the key with your MD. If the keyboardist moves the medley up, the capo-3 G shapes move with you: capo 4 for B, or capo 5 for C.
