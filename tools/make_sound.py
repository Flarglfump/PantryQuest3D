#!/usr/bin/env python3
"""Synthesises Pantry Quest 3D's sound effects (all original) into sfx/, at 22050 Hz.

    python3 tools/make_sound.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'lib'))
from synth import Track, tone  # noqa: E402

OUT = os.path.join(HERE, '..', 'sfx')
R = 22050


def sfx(name, seconds, parts):
    tr = Track(seconds, R)
    for start, samples in parts:
        tr.add(start, samples)
    tr.write(os.path.join(OUT, name + '.wav'))


def seq(notes, step, start=0.0, wave='square', **kw):
    parts, t = [], start
    for note, length in notes:
        if note is not None:
            parts.append((t, tone(R, note, length * step * 0.95, wave, **kw)))
        t += length * step
    return parts


def main():
    os.makedirs(OUT, exist_ok=True)
    sfx('swing', 0.16, [(0, tone(R, 900, 0.15, 'noise', vol=0.25, f1=3000, attack=0.03, decay=0.06))])
    sfx('spin', 0.5, [(0, tone(R, 600, 0.48, 'noise', vol=0.3, f1=4000, attack=0.05, decay=0.25)),
                      (0, tone(R, 300, 0.45, wave='triangle', vol=0.2, f1=900, vibrato=6, vib_delay=0))])
    sfx('hit', 0.14, [(0, tone(R, 'C3', 0.12, duty=0.25, vol=0.3, f1='G2')), (0, tone(R, 3000, 0.08, 'noise', vol=0.2, decay=0.02))])
    sfx('thunk', 0.12, [(0, tone(R, 180, 0.1, wave='triangle', vol=0.4, f1=90, decay=0.04)), (0, tone(R, 1200, 0.05, 'noise', vol=0.08, decay=0.01))])
    sfx('block', 0.2, [(0, tone(R, 1800, 0.18, duty=0.125, vol=0.2, decay=0.05)), (0, tone(R, 2700, 0.16, duty=0.125, vol=0.12, decay=0.05))])
    sfx('hurt', 0.32, [(0, tone(R, 'A4', 0.3, duty=0.5, vol=0.28, f1='C3')), (0, tone(R, 900, 0.2, 'noise', vol=0.15, decay=0.08))])
    sfx('dead', 1.2, seq([('E4', 1), ('C4', 1), ('A3', 1), ('F3', 3)], 0.16, duty=0.5, vol=0.25))
    sfx('defeat', 0.4, [(0, tone(R, 1200, 0.38, 'noise', vol=0.3, f1=150, decay=0.12)), (0.05, tone(R, 'E5', 0.3, duty=0.25, vol=0.15, f1='E3'))])
    sfx('roll', 0.3, [(0, tone(R, 300, 0.28, 'noise', vol=0.18, f1=900, decay=0.12))])
    sfx('hop', 0.12, [(0, tone(R, 300, 0.11, duty=0.25, vol=0.15, f1=650))])
    sfx('jumpatk', 0.3, [(0, tone(R, 250, 0.28, duty=0.25, vol=0.2, f1=900)), (0, tone(R, 900, 0.2, 'noise', vol=0.15, f1=3000))])
    sfx('land', 0.15, [(0, tone(R, 120, 0.14, wave='triangle', vol=0.4, f1=50, decay=0.05)), (0, tone(R, 800, 0.1, 'noise', vol=0.15, decay=0.03))])
    sfx('bonk', 0.25, [(0, tone(R, 140, 0.22, wave='triangle', vol=0.5, f1=60, decay=0.08)), (0, tone(R, 600, 0.15, 'noise', vol=0.2, decay=0.05))])
    sfx('cut', 0.15, [(0, tone(R, 4000, 0.13, 'noise', vol=0.22, decay=0.04)), (0, tone(R, 1400, 0.1, duty=0.125, vol=0.06, f1=700))])
    sfx('smash', 0.35, [(0, tone(R, 2500, 0.3, 'noise', vol=0.35, f1=800, decay=0.08)),
                        (0.03, tone(R, 3200, 0.2, 'noise', vol=0.2, decay=0.05))])
    sfx('bean', 0.2, seq([('E6', 1), ('B6', 2)], 0.05, duty=0.25, vol=0.16))
    sfx('heart', 0.3, seq([('C6', 1), ('E6', 1), ('G6', 2)], 0.06, wave='triangle', vol=0.3))
    sfx('focus', 0.12, [(0, tone(R, 'A5', 0.1, duty=0.25, vol=0.12, f1='E6'))])
    sfx('blip', 0.04, [(0, tone(R, 'C6', 0.035, duty=0.25, vol=0.08))])
    sfx('cursor', 0.06, [(0, tone(R, 'G5', 0.05, duty=0.25, vol=0.12))])
    sfx('select', 0.15, seq([('C6', 1), ('G6', 2)], 0.04, duty=0.25, vol=0.14))
    sfx('menu', 0.2, seq([('G5', 1), ('C6', 1), ('E6', 2)], 0.04, wave='triangle', vol=0.25))
    sfx('page', 0.1, [(0, tone(R, 2000, 0.08, 'noise', vol=0.1, f1=600, decay=0.03))])
    sfx('save', 0.6, seq([('C5', 1), ('E5', 1), ('G5', 1), ('C6', 3)], 0.08, wave='triangle', vol=0.3))
    sfx('empty', 0.15, [(0, tone(R, 200, 0.12, duty=0.5, vol=0.15))])
    sfx('pea', 0.12, [(0, tone(R, 700, 0.1, duty=0.25, vol=0.2, f1=1400)), (0, tone(R, 2000, 0.05, 'noise', vol=0.08, decay=0.02))])
    sfx('tick', 0.06, [(0, tone(R, 2500, 0.05, 'noise', vol=0.15, decay=0.015))])
    sfx('spit', 0.12, [(0, tone(R, 500, 0.1, duty=0.5, vol=0.18, f1=250)), (0, tone(R, 1500, 0.06, 'noise', vol=0.1, decay=0.02))])
    sfx('pop', 0.15, [(0, tone(R, 300, 0.12, duty=0.25, vol=0.16, f1=900))])
    sfx('lunge', 0.2, [(0, tone(R, 200, 0.18, duty=0.25, vol=0.15, f1=500)), (0, tone(R, 1000, 0.15, 'noise', vol=0.08))])
    sfx('ignite', 0.4, [(0, tone(R, 300, 0.38, 'noise', vol=0.3, f1=2000, decay=0.2))])
    sfx('door', 0.4, [(0, tone(R, 160, 0.38, duty=0.5, vol=0.15, f1=90)), (0, tone(R, 800, 0.35, 'noise', vol=0.08, decay=0.15))])
    sfx('rumble', 1.4, [(0, tone(R, 60, 1.38, 'noise', vol=0.4, decay=0.6)), (0, tone(R, 50, 1.3, wave='triangle', vol=0.4, f1=35, decay=0.7))])
    sfx('chest', 0.7, [(0, tone(R, 150, 0.3, duty=0.5, vol=0.15, f1=260))] + seq([(None, 3), ('C5', 1), ('D5', 1), ('E5', 1), ('G5', 3)], 0.05, duty=0.25, vol=0.12))
    sfx('secret', 1.0, seq([('G5', 1), ('F#5', 1), ('D#5', 1), ('A4', 1), ('G#4', 1), ('E5', 1), ('G#5', 1), ('C6', 3)], 0.09, duty=0.25, vol=0.13))
    # the item fanfare: a little rising flourish and a held chord
    fan = seq([('G4', 1), ('C5', 1), ('E5', 1), ('G5', 2), ('E5', 1), ('G5', 4)], 0.11, duty=0.25, vol=0.16, vibrato=2)
    fan += seq([('C4', 1), ('E4', 1), ('G4', 1), ('C5', 2), ('G4', 1), ('C5', 4)], 0.11, wave='triangle', vol=0.3)
    sfx('fanfare', 1.4, fan)
    sfx('boss_roar', 1.0, [(0, tone(R, 120, 0.95, 'saw', vol=0.25, f1=60, vibrato=8, vib_delay=0)), (0, tone(R, 600, 0.9, 'noise', vol=0.2, decay=0.4))])
    sfx('screech', 0.5, [(0, tone(R, 1800, 0.45, duty=0.125, vol=0.18, f1=900, vibrato=10, vib_delay=0))])
    sfx('switch', 0.25, seq([('C6', 1), ('G6', 1)], 0.06, duty=0.25, vol=0.15))
    sfx('burn', 0.8, [(0, tone(R, 400, 0.78, 'noise', vol=0.3, f1=3000, decay=0.3))])
    sfx('splash', 0.4, [(0, tone(R, 1500, 0.35, 'noise', vol=0.3, f1=400, decay=0.12))])
    sfx('warp', 1.6, seq([('C5', 1), ('E5', 1), ('G5', 1), ('C6', 1), ('E6', 1), ('G6', 1), ('C7', 4)], 0.12, wave='triangle', vol=0.25, vibrato=3))
    sfx('step', 0.08, [(0, tone(R, 300, 0.07, 'noise', vol=0.08, decay=0.02))])
    sfx('grow', 0.5, [(0, tone(R, 200, 0.45, wave='triangle', vol=0.3, f1=600))])
    sfx('blast', 0.6, [(0, tone(R, 900, 0.58, 'noise', vol=0.5, f1=80, decay=0.18)), (0, tone(R, 110, 0.4, wave='triangle', vol=0.5, f1=35, decay=0.12))])
    sfx('crumble', 0.5, [(0, tone(R, 700, 0.48, 'noise', vol=0.4, f1=120, decay=0.15))])
    sfx('sizzle', 0.4, [(0, tone(R, 5000, 0.38, 'noise', vol=0.25, decay=0.15))])
    sfx('song', 0.1, [(0, tone(R, 'A5', 0.08, wave='triangle', vol=0.2))])
    print('sounds written')


if __name__ == '__main__':
    main()
