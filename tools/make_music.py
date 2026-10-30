#!/usr/bin/env python3
"""Pantry Quest 3D's music (all original), played on the chip synthesiser in lib/synth.py:
a pulse lead (with an echo), a second pulse for harmony, a triangle bass and noise drums.
Each track is a loop.

    python3 tools/make_music.py

A part is written as "note:beats" words ("r" is a rest): "C5:1 E5:0.5 r:0.5".
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'lib'))
from synth import Track, tone, drum  # noqa: E402

OUT = os.path.join(HERE, '..', 'music')
R = 22050


def parse(text):
    out = []
    for w in text.split():
        n, b = w.split(':')
        out.append((None if n == 'r' else n, float(b)))
    return out


def beats(part):
    return sum(b for _, b in part)


def song(name, bpm, parts, drums='', loop=True, echo=0.25):
    """parts: [(text, wave, duty, vol, extra)], drums: 'k h s h ...' a step per 16th."""
    beat = 60.0 / bpm
    length = max(beats(parse(p[0])) for p in parts)
    tr = Track(length * beat, R)
    for text, wave, duty, vol, kw in parts:
        t = 0.0
        for note, b in parse(text):
            if note:
                d = b * beat
                s = tone(R, note, d * 0.92, wave, duty=duty, vol=vol, **kw)
                if loop:
                    tr.add_wrapped(t, s)
                else:
                    tr.add(t, s)
            t += b * beat
    if drums:
        steps = drums.split()
        step = beat / 4
        n = int(length * 4)
        for i in range(n):
            k = steps[i % len(steps)]
            if k != '.':
                kind = {'k': 'kick', 's': 'snare', 'h': 'hat', 'c': 'crash'}[k]
                tr.add_wrapped(i * step, drum(R, kind, 0.22)) if loop else tr.add(i * step, drum(R, kind, 0.22))
    if echo:
        tr.echo(beat * 0.75, echo, wrapped=loop)
    tr.write(os.path.join(OUT, name + '.wav'), 0.8)


LEAD = dict(vibrato=1.5, release=0.03)


def main():
    os.makedirs(OUT, exist_ok=True)
    # ---- Sprouthollow: a lilting village tune in F (3/4 feel written in 4) ----
    lead = ('F5:1 A5:1 C6:1.5 A5:0.5 G5:1 F5:1 E5:1 G5:1 '
            'F5:1 A5:1 C6:1.5 D6:0.5 C6:1 A5:1 G5:2 '
            'Bb5:1 D6:1 C6:1 A5:1 G5:1 Bb5:1 A5:1 F5:1 '
            'G5:1 A5:0.5 G5:0.5 F5:1 E5:1 F5:4 '
            'A5:1 G5:1 F5:1 G5:1 A5:1.5 C6:0.5 A5:2 '
            'G5:1 F5:1 E5:1 F5:1 G5:3 r:1 '
            'D6:1 C6:1 Bb5:1 A5:1 G5:1 A5:1 Bb5:2 '
            'A5:1 G5:1 E5:1 G5:1 F5:4')
    harm = ('C5:2 F5:2 E5:2 C5:2 C5:2 F5:2 E5:4 D5:2 F5:2 E5:2 C5:2 E5:2 C5:2 A4:4 '
            'C5:2 E5:2 F5:2 C5:2 E5:2 C5:2 E5:4 F5:2 D5:2 E5:2 F5:2 E5:2 C5:2 A4:4')
    bass = ' '.join(['F3:1 C4:1 A3:1 C4:1'] * 2 + ['C3:1 G3:1 E3:1 G3:1'] * 2 + ['Bb2:1 F3:1 D3:1 F3:1', 'C3:1 G3:1 E3:1 G3:1',
                    'F3:1 C4:1 A3:1 C4:1', 'F3:2 C3:2'] + ['F3:1 C4:1 A3:1 C4:1', 'C3:1 G3:1 E3:1 G3:1'] * 2
                   + ['Bb2:1 F3:1 D3:1 F3:1', 'Bb2:1 F3:1 D3:1 F3:1', 'C3:1 G3:1 E3:1 G3:1', 'F3:2 C3:2'])
    song('sprouthollow', 116, [(lead, 'square', 0.25, 0.16, LEAD), (harm, 'square', 0.5, 0.06, {}), (bass, 'triangle', 0.5, 0.3, {})],
         drums='k . h . s . h . k . h h s . h .')
    # ---- The Great Crock: low, bubbling, a little uneasy (D minor) ----
    lead = ('D5:2 r:1 F5:1 E5:2 r:1 C5:1 D5:3 A4:1 Bb4:2 A4:2 '
            'D5:2 r:1 F5:1 G5:2 F5:1 E5:1 F5:3 E5:1 C#5:4 '
            'A5:2 G5:1 F5:1 E5:2 F5:1 G5:1 A5:3 Bb5:1 A5:2 G5:2 '
            'F5:2 E5:1 D5:1 C#5:2 E5:2 D5:6 r:2')
    bub = ' '.join(['A5:0.25 r:0.75 D6:0.25 r:1.75 F6:0.25 r:0.75'] * 16)
    bass = ' '.join(['D3:2 A2:2'] * 3 + ['Bb2:2 A2:2'] + ['D3:2 A2:2', 'G2:2 A2:2', 'D3:2 A2:2', 'A2:4']
                    + ['F2:2 C3:2', 'C3:2 G2:2', 'F2:2 C3:2', 'Bb2:2 C3:2', 'Bb2:2 A2:2', 'A2:4', 'D3:2 A2:2', 'D3:4'])
    song('crock', 88, [(lead, 'square', 0.125, 0.11, LEAD), (bub, 'triangle', 0.5, 0.12, {}), (bass, 'triangle', 0.5, 0.32, {})],
         drums='k . . . . . h . . . k . . . h .', echo=0.35)
    # ---- the boss: driving E minor ----
    lead = ('E5:0.5 E5:0.5 G5:0.5 E5:0.5 B5:1 A5:1 G5:0.5 F#5:0.5 E5:0.5 F#5:0.5 G5:2 '
            'E5:0.5 E5:0.5 G5:0.5 E5:0.5 C6:1 B5:1 A5:0.5 G5:0.5 F#5:0.5 G5:0.5 A5:2 '
            'B5:1 C6:0.5 B5:0.5 A5:1 G5:1 F#5:1 G5:0.5 F#5:0.5 E5:1 D#5:1 '
            'E5:1 F#5:1 G5:1 A5:1 B5:4')
    bass = ' '.join(['E2:0.5 E3:0.5'] * 8 + ['C2:0.5 C3:0.5'] * 4 + ['D2:0.5 D3:0.5'] * 4
                    + ['A1:0.5 A2:0.5'] * 4 + ['B1:0.5 B2:0.5'] * 4 + ['E2:0.5 E3:0.5'] * 4 + ['B1:0.5 B2:0.5'] * 4)
    song('boss', 152, [(lead, 'square', 0.25, 0.14, LEAD), (bass, 'triangle', 0.5, 0.34, {})],
         drums='k . h k s . h . k k h . s . h h')
    # ---- the title: gentle, hopeful (C major) ----
    lead = ('E5:2 G5:1 C6:1 B5:2 G5:2 A5:2 F5:1 A5:1 G5:4 '
            'E5:2 G5:1 C6:1 D6:2 C6:1 B5:1 A5:2 B5:1 G5:1 C6:4 '
            'F5:2 A5:1 C6:1 B5:2 G5:2 A5:1 G5:1 F5:1 E5:1 D5:4 '
            'E5:2 G5:1 C6:1 E6:2 D6:1 C6:1 B5:2 D6:2 C6:4')
    harm = 'C5:4 D5:4 C5:4 B4:4 C5:4 F5:4 F5:4 E5:4 A4:4 B4:4 C5:4 B4:4 C5:4 G4:4 G4:4 E5:4'
    bass = 'C3:4 G2:4 F2:4 G2:4 C3:4 G2:4 F2:4 C3:4 F2:4 G2:4 A2:4 G2:4 C3:4 E3:4 G2:4 C3:4'
    song('title', 92, [(lead, 'square', 0.25, 0.14, LEAD), (harm, 'triangle', 0.5, 0.12, {}), (bass, 'triangle', 0.5, 0.3, {})],
         drums='k . . . h . . . s . . . h . . .')
    # ---- Breadbasket Fields: an open, striding tune in D (the road ahead) ----
    lead = ('D5:1.5 A4:0.5 D5:1 F#5:1 E5:1.5 D5:0.5 E5:1 A5:1 '
            'G5:1.5 F#5:0.5 E5:1 D5:1 E5:3 A4:1 '
            'D5:1.5 A4:0.5 D5:1 F#5:1 A5:1.5 B5:0.5 A5:1 F#5:1 '
            'G5:1 F#5:1 E5:1 C#5:1 D5:4 '
            'B5:1.5 A5:0.5 G5:1 F#5:1 G5:1.5 F#5:0.5 E5:2 '
            'A5:1.5 G5:0.5 F#5:1 E5:1 F#5:3 r:1 '
            'G5:1 A5:1 B5:1 G5:1 F#5:1 G5:1 A5:2 '
            'E5:1 F#5:1 G5:1 E5:1 D5:4')
    harm = ('F#4:2 A4:2 G4:2 C#5:2 B4:2 A4:2 G4:4 F#4:2 A4:2 C#5:2 D5:2 B4:2 G4:2 F#4:4 '
            'D5:2 B4:2 B4:2 G4:2 C#5:2 A4:2 A4:4 B4:2 D5:2 A4:2 F#4:2 G4:2 C#5:2 F#4:4')
    bass = ' '.join(['D3:1 A3:1 F#3:1 A3:1', 'A2:1 E3:1 C#3:1 E3:1', 'G2:1 D3:1 B2:1 D3:1', 'A2:1 E3:1 C#3:1 E3:1',
                     'D3:1 A3:1 F#3:1 A3:1', 'F#2:1 C#3:1 A2:1 C#3:1', 'G2:1 D3:1 A2:1 E3:1', 'D3:2 A2:2',
                     'G2:1 D3:1 B2:1 D3:1', 'E2:1 B2:1 G2:1 B2:1', 'A2:1 E3:1 C#3:1 E3:1', 'F#2:1 C#3:1 A2:1 C#3:1',
                     'G2:1 D3:1 B2:1 D3:1', 'A2:1 E3:1 C#3:1 E3:1', 'G2:1 D3:1 A2:1 E3:1', 'D3:2 A2:2'])
    song('fields', 126, [(lead, 'square', 0.25, 0.15, LEAD), (harm, 'square', 0.5, 0.055, {}), (bass, 'triangle', 0.5, 0.3, {})],
         drums='k . h . s . h k k . h . s . h h')
    # ---- Larder Town: a busy market jig in G ----
    lead = ('G5:0.5 B5:0.5 D6:1 B5:0.5 G5:0.5 A5:1 F#5:0.5 A5:0.5 C6:1 A5:0.5 F#5:0.5 G5:2 '
            'E5:0.5 G5:0.5 B5:1 A5:0.5 G5:0.5 F#5:0.5 E5:0.5 D5:1 G5:0.5 F#5:0.5 E5:0.5 D5:0.5 D5:2 '
            'G5:0.5 B5:0.5 D6:1 E6:0.5 D6:0.5 C6:1 B5:0.5 C6:0.5 D6:1 B5:0.5 G5:0.5 A5:2 '
            'C6:0.5 B5:0.5 A5:0.5 G5:0.5 F#5:1 A5:1 G5:1 D5:1 G5:2')
    bass = ' '.join(['G2:1 D3:1'] * 2 + ['D2:1 A2:1'] * 2 + ['C3:1 G2:1', 'D3:1 A2:1', 'G2:1 D3:1', 'G2:1 D3:1']
                    + ['G2:1 D3:1'] * 2 + ['C3:1 G2:1'] * 2 + ['D3:1 A2:1'] * 2 + ['G2:1 D3:1', 'G2:2'])
    song('town', 132, [(lead, 'square', 0.25, 0.14, LEAD), (bass, 'triangle', 0.5, 0.3, {})], drums='k . h . s . h . k k h . s . h .')
    # ---- the castle garden: sneaking, pizzicato, in A minor ----
    lead = ('A4:0.5 r:0.5 C5:0.5 r:0.5 E5:0.5 r:0.5 D5:0.5 C5:0.5 B4:0.5 r:0.5 D5:0.5 r:0.5 G4:1 r:1 '
            'A4:0.5 r:0.5 C5:0.5 r:0.5 E5:0.5 r:0.5 F5:0.5 E5:0.5 D5:0.5 r:0.5 B4:0.5 r:0.5 E5:1 r:1 '
            'F5:0.5 r:0.5 E5:0.5 r:0.5 D5:0.5 r:0.5 C5:0.5 B4:0.5 C5:0.5 r:0.5 A4:0.5 r:0.5 B4:1 r:1 '
            'C5:0.5 D5:0.5 E5:0.5 r:0.5 G#4:0.5 r:0.5 B4:0.5 r:0.5 A4:2 r:2')
    bass = ' '.join(['A2:0.5 r:0.5'] * 4 + ['G2:0.5 r:0.5'] * 4 + ['A2:0.5 r:0.5'] * 4 + ['E2:0.5 r:0.5'] * 4
                    + ['F2:0.5 r:0.5'] * 4 + ['E2:0.5 r:0.5'] * 4 + ['A2:0.5 r:0.5'] * 2 + ['E2:0.5 r:0.5'] * 2 + ['A2:0.5 r:0.5'] * 4)
    song('castle', 100, [(lead, 'square', 0.125, 0.13, {'release': 0.02}), (bass, 'triangle', 0.5, 0.3, {})],
         drums='. . h . . . h . . . h . . . h h', echo=0.2)
    # ---- Peppermill: a gentle waltz-like turn in F, the windmill going round ----
    lead = ('C5:1 F5:1 A5:1 G5:1 F5:1 E5:1 F5:2 C5:2 D5:1 E5:1 F5:1 G5:1 A5:1 G5:3 r:1 '
            'A5:1 Bb5:1 C6:1 A5:1 G5:1 F5:1 G5:2 E5:2 F5:1 G5:1 A5:1 G5:1 E5:1 F5:3 r:1')
    bass = 'F3:2 C3:2 F3:2 C3:2 Bb2:2 F3:2 C3:2 C3:2 F3:2 A2:2 Bb2:2 G2:2 C3:2 C3:2 F3:2 F3:2'
    song('peppermill', 104, [(lead, 'square', 0.25, 0.13, LEAD), (bass, 'triangle', 0.5, 0.3, {})], drums='k . . . h . . . s . . . h . h .')
    # ---- Mount Fondue: heavy, rumbling, in C minor ----
    lead = ('C5:1.5 Eb5:0.5 G5:1 F5:1 Eb5:1 D5:1 C5:2 Ab4:1.5 C5:0.5 Eb5:1 D5:1 G4:4 '
            'C5:1.5 Eb5:0.5 G5:1 Ab5:1 G5:1 F5:1 Eb5:2 F5:1 Eb5:1 D5:1 B4:1 C5:4')
    bass = ' '.join(['C2:0.5 C3:0.5'] * 8 + ['Ab1:0.5 Ab2:0.5'] * 4 + ['G1:0.5 G2:0.5'] * 4 + ['C2:0.5 C3:0.5'] * 8
                    + ['F1:0.5 F2:0.5'] * 2 + ['G1:0.5 G2:0.5'] * 2 + ['C2:0.5 C3:0.5'] * 4)
    song('fondue', 112, [(lead, 'square', 0.5, 0.12, LEAD), (bass, 'triangle', 0.5, 0.34, {})], drums='k . . k s . . . k . k . s . . h')
    # ---- Hardtack Caverns: hot and driving, in E Phrygian ----
    lead = ('E5:0.5 F5:0.5 E5:1 r:0.5 B4:0.5 C5:1 D5:0.5 C5:0.5 B4:1 A4:1 B4:1 '
            'E5:0.5 F5:0.5 G5:1 r:0.5 F5:0.5 E5:1 D5:0.5 E5:0.5 F5:1 E5:2')
    bass = ' '.join(['E2:0.5 r:0.5 E2:0.5 F2:0.5'] * 4 + ['D2:0.5 r:0.5 D2:0.5 E2:0.5'] * 2 + ['E2:0.5 r:0.5 E2:0.5 F2:0.5'] * 2)
    song('caverns', 120, [(lead, 'square', 0.25, 0.11, LEAD), (bass, 'triangle', 0.5, 0.34, {})], drums='k . h k s . h . k . h k s . h h', echo=0.3)
    # ---- game over ----
    song('gameover', 70, [('E5:1 D5:1 C5:1 B4:1 A4:2 C5:2 B4:4 r:4', 'square', 0.25, 0.14, LEAD),
                          ('A3:4 F3:4 E3:4 r:4', 'triangle', 0.5, 0.3, {})], loop=False, echo=0.3)
    print('music written')


if __name__ == '__main__':
    main()
