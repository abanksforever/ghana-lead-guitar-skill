#!/usr/bin/env python3
"""Ear-assist for a Ghanaian lead guitarist. Machine estimates only - always confirm by ear.

  song FILE [--start S] [--duration D] [--bpb 4]
      tuning offset, tempo, top-3 key candidates, chord timeline with Roman numerals, capo tip
  lead FILE [--key G] [--bpm 120] [--grid 8|12|16]
      for a recording of a player's single-note lead: notes, intonation, timing vs grid, space

Needs: pip install --break-system-packages librosa soundfile   (ffmpeg for mp3/m4a/mp4)
"""
import argparse, sys, numpy as np

NAMES = ['C','Db','D','Eb','E','F','F#','G','Ab','A','Bb','B']
# Krumhansl-Kessler key profiles
KK_MAJ = np.array([6.35,2.23,3.48,2.33,4.38,4.09,2.52,5.19,2.39,3.66,2.29,2.88])
KK_MIN = np.array([6.33,2.68,3.52,5.38,2.60,3.53,2.54,4.75,3.98,2.69,3.34,3.17])
ROM_MAJ = {0:'I',2:'II',4:'III',5:'IV',7:'V',9:'VI',11:'VII',1:'bII',3:'bIII',6:'#IV',8:'bVI',10:'bVII'}

def load(path, start, dur):
    import librosa
    try: y, sr = librosa.load(path, sr=22050, mono=True, offset=start or 0.0, duration=dur)
    except Exception as e:
        sys.exit(f"Could not read {path}: {e}\nConvert first: ffmpeg -i in.m4a -ac 1 -ar 22050 out.wav")
    if len(y) < sr * 3: sys.exit('Audio shorter than 3 s - need a longer clip.')
    return y, sr

def key_candidates(chroma_mean):
    res = []
    for t in range(12):
        for prof, mode in ((KK_MAJ, 'major'), (KK_MIN, 'minor')):
            r = np.corrcoef(chroma_mean, np.roll(prof, t))[0, 1]
            res.append((r, t, mode))
    return sorted(res, reverse=True)[:3]

def templates():
    T = []
    for r in range(12):
        for q, ivs in (('', [0,4,7]), ('m', [0,3,7]), ('7', [0,4,7,10])):
            v = np.zeros(12); v[[(r+i) % 12 for i in ivs]] = 1; v[r] += 0.5  # weight root
            T.append((NAMES[r] + q, r, q, v / np.linalg.norm(v)))
    return T

def roman(root, q, tonic, mode):
    ref = tonic if mode == 'major' else (tonic + 3) % 12  # minor keys: numerals vs relative major
    iv = (root - ref) % 12; r = ROM_MAJ[iv]
    return (r.lower() if q == 'm' else r) + ('7' if q == '7' else '')

def cmd_song(a):
    import librosa
    y, sr = load(a.file, a.start, a.duration)
    tuning = librosa.estimate_tuning(y=y, sr=sr)
    yh, yp = librosa.effects.hpss(y)
    tempo, beats = librosa.beat.beat_track(y=yp if np.abs(yp).sum() > 0 else y, sr=sr)
    tempo = float(np.atleast_1d(tempo)[0])
    chroma = librosa.feature.chroma_cqt(y=yh, sr=sr, tuning=tuning, bins_per_octave=36)
    cands = key_candidates(chroma.mean(axis=1))
    r0, tonic, mode = cands[0]
    print(f"Tuning offset: {tuning*100:+.0f} cents from A440" + ("  <- band tuned off concert; tune to the track" if abs(tuning) > 0.15 else ''))
    print(f"Tempo: ~{tempo:.0f} BPM (could be {tempo/2:.0f} or {tempo*2:.0f}; in 12/8 highlife the felt pulse may be {tempo*2/3:.0f} dotted-quarters)")
    print('Key candidates: ' + ' | '.join(f"{NAMES[t]} {m} ({r:.2f})" for r, t, m in cands))
    if cands[0][0] - cands[1][0] < 0.05: print('  -> top two are close: check by ear which note feels like home on the final chord')
    if len(beats) < 4: print('Too few beats detected for a chord timeline.'); return
    sync = librosa.util.sync(chroma, beats, aggregate=np.median)
    T = templates(); times = librosa.frames_to_time(beats, sr=sr)
    labels = []
    for i in range(sync.shape[1]):
        v = sync[:, i]; n = np.linalg.norm(v)
        if n < 1e-6: labels.append(('N', 0, '', 0)); continue
        v = v / n; scores = [(float(v @ tv), nm, r, q) for nm, r, q, tv in T]
        s, nm, r, q = max(scores); labels.append((nm, r, q, s))
    # smooth: majority over each bar
    times = times + (a.start or 0)
    bpb = a.bpb
    print(f"\nChord per bar ({bpb} beats/bar, counted from the first detected beat; if changes look shifted, "
          f"rerun with --start on a downbeat. '?' = low confidence):")
    bars = []
    for b in range(0, len(labels), bpb):
        seg = labels[b:b+bpb]; names = [l[0] for l in seg]
        best = max(set(names), key=names.count); conf = names.count(best) / len(seg)
        lab = next(l for l in seg if l[0] == best)
        t0 = times[min(b, len(times)-1)]
        bars.append((t0, best, lab[1], lab[2], conf))
    line = []
    for i, (t0, nm, r, q, conf) in enumerate(bars):
        rn = roman(r, q, tonic, mode) if nm != 'N' else '-'
        line.append(f"{nm}{'?' if conf < 0.5 else ''} ({rn})")
        if (i + 1) % 4 == 0:
            print(f"  {bars[i-3][0]:6.1f}s  | " + ' | '.join(line) + ' |'); line = []
    if line: print(f"  {bars[-len(line)][0]:6.1f}s  | " + ' | '.join(line) + ' |')
    shapes = {'major': {'C','G','D','A','E'}, 'minor': {'A','E','D'}}[mode]
    tips = [f"capo {c}: {NAMES[(tonic-c)%12]}{'m' if mode=='minor' else ''} shapes" for c in range(8) if NAMES[(tonic-c)%12] in shapes]
    print('\nCapo options: ' + '; '.join(tips))

def cmd_lead(a):
    import librosa
    y, sr = load(a.file, a.start, a.duration)
    f0, voiced, _ = librosa.pyin(y, fmin=75, fmax=1400, sr=sr, frame_length=2048, hop_length=256)
    hop = 256; ft = librosa.frames_to_time(np.arange(len(f0)), sr=sr, hop_length=hop)
    env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=64, n_fft=512)  # fine time resolution
    onsets = librosa.onset.onset_detect(onset_envelope=env, sr=sr, hop_length=64, units='time')
    if a.bpm:  # no click in the recording: fit the grid phase to the player, so we measure steadiness
        tempo = a.bpm; step = 60 / tempo / {8: 2, 12: 3, 16: 4}[a.grid]
        ph = np.angle(np.mean(np.exp(2j * np.pi * onsets / step))) / (2 * np.pi) * step if len(onsets) else 0
        beat_times = np.arange(ph % step, ft[-1] + step, 60 / tempo)
    else:
        tempo, bf = librosa.beat.beat_track(y=y, sr=sr, hop_length=hop); tempo = float(np.atleast_1d(tempo)[0])
        beat_times = librosa.frames_to_time(bf, sr=sr, hop_length=hop)
    notes = []
    bounds = list(onsets) + [ft[-1]]
    for s, e in zip(bounds[:-1], bounds[1:]):
        m = (ft >= s + 0.03) & (ft < min(e, s + 0.30)) & voiced & ~np.isnan(f0)  # skip pick attack
        if m.sum() < 3: continue
        midi = librosa.hz_to_midi(np.median(f0[m])); n = int(round(midi))
        if notes and n == notes[-1][2] and s - notes[-1][0] < 0.09:
            continue  # double-triggered onset on one note
        notes.append((s, e, n, (midi - n) * 100))
    if not notes: sys.exit('No pitched notes found - is this a single-note lead recording?')
    sub = {8: 2, 12: 3, 16: 4}[a.grid]
    grid = []
    for b0, b1 in zip(beat_times[:-1], beat_times[1:]):
        grid += list(np.linspace(b0, b1, sub, endpoint=False))
    grid = np.array(grid) if grid else beat_times
    tonic = None
    if a.key:
        k = a.key.rstrip('m'); kn = {'Db':'Db','C#':'Db','D#':'Eb','Gb':'F#','G#':'Ab','A#':'Bb'}.get(k, k)
        tonic = NAMES.index(kn); minor = a.key.endswith('m')
        scale = {(tonic + i) % 12 for i in ([0,2,3,5,7,8,10] if minor else [0,2,4,5,7,9,11])}
    print(f"Tempo used: {tempo:.0f} BPM, grid: {a.grid}ths")
    offs, sharp, outkey = [], [], []
    print('  time    note  cents  timing(ms)')
    for s, e, n, c in notes:
        d = (s - grid[np.argmin(np.abs(grid - s))]) * 1000 if len(grid) else 0; offs.append(d)
        nm = NAMES[n % 12] + str(n // 12 - 1)
        flag = ''
        if abs(c) > 25: flag += ' out-of-tune'; sharp.append(nm)
        if tonic is not None and n % 12 not in scale: flag += ' out-of-key'; outkey.append(nm)
        print(f"  {s:6.2f}  {nm:5s} {c:+5.0f}   {d:+5.0f}{flag}")
    offs = np.array(offs); dur = notes[-1][1] - notes[0][0]
    span = (ft >= notes[0][0]) & (ft <= notes[-1][1])
    rms = librosa.feature.rms(y=y, hop_length=hop)[0][:len(ft)]
    sounding = dur * np.mean((rms[span[:len(rms)]] > 0.1 * rms.max()))
    print('\nTiming: mean |offset| %.0f ms, spread (std) %.0f ms, %d%% within 25 ms of the grid' % (
        np.mean(np.abs(offs)), np.std(offs), 100 * np.mean(np.abs(offs) < 25)))
    if not a.bpm:
        print('  Overall tendency vs the track: %s' % ('rushing (ahead)' if np.mean(offs) < -10 else 'dragging (behind)' if np.mean(offs) > 10 else 'centred'))
    else:
        print('  (No reference beat in the file, so this measures steadiness, not rushing/dragging.)')
    late = [NAMES[n % 12] for (s_, e_, n, c), o in zip(notes, offs) if abs(o) > 25]
    if late: print('  Notes >25 ms off the grid: ' + ', '.join(late[:10]))
    print(f"Intonation: {len(sharp)} of {len(notes)} notes >25 cents off" + (f" ({', '.join(sharp[:8])})" if sharp else ''))
    if tonic is not None: print(f"Out-of-key notes: {len(outkey)}" + (f" ({', '.join(outkey[:8])})" if outkey else ''))
    print(f"Density: {len(notes)/max(dur,1e-3):.1f} notes/s; sound vs space: {100*sounding/max(dur,1e-3):.0f}% sounding")

p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
sp = p.add_subparsers(dest='cmd', required=True)
for name, fn in (('song', cmd_song), ('lead', cmd_lead)):
    x = sp.add_parser(name); x.add_argument('file'); x.add_argument('--start', type=float); x.add_argument('--duration', type=float)
    x.set_defaults(fn=fn)
    if name == 'song': x.add_argument('--bpb', type=int, default=4)
    else:
        x.add_argument('--key'); x.add_argument('--bpm', type=float); x.add_argument('--grid', type=int, choices=[8, 12, 16], default=8)
a = p.parse_args(); a.fn(a)
