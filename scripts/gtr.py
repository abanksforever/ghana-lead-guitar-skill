#!/usr/bin/env python3
"""Fretboard toolkit for Ghanaian lead guitar work. Standard tuning unless --tuning given.

  key KEY                       scale, diatonic chords, Nashville numbers, tonic sol-fa, capo options
  capo KEY                      capo position -> chord-shape key table
  nashville "1 4 5 6m" --key Bb numbers -> chord names (also accepts roman: "I IV V vi")
  transpose "G C D Em" --from G --to Bb
  doublestops KEY --interval 6|3 --strings GE|DB|GB|BE   diatonic sixths/thirds ladder as tab
  scale KEY [--type major|minor|majpent|minpent|mixolydian|majblues] [--frets 0-15]   fretboard map of degrees
  check --key G [--chords "G C G D"] [--capo N] FILE|-   verify a tab: notes, degree, sol-fa, chord fit per bar
  render "D9+B8 - D10+B10 - ... | ..." [--steps 8|12|16] [--chords "G C"]   aligned tab + count line
         (steps per bar: 8 = 4/4 eighths, 12 = 12/8, 16 = sixteenths; '-' = rest; '+' joins simultaneous notes)
KEY examples: G, Bb, F#, Am, C#m, Ebm
"""
import argparse, re, sys

SH = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
FL = ['C','Db','D','Eb','E','F','Gb','G','Ab','A','Bb','B']
PC = {n: i for i, n in enumerate(SH)}; PC.update({n: i for i, n in enumerate(FL)})
PC.update({'Cb': 11, 'Fb': 4, 'E#': 5, 'B#': 0})
MAJ = [0, 2, 4, 5, 7, 9, 11]; MIN = [0, 2, 3, 5, 7, 8, 10]
SOLFA = {0:'d',1:'de',2:'r',3:'me',4:'m',5:'f',6:'fi',7:'s',8:'si',9:'l',10:'te',11:'t'}
DEG = {0:'1',1:'b2',2:'2',3:'b3',4:'3',5:'4',6:'#4',7:'5',8:'b6',9:'6',10:'b7',11:'7'}
QUAL = {'':[0,4,7],'maj':[0,4,7],'m':[0,3,7],'min':[0,3,7],'7':[0,4,7,10],'maj7':[0,4,7,11],
        'm7':[0,3,7,10],'sus2':[0,2,7],'sus4':[0,5,7],'sus':[0,5,7],'add9':[0,4,7,2],'madd9':[0,3,7,2],
        '6':[0,4,7,9],'m6':[0,3,7,9],'9':[0,4,7,10,2],'maj9':[0,4,7,11,2],'m9':[0,3,7,10,2],
        'dim':[0,3,6],'dim7':[0,3,6,9],'m7b5':[0,3,6,10],'aug':[0,4,8],'7sus4':[0,5,7,10],'5':[0,7]}
CTNAME = {0:'R',1:'b9',2:'9',3:'b3',4:'3',5:'11',6:'b5/#11',7:'5',8:'#5/b13',9:'6/13',10:'b7',11:'7'}
STD = ['E','A','D','G','B','E']  # low -> high

def parse_key(k):
    m = re.fullmatch(r'([A-Ga-g][#b]?)(m|min|minor)?', k.strip())
    if not m: sys.exit(f'bad key: {k}')
    root = m.group(1)[0].upper() + m.group(1)[1:]
    return PC[root], bool(m.group(2)), root

def uses_flats(root, minor):
    flat_major = {'F','Bb','Eb','Ab','Db','Gb','Cb'}
    flat_minor = {'D','G','C','F','Bb','Eb','Ab'}
    return ('b' in root) or (root in (flat_minor if minor else flat_major))

def nm(pc, flats): return (FL if flats else SH)[pc % 12]

def parse_chord(c):
    m = re.fullmatch(r'([A-G][#b]?)([^/]*)(?:/([A-G][#b]?))?', c.strip())
    if not m or m.group(2) not in QUAL: return None
    r = PC[m.group(1)]; tones = {(r + i) % 12 for i in QUAL[m.group(2)]}
    if m.group(3): tones.add(PC[m.group(3)])
    return r, tones

def do_pc(tonic, minor):  # tonic sol-fa "do" (la-based minor)
    return (tonic + 3) % 12 if minor else tonic

def cmd_key(a):
    t, minor, root = parse_key(a.key); f = uses_flats(root, minor); sc = MIN if minor else MAJ
    print(f"Key: {nm(t,f)} {'minor' if minor else 'major'}")
    print('Scale:   ' + '  '.join(nm(t+i, f) for i in sc))
    d = do_pc(t, minor)
    print('Sol-fa:  ' + '  '.join(SOLFA[(t+i-d) % 12] for i in sc) + ("   (la-based minor)" if minor else ''))
    romans = ['i','ii°','III','iv','v (V)','VI','VII'] if minor else ['I','ii','iii','IV','V','vi','vii°']
    quals = ['m','dim','','m','m','',''] if minor else ['','m','m','','','m','dim']
    print('Chords:')
    for n, (iv, q, r) in enumerate(zip(sc, quals, romans), 1):
        extra = f"  (harmonic-minor V = {nm(t+7,f)} / {nm(t+7,f)}7)" if minor and n == 5 else ''
        print(f"  {n}  {r:7s} {nm(t+iv,f)}{q}{extra}")
    rel = (t + 3) % 12 if minor else (t + 9) % 12
    print(f"Relative {'major' if minor else 'minor'}: {nm(rel,f)}{'' if minor else 'm'}")
    cmd_capo(a)

def cmd_capo(a):
    t, minor, root = parse_key(a.key)
    friendly = {'C','G','D','A','E'} if not minor else {'A','E','D'}
    print(f"Capo options for concert {a.key} (shapes you finger):")
    for c in range(0, 8):
        s = SH[(t - c) % 12]; s = {'A#':'Bb','D#':'Eb','G#':'Ab','C#':'C#','F#':'F#'}.get(s, s)
        star = '  <- easy open shapes' if s in friendly else ''
        print(f"  capo {c}: play {s}{'m' if minor else ''} shapes{star}")

def to_chords(tokens, t, minor, f):
    out = []
    romans = {'i':1,'ii':2,'iii':3,'iv':4,'v':5,'vi':6,'vii':7}
    for tok in tokens:
        m = re.fullmatch(r'([b#]?)([1-7]|[ivIV]+)(.*)', tok)
        if not m: out.append('?'); continue
        acc, deg, suf = m.groups()
        if deg.isdigit(): n = int(deg); low = False
        else: n = romans.get(deg.lower(), 0); low = deg.islower()
        if not n: out.append('?'); continue
        base = (MIN if minor else MAJ)[n-1] + (-1 if acc == 'b' else 1 if acc == '#' else 0)
        if low and not suf.startswith('m') and 'dim' not in suf and suf != '°': suf = 'm' + suf
        out.append(nm(t+base, f) + suf.replace('°', 'dim'))
    return out

def cmd_nashville(a):
    t, minor, root = parse_key(a.key); f = uses_flats(root, minor)
    print(' '.join(to_chords(a.numbers.replace('|',' ').split(), t, minor, f)))

def cmd_transpose(a):
    t1, _, _ = parse_key(a.frm); t2, m2, r2 = parse_key(a.to); f = uses_flats(r2, m2)
    out = []
    for c in a.chords.replace('|',' ').split():
        m = re.fullmatch(r'([A-G][#b]?)([^/]*)(?:/([A-G][#b]?))?', c)
        if not m: out.append(c); continue
        s = nm(PC[m.group(1)] - t1 + t2, f) + m.group(2)
        if m.group(3): s += '/' + nm(PC[m.group(3)] - t1 + t2, f)
        out.append(s)
    print(' '.join(out))

def open_pcs(tuning): return [PC[x] for x in tuning]

def cmd_doublestops(a):
    t, minor, root = parse_key(a.key); f = uses_flats(root, minor); sc = MIN if minor else MAJ
    names = {'E':0,'A':1,'D':2,'G':3,'B':4,'e':5}
    lo = names[a.strings[0].upper() if a.strings[0] != 'e' else 'E']
    hi = 5 if a.strings[1] in 'eE' else names[a.strings[1].upper()]
    tun = open_pcs(STD); step = 5 if a.interval == 6 else 2
    lab = ['e','B','G','D','A','E']
    rows = []; prev = a.min_fret; OFF = [0, 5, 10, 15, 19, 24]
    for i in range(8):
        dl = sc[i % 7] + 12 * (i // 7); du_i = i + step
        du = sc[du_i % 7] + 12 * (du_i // 7)
        lo_pc, hi_pc = (t + dl) % 12, (t + du) % 12
        for fl in range(prev, prev + 12):   # next position up the neck: one continuous ladder
            if (tun[lo] + fl) % 12 == lo_pc:
                fh = fl + OFF[lo] + (du - dl) - OFF[hi]
                if fh < 0: fh += 12; fl += 12
                rows.append((i % 7 + 1, (fl, fh), nm(lo_pc, f), nm(hi_pc, f))); prev = fl; break
    print(f"Diatonic {'6ths' if a.interval == 6 else '3rds'} in {a.key} on {lab[5-lo]} & {lab[5-hi]} strings (lower note = scale degree):")
    lines = {s: f"{lab[5-s]}|-" for s in (hi, lo)}
    for deg, (fl, fh), ln, hn in rows:
        w = max(len(str(fl)), len(str(fh)))
        lines[hi] += str(fh).ljust(w, '-') + '--'; lines[lo] += str(fl).ljust(w, '-') + '--'
    print(lines[hi] + '|'); print(lines[lo] + '|')
    print('   ' + '  '.join(f"{d}:{l}/{h}" for d, _, l, h in rows))

def cmd_scale(a):
    t, minor, root = parse_key(a.key); f = uses_flats(root, minor)
    types = {'major':MAJ,'minor':MIN,'majpent':[0,2,4,7,9],'minpent':[0,3,5,7,10],
             'mixolydian':[0,2,4,5,7,9,10],'majblues':[0,2,3,4,7,9]}
    ivs = types[a.type or ('minor' if minor else 'major')]
    lo, hi = map(int, a.frets.split('-')); tun = open_pcs(STD)
    print('fret ' + ''.join(f"{x:>4}" for x in range(lo, hi+1)))
    for s in range(5, -1, -1):
        row = ''
        for fr in range(lo, hi+1):
            iv = (tun[s] + fr - t) % 12
            row += f"{DEG[iv] if iv in ivs else '-':>4}"
        print(f"{'eBGDAE'[5-s]:>4} " + row)

def parse_tab(text):
    lines = [l for l in text.splitlines() if re.match(r'^\s*[eBGDAEbgda]\s*\|', l)]
    if len(lines) < 6: sys.exit('need 6 tab lines starting e| B| G| D| A| E|')
    events = []
    for block in range(0, len(lines) - len(lines) % 6, 6):
        grp = lines[block:block+6]; contents = [l.split('|', 1)[1] for l in grp]
        barcols = [i for i, ch in enumerate(contents[0]) if ch == '|']
        for si, c in enumerate(contents):
            string_idx = 5 - si  # 5 = high e
            i = 0
            while i < len(c):
                if c[i].isdigit():
                    j = i
                    while j < len(c) and c[j].isdigit() and j - i < 2: j += 1
                    fr = int(c[i:j])
                    if fr > 24: j = i + 1; fr = int(c[i])
                    bar = sum(1 for b in barcols if b < i)
                    events.append((block // 6, bar, i, string_idx, fr)); i = j
                else: i += 1
    return sorted(events)

def cmd_check(a):
    t, minor, root = parse_key(a.key); f = uses_flats(root, minor)
    text = sys.stdin.read() if a.file == '-' else open(a.file).read()
    tun = open_pcs(a.tuning.split(',') if a.tuning else STD)
    ev = parse_tab(text); sc = set(MIN if minor else MAJ); d = do_pc(t, minor)
    chords = a.chords.split() if a.chords else []
    nb = max((e[1] for e in ev if e[0] == 0), default=0) + 1
    out_key = 0; nonchord = 0
    print(f"Key {a.key}{' capo '+str(a.capo) if a.capo else ''} | {len(ev)} notes")
    for blk, bar, col, s, fr in ev:
        pc = (tun[s] + fr + a.capo) % 12; iv = (pc - t) % 12
        flag = '' if iv in sc else '  <- OUT OF KEY (fine only as a chromatic passing/approach note)'
        out_key += bool(flag)
        gbar = blk * nb + bar; ch = ''
        if chords:
            cname = chords[min(gbar, len(chords)-1)]; p = parse_chord(cname)
            if p:
                r, tones = p; rel = (pc - r) % 12
                if pc in tones: ch = f"  {cname}: chord tone ({CTNAME[rel]})"
                else: ch = f"  {cname}: tension/passing ({CTNAME[rel]})"; nonchord += 1
        print(f"  bar {gbar+1:>2} col {col:>3}  {'eBGDAE'[5-s]}{fr:<2} = {nm(pc,f):<2}  deg {DEG[iv]:<3} sol-fa {SOLFA[(pc-d)%12]:<3}{ch}{flag}")
    print(f"Summary: {out_key} out-of-key note(s)" + (f", {nonchord} non-chord tone(s) - make sure they resolve" if chords else ''))

COUNTS = {8: '1 & 2 & 3 & 4 &'.split(), 12: '1 + a 2 + a 3 + a 4 + a'.split(),
          16: '1 e & a 2 e & a 3 e & a 4 e & a'.split(), 6: '1 + a 2 + a'.split(), 4: '1 2 3 4'.split()}

def cmd_render(a):
    """spec: bars split by '|', steps split by spaces; step = '-' or notes joined by '+'.
    note = string letter (e B G D A E; e = high) + fret text, e.g. G7  B8  D5h7  e10b12  G7/9"""
    order = 'eBGDAE'; bars = [b.split() for b in a.spec.split('|') if b.strip()]
    chords = a.chords.split() if a.chords else []
    rows = {s: s + '|' for s in order}; count = '  '; chordline = '  '
    for bi, bar in enumerate(bars):
        if len(bar) != a.steps: sys.exit(f'bar {bi+1} has {len(bar)} steps, expected {a.steps}')
        start = len(rows['e'])
        for si, step in enumerate(bar):
            cells = {}
            if step != '-':
                for n in step.split('+'):
                    if n[0] not in order: sys.exit(f'bad note {n} (start with e B G D A E)')
                    cells[n[0]] = n[1:]
            w = max([len(v) for v in cells.values()] + [1]) + 1
            for s in order: rows[s] += '-' + cells.get(s, '').ljust(w - 1, '-')
            cnt = COUNTS.get(a.steps, [str(i+1) for i in range(a.steps)])[si]
            count += ' ' + cnt.ljust(w - 1)
        for s in order: rows[s] += '-|'
        count += '  '
        ch = chords[bi] if bi < len(chords) else ''
        chordline += ' ' * (start - len(chordline)) + ch
    if chords: print(chordline.rstrip())
    for s in order: print(rows[s])
    print(count.rstrip())

p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
sp = p.add_subparsers(dest='cmd', required=True)
x = sp.add_parser('key'); x.add_argument('key'); x.set_defaults(fn=cmd_key)
x = sp.add_parser('capo'); x.add_argument('key'); x.set_defaults(fn=cmd_capo)
x = sp.add_parser('nashville'); x.add_argument('numbers'); x.add_argument('--key', required=True); x.set_defaults(fn=cmd_nashville)
x = sp.add_parser('transpose'); x.add_argument('chords'); x.add_argument('--from', dest='frm', required=True); x.add_argument('--to', required=True); x.set_defaults(fn=cmd_transpose)
x = sp.add_parser('doublestops'); x.add_argument('key'); x.add_argument('--interval', type=int, choices=[3, 6], default=6)
x.add_argument('--strings', default='GE'); x.add_argument('--min-fret', type=int, default=0); x.set_defaults(fn=cmd_doublestops)
x = sp.add_parser('scale'); x.add_argument('key'); x.add_argument('--type'); x.add_argument('--frets', default='0-15'); x.set_defaults(fn=cmd_scale)
x = sp.add_parser('check'); x.add_argument('file'); x.add_argument('--key', required=True); x.add_argument('--chords')
x.add_argument('--capo', type=int, default=0); x.add_argument('--tuning', help='low->high, e.g. D,A,D,G,B,E'); x.set_defaults(fn=cmd_check)
x = sp.add_parser('render'); x.add_argument('spec'); x.add_argument('--steps', type=int, default=8); x.add_argument('--chords')
x.set_defaults(fn=cmd_render)
a = p.parse_args(); a.fn(a)
