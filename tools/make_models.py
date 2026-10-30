#!/usr/bin/env python3
"""Makes Pantry Quest 3D's characters: blocky figures with skeletons and animations
(glTF .glb, through lib/gltf_writer.py), and the few static models (.obj).

    python3 tools/make_models.py

Every figure faces -z (Bronto's forward), so it needs no turning in the game.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'lib'))
from gltf_writer import Model  # noqa: E402
from kit import path, Obj  # noqa: E402


def qmul(a, b):
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return (aw * bx + ax * bw + ay * bz - az * by,
            aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw,
            aw * bw - ax * bx - ay * by - az * bz)


def R(x=0, y=0, z=0):
    """A rotation: about y, then x, then z (degrees), as a quaternion (x, y, z, w)."""
    def axis(ax, d):
        h = math.radians(d) / 2
        s, c = math.sin(h), math.cos(h)
        return {'x': (s, 0, 0, c), 'y': (0, s, 0, c), 'z': (0, 0, s, c)}[ax]
    return qmul(qmul(axis('y', y), axis('x', x)), axis('z', z))


def hexc(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def cycle(n, length, fn):
    """Keyframes 0..length from fn(phase 0..1) -> rotation."""
    return [(length * i / n, fn(i / n)) for i in range(n + 1)]


def figure(s=1.0, skin='#f2c9a0', shirt='#5fa04a', trousers='#7a5a3a', shoes='#5a3a20', hair='#7a4a22',
           hat=None, hat_kind='leaf', apron=None, eyes='#2a1a10', girl=False, belly=0.0, big_head=1.0):
    """A child-proportioned blocky figure about 1.1 * s tall (feet at y 0). Returns (model, bones)."""
    m = Model()
    S = lambda *v: tuple(c * s for c in v)
    hips = m.bone('hips', S(0, 0.5, 0))
    spine = m.bone('spine', S(0, 0.56, 0), hips)
    head = m.bone('head', S(0, 0.82, 0), spine)
    b = {'hips': hips, 'spine': spine, 'head': head}
    for side, x in (('l', 1), ('r', -1)):
        b['arm_' + side] = m.bone('arm_' + side, S(0.17 * x, 0.8, 0), spine)
        b['hand_' + side] = m.bone('hand_' + side, S(0.17 * x, 0.62, 0), b['arm_' + side])
        b['leg_' + side] = m.bone('leg_' + side, S(0.08 * x, 0.48, 0), hips)
        b['shin_' + side] = m.bone('shin_' + side, S(0.08 * x, 0.25, 0), b['leg_' + side])
    C = hexc
    bw = 0.13 + belly
    m.box(S(-bw, 0.44, -0.09 - belly), S(bw, 0.56, 0.09), hips, C(trousers))
    m.box(S(-bw, 0.54, -0.1 - belly), S(bw, 0.84, 0.1), spine, C(shirt))
    if apron:
        m.box(S(-0.11, 0.42, -0.115 - belly), S(0.11, 0.78, -0.1 - belly), spine, C(apron))
    hs = big_head
    m.box(S(-0.14 * hs, 0.82, -0.13 * hs), S(0.14 * hs, 0.82 + 0.26 * hs, 0.13 * hs), head, C(skin))
    top = 0.82 + 0.26 * hs
    m.box(S(-0.15 * hs, top - 0.08, -0.1 * hs), S(0.15 * hs, top + 0.03, 0.14 * hs), head, C(hair))     # hair
    m.box(S(-0.145 * hs, 0.86, 0.1 * hs), S(0.145 * hs, top - 0.05, 0.14 * hs), head, C(hair))           # (round the back)
    if girl:
        m.box(S(-0.16 * hs, top - 0.28, 0.0), S(0.16 * hs, top - 0.02, 0.15 * hs), head, C(hair))
    ey = 0.82 + 0.13 * hs
    for x in (-1, 1):
        m.box(S(0.05 * x * hs - 0.025, ey, -0.135 * hs), S(0.05 * x * hs + 0.025, ey + 0.05, -0.125 * hs), head, C(eyes))
    if hat:
        if hat_kind == 'leaf':          # a leafy cap: a flat leaf, its tip falling back
            m.box(S(-0.16 * hs, top, -0.15 * hs), S(0.16 * hs, top + 0.05, 0.16 * hs), head, C(hat))
            m.box(S(-0.07 * hs, top + 0.02, 0.1 * hs), S(0.07 * hs, top + 0.07, 0.3 * hs), head, C(hat))
            m.box(S(-0.02, top + 0.05, -0.05), S(0.02, top + 0.16, -0.01), head, C('#4a7a2a'))          # its stalk
        elif hat_kind == 'tall':        # a chef's hat
            m.box(S(-0.13 * hs, top, -0.13 * hs), S(0.13 * hs, top + 0.22, 0.13 * hs), head, C(hat))
        elif hat_kind == 'helmet':      # a guard's steel cap with a crest
            m.box(S(-0.16 * hs, top - 0.1, -0.16 * hs), S(0.16 * hs, top + 0.08, 0.16 * hs), head, C(hat))
            m.box(S(-0.025, top + 0.05, -0.12), S(0.025, top + 0.2, 0.14), head, C('#c03030'))
        elif hat_kind == 'tiara':       # a princess's gold band
            m.box(S(-0.155 * hs, top - 0.06, -0.155 * hs), S(0.155 * hs, top - 0.01, 0.155 * hs), head, C(hat))
            m.box(S(-0.03, top - 0.01, -0.16 * hs), S(0.03, top + 0.06, -0.14 * hs), head, C('#e04060'))
        elif hat_kind == 'bun':         # an old nanny's grey bun
            m.box(S(-0.08, top - 0.02, 0.02), S(0.08, top + 0.12, 0.18), head, C(hat))
        elif hat_kind == 'spiky':       # Chive's red sprout
            for k in range(4):
                a = k * math.pi / 2 + 0.4
                cx, cz = math.cos(a) * 0.07, math.sin(a) * 0.07
                m.box(S(cx - 0.03, top, cz - 0.03), S(cx + 0.03, top + 0.18, cz + 0.03), head, C(hat))
    for side, x in (('l', 1), ('r', -1)):
        cx = 0.17 * x
        m.box(S(cx - 0.045, 0.6, -0.045), S(cx + 0.045, 0.82, 0.045), b['arm_' + side], C(shirt))
        m.box(S(cx - 0.04, 0.44, -0.04), S(cx + 0.04, 0.62, 0.04), b['hand_' + side], C(skin))
        lx = 0.08 * x
        m.box(S(lx - 0.055, 0.26, -0.055), S(lx + 0.055, 0.48, 0.055), b['leg_' + side], C(trousers))
        m.box(S(lx - 0.05, 0.05, -0.05), S(lx + 0.05, 0.27, 0.05), b['shin_' + side], C(trousers))
        m.box(S(lx - 0.055, 0.0, -0.11), S(lx + 0.055, 0.07, 0.06), b['shin_' + side], C(shoes))
    return m, b


def standard_anims(m, b, s=1.0, hero=False):
    """idle, walk, run, talk, wave, hold (an item over the head), hurt, plus the hero's own."""
    m.animation('idle', rotations={
        b['arm_l']: [(0, R(z=5)), (1, R(z=8)), (2, R(z=5))],
        b['arm_r']: [(0, R(z=-5)), (1, R(z=-8)), (2, R(z=-5))],
        b['head']: [(0, R()), (1, R(x=-4)), (2, R())]},
        translations={b['hips']: [(0, (0, 0, 0)), (1, (0, 0.012 * s, 0)), (2, (0, 0, 0))]})

    def stride(name, length, leg, knee, arm, bob):
        m.animation(name, rotations={
            b['leg_l']: cycle(8, length, lambda p: R(x=leg * math.sin(2 * math.pi * p))),
            b['leg_r']: cycle(8, length, lambda p: R(x=-leg * math.sin(2 * math.pi * p))),
            b['shin_l']: cycle(8, length, lambda p: R(x=-knee * max(0, math.sin(2 * math.pi * p - math.pi / 2)))),
            b['shin_r']: cycle(8, length, lambda p: R(x=-knee * max(0, math.sin(2 * math.pi * p + math.pi / 2)))),
            b['arm_l']: cycle(8, length, lambda p: R(x=-arm * math.sin(2 * math.pi * p), z=6)),
            b['arm_r']: cycle(8, length, lambda p: R(x=arm * math.sin(2 * math.pi * p), z=-6)),
            b['spine']: [(0, R(x=-6 if bob > 0.03 else 0)), (length, R(x=-6 if bob > 0.03 else 0))]},
            translations={b['hips']: cycle(8, length, lambda p: (0, bob * s * abs(math.cos(2 * math.pi * p)) - bob * s / 2, 0))})
    stride('walk', 0.9, 28, 35, 24, 0.02)
    stride('run', 0.5, 45, 70, 50, 0.05)
    m.animation('talk', rotations={
        b['head']: [(0, R()), (0.2, R(x=-8)), (0.4, R(x=3)), (0.6, R(x=-6)), (0.8, R())],
        b['arm_r']: [(0, R(z=-5)), (0.4, R(x=40, z=-20)), (0.8, R(z=-5))]})
    m.animation('wave', rotations={
        b['arm_r']: [(0, R(z=-150)), (0.25, R(z=-120)), (0.5, R(z=-150))],
        b['hand_r']: [(0, R(z=-20)), (0.25, R(z=20)), (0.5, R(z=-20))]})
    m.animation('hold', rotations={
        b['arm_l']: [(0, R(z=165)), (1, R(z=165))], b['arm_r']: [(0, R(z=-165)), (1, R(z=-165))],
        b['head']: [(0, R(x=-15)), (1, R(x=-15))]})
    m.animation('hurt', rotations={
        b['spine']: [(0, R(x=20)), (0.3, R(x=10))], b['head']: [(0, R(x=20)), (0.3, R())],
        b['arm_l']: [(0, R(x=-40, z=40)), (0.3, R(z=10))], b['arm_r']: [(0, R(x=-40, z=-40)), (0.3, R(z=-10))]})
    if not hero:
        return
    # the hero's moves. The weapon is its own entity, swung by sprig.bs in time with these.
    m.animation('slash', rotations={       # right arm from the right shoulder across to the left
        b['arm_r']: [(0, R(x=60, y=0, z=-80)), (0.08, R(x=85, z=-60)), (0.18, R(x=80, z=40)), (0.3, R(x=40, z=10))],
        b['spine']: [(0, R(y=-30)), (0.1, R(y=-10)), (0.2, R(y=30)), (0.3, R(y=10))],
        b['arm_l']: [(0, R(x=40, z=20)), (0.3, R(x=30, z=10))],
        b['leg_l']: [(0, R(x=25)), (0.3, R(x=20))], b['leg_r']: [(0, R(x=-20)), (0.3, R(x=-15))]})
    m.animation('slash2', rotations={      # back the other way
        b['arm_r']: [(0, R(x=80, z=40)), (0.08, R(x=85, z=10)), (0.18, R(x=70, z=-70)), (0.3, R(x=40, z=-40))],
        b['spine']: [(0, R(y=30)), (0.1, R(y=10)), (0.2, R(y=-30)), (0.3, R(y=-10))],
        b['leg_l']: [(0, R(x=25)), (0.3, R(x=20))], b['leg_r']: [(0, R(x=-20)), (0.3, R(x=-15))]})
    m.animation('thrust', rotations={      # straight ahead
        b['arm_r']: [(0, R(x=40, z=-10)), (0.1, R(x=95)), (0.3, R(x=70))],
        b['spine']: [(0, R(x=0)), (0.1, R(x=-10)), (0.3, R(x=-4))],
        b['leg_l']: [(0, R(x=10)), (0.1, R(x=35)), (0.3, R(x=25))], b['leg_r']: [(0, R()), (0.1, R(x=-25)), (0.3, R(x=-15))]})
    m.animation('charge', rotations={      # arm back, ready to spin
        b['arm_r']: [(0, R(x=50, z=-90)), (1, R(x=50, z=-95))], b['spine']: [(0, R(y=-45)), (1, R(y=-48))],
        b['leg_l']: [(0, R(x=30)), (1, R(x=30))], b['leg_r']: [(0, R(x=-25)), (1, R(x=-25))],
        b['shin_l']: [(0, R(x=-30)), (1, R(x=-30))]})
    m.animation('spin', rotations={
        b['arm_r']: [(0, R(x=85, z=-80)), (0.5, R(x=85, z=-80))], b['arm_l']: [(0, R(x=20, z=60)), (0.5, R(x=20, z=60))],
        b['spine']: [(0, R(y=0)), (0.5, R(y=0))]})
    m.animation('roll', rotations={        # tuck: the script turns the whole body over
        b['spine']: [(0, R(x=60)), (0.4, R(x=60))], b['head']: [(0, R(x=40)), (0.4, R(x=40))],
        b['leg_l']: [(0, R(x=110)), (0.4, R(x=110))], b['leg_r']: [(0, R(x=110)), (0.4, R(x=110))],
        b['shin_l']: [(0, R(x=-140)), (0.4, R(x=-140))], b['shin_r']: [(0, R(x=-140)), (0.4, R(x=-140))],
        b['arm_l']: [(0, R(x=70)), (0.4, R(x=70))], b['arm_r']: [(0, R(x=70)), (0.4, R(x=70))]},
        translations={b['hips']: [(0, (0, -0.25 * s, 0)), (0.4, (0, -0.25 * s, 0))]})
    m.animation('jump', rotations={
        b['leg_l']: [(0, R()), (0.15, R(x=60))], b['leg_r']: [(0, R()), (0.15, R(x=10))],
        b['shin_l']: [(0, R()), (0.15, R(x=-80))], b['shin_r']: [(0, R()), (0.15, R(x=-30))],
        b['arm_l']: [(0, R()), (0.15, R(x=-30, z=60))], b['arm_r']: [(0, R()), (0.15, R(x=-30, z=-60))]})
    m.animation('shield', rotations={      # left arm up and forward with the lid
        b['arm_l']: [(0, R(x=80, z=-30)), (1, R(x=80, z=-30))], b['hand_l']: [(0, R(x=10)), (1, R(x=10))],
        b['arm_r']: [(0, R(x=20, z=-15)), (1, R(x=20, z=-15))],
        b['leg_l']: [(0, R(x=20)), (1, R(x=20))], b['leg_r']: [(0, R(x=-15)), (1, R(x=-15))],
        b['shin_l']: [(0, R(x=-20)), (1, R(x=-20))]})
    m.animation('climb', rotations={
        b['arm_l']: cycle(4, 0.8, lambda p: R(x=150 + 20 * math.sin(2 * math.pi * p))),
        b['arm_r']: cycle(4, 0.8, lambda p: R(x=150 - 20 * math.sin(2 * math.pi * p))),
        b['leg_l']: cycle(4, 0.8, lambda p: R(x=30 - 30 * math.sin(2 * math.pi * p))),
        b['leg_r']: cycle(4, 0.8, lambda p: R(x=30 + 30 * math.sin(2 * math.pi * p)))})
    m.animation('push', rotations={
        b['arm_l']: [(0, R(x=85)), (1, R(x=85))], b['arm_r']: [(0, R(x=85)), (1, R(x=85))],
        b['spine']: [(0, R(x=-20)), (1, R(x=-20))],
        b['leg_l']: cycle(4, 1.2, lambda p: R(x=30 * math.sin(2 * math.pi * p) - 10)),
        b['leg_r']: cycle(4, 1.2, lambda p: R(x=-30 * math.sin(2 * math.pi * p) - 10))})
    m.animation('aim', rotations={         # the pea shooter held up to the eye
        b['arm_r']: [(0, R(x=85, z=10)), (1, R(x=85, z=10))], b['arm_l']: [(0, R(x=85, z=-25)), (1, R(x=85, z=-25))]})
    m.animation('fall', rotations={
        b['arm_l']: [(0, R(z=100)), (0.3, R(z=120)), (0.6, R(z=100))], b['arm_r']: [(0, R(z=-100)), (0.3, R(z=-120)), (0.6, R(z=-100))],
        b['leg_l']: [(0, R(x=20)), (0.6, R(x=20))], b['leg_r']: [(0, R(x=-10)), (0.6, R(x=-10))]})
    m.animation('dead', rotations={b['spine']: [(0, R(x=10)), (0.6, R(x=80))], b['head']: [(0, R()), (0.6, R(x=20))],
                                    b['leg_l']: [(0, R()), (0.6, R(x=-80))], b['leg_r']: [(0, R()), (0.6, R(x=-80))]},
                translations={b['hips']: [(0, (0, 0, 0)), (0.6, (0, -0.4 * s, 0.3 * s))]})


def blob(name, body, eye='#ffffff', pupil='#101010', size=0.5, fuzz=None, legs=0):
    """A round creature (Fuzzball, larva): a body bone that bounces, eyes on its front."""
    m = Model()
    root = m.bone('root', (0, 0, 0))
    bod = m.bone('body', (0, size * 0.5, 0), root)
    eyes = m.bone('eyes', (0, size * 0.6, -size * 0.45), bod)
    s = size
    m.box((-s * 0.5, 0.0, -s * 0.5), (s * 0.5, s * 0.9, s * 0.5), bod, hexc(body))
    m.box((-s * 0.42, s * 0.85, -s * 0.42), (s * 0.42, s * 1.0, s * 0.42), bod, hexc(body))
    if fuzz:
        for k in range(6):
            a = k * math.pi / 3
            cx, cz = math.cos(a) * s * 0.48, math.sin(a) * s * 0.48
            m.box((cx - s * 0.1, s * 0.2, cz - s * 0.1), (cx + s * 0.1, s * 0.75, cz + s * 0.1), bod, hexc(fuzz))
    for x in (-1, 1):
        m.box((x * s * 0.2 - s * 0.1, s * 0.5, -s * 0.53), (x * s * 0.2 + s * 0.1, s * 0.72, -s * 0.5), eyes, hexc(eye))
        m.box((x * s * 0.2 - s * 0.04, s * 0.54, -s * 0.545), (x * s * 0.2 + s * 0.04, s * 0.64, -s * 0.53), eyes, hexc(pupil))
    leg_bones = []
    for k in range(legs):
        side = -1 if k % 2 else 1
        z = (k // 2 - (legs // 2 - 1) / 2) * s * 0.4
        lb = m.bone('leg%d' % k, (side * s * 0.5, s * 0.3, z), bod)
        leg_bones.append(lb)
        m.box((side * s * 0.5 - 0.03, 0.0, z - 0.03), (side * s * 0.5 + side * s * 0.3 + 0.03, s * 0.35, z + 0.03), lb, hexc(pupil))
    m.animation('idle', translations={bod: [(0, (0, 0, 0)), (0.5, (0, s * 0.05, 0)), (1, (0, 0, 0))]})
    m.animation('hop', translations={bod: [(0, (0, 0, 0)), (0.25, (0, s * 0.5, 0)), (0.5, (0, 0, 0))]},
                rotations={bod: [(0, R(x=10)), (0.25, R(x=-10)), (0.5, R(x=10))]})
    m.animation('lunge', rotations={bod: [(0, R(x=-25)), (0.2, R(x=30)), (0.5, R())]},
                translations={bod: [(0, (0, 0, 0)), (0.2, (0, s * 0.2, -s * 0.4)), (0.5, (0, 0, 0))]})
    m.animation('walk', rotations={lb: cycle(4, 0.4, lambda p, k=k: R(y=25 * math.sin(2 * math.pi * p + k))) for k, lb in enumerate(leg_bones)},
                translations={bod: cycle(4, 0.4, lambda p: (0, s * 0.03 * abs(math.sin(2 * math.pi * p)), 0))})
    m.animation('hurt', rotations={bod: [(0, R(x=30, z=15)), (0.3, R())]})
    m.save_glb(path('models', name + '.glb'))


def scrub():
    """A Spit-scrub: a little leaf-capped seed that hides in its bush and spits nuts."""
    m = Model()
    root = m.bone('root', (0, 0, 0))
    bod = m.bone('body', (0, 0.25, 0), root)
    cap = m.bone('cap', (0, 0.55, 0), bod)
    m.box((-0.2, 0.0, -0.2), (0.2, 0.5, 0.2), bod, hexc('#8a5a2a'))
    m.box((-0.07, 0.25, -0.38), (0.07, 0.37, -0.2), bod, hexc('#6a3a1a'))                       # its snout
    m.box((-0.08, 0.27, -0.385), (0.08, 0.35, -0.375), bod, hexc('#1a0a00'))
    for x in (-1, 1):
        m.box((x * 0.09 - 0.04, 0.36, -0.215), (x * 0.09 + 0.04, 0.44, -0.2), bod, hexc('#ffd040'))
    m.box((-0.32, 0.5, -0.32), (0.32, 0.6, 0.32), cap, hexc('#4a9a3a'))
    m.box((-0.1, 0.55, -0.1), (0.1, 0.75, 0.1), cap, hexc('#3a7a2a'))
    m.animation('idle', translations={bod: [(0, (0, 0, 0)), (0.6, (0, 0.03, 0)), (1.2, (0, 0, 0))]})
    m.animation('spit', translations={bod: [(0, (0, 0, 0)), (0.1, (0, 0, 0.1)), (0.2, (0, 0, -0.1)), (0.4, (0, 0, 0))]},
                rotations={bod: [(0, R()), (0.1, R(x=15)), (0.2, R(x=-15)), (0.4, R())]})
    m.animation('hide', translations={bod: [(0, (0, -0.4, 0)), (1, (0, -0.4, 0))]})
    m.animation('hurt', rotations={bod: [(0, R(z=-30)), (0.2, R(z=30)), (0.4, R(z=-20)), (0.6, R())]})
    m.save_glb(path('models', 'scrub.glb'))


def queen():
    """Queen Mildewmite: a great grey-green mite with one red eye, six legs, and a sac."""
    m = Model()
    root = m.bone('root', (0, 0, 0))
    bod = m.bone('body', (0, 1.0, 0), root)
    eye = m.bone('eye', (0, 1.5, -1.0), bod)
    m.box((-1.0, 0.6, -0.9), (1.0, 1.6, 0.6), bod, hexc('#6a7a5a'))
    m.box((-0.8, 0.7, 0.5), (0.8, 1.5, 1.8), bod, hexc('#8a9a6a'))                              # the egg sac
    m.box((-0.6, 0.5, -1.1), (0.6, 1.4, -0.85), bod, hexc('#4a5a3a'))                           # face
    m.box((-0.35, 1.2, -1.2), (0.35, 1.7, -1.05), eye, hexc('#f0f0e0'))                          # eye
    m.box((-0.18, 1.3, -1.25), (0.18, 1.6, -1.18), eye, hexc('#d02020'))
    for x in (-1, 1):                                                                           # mandibles
        m.box((x * 0.3 - 0.08, 0.4, -1.4), (x * 0.3 + 0.08, 0.7, -1.0), bod, hexc('#3a2a1a'))
    legs = []
    for k in range(6):
        side = 1 if k < 3 else -1
        z = (k % 3 - 1) * 0.6
        lb = m.bone('leg%d' % k, (side * 1.0, 1.0, z), bod)
        legs.append(lb)
        m.box((min(side * 1.0, side * 2.0) - 0.08, 0.9, z - 0.08), (max(side * 1.0, side * 2.0) + 0.08, 1.1, z + 0.08), lb, hexc('#3a4a2a'))
        m.box((side * 2.0 - 0.08, -0.0, z - 0.08), (side * 2.0 + 0.08, 1.05, z + 0.08), lb, hexc('#3a4a2a'))
    m.animation('idle', rotations={lb: [(0, R()), (0.6, R(z=4 * (1 if k < 3 else -1))), (1.2, R())] for k, lb in enumerate(legs)},
                translations={bod: [(0, (0, 0, 0)), (0.6, (0, 0.06, 0)), (1.2, (0, 0, 0))]})
    m.animation('walk', rotations={lb: cycle(4, 0.5, lambda p, k=k: R(y=25 * math.sin(2 * math.pi * p + k * 2.1))) for k, lb in enumerate(legs)},
                translations={bod: cycle(4, 0.5, lambda p: (0, 0.06 * abs(math.sin(2 * math.pi * p)), 0))})
    m.animation('stunned', rotations={bod: [(0, R(z=150)), (1, R(z=150))]},
                translations={bod: [(0, (0, -0.3, 0)), (1, (0, -0.3, 0))]})
    m.animation('lay', rotations={bod: [(0, R(x=-10)), (0.3, R(x=15)), (0.6, R())]})
    m.animation('roar', rotations={bod: [(0, R(x=0)), (0.3, R(x=-25)), (0.9, R(x=-25)), (1.2, R())]})
    m.animation('dead', rotations={bod: [(0, R()), (1.5, R(z=150, x=20))]},
                translations={bod: [(0, (0, 0, 0)), (1.5, (0, -0.4, 0))]})
    m.save_glb(path('models', 'queen.glb'))


def owl():
    """Sir Hootenanny: a round crust-owl with a pie-crust brow, who flaps when he talks."""
    m = Model()
    root = m.bone('root', (0, 0, 0))
    bod = m.bone('body', (0, 0.4, 0), root)
    head = m.bone('head', (0, 0.9, 0), bod)
    wl = m.bone('wing_l', (0.32, 0.75, 0), bod)
    wr = m.bone('wing_r', (-0.32, 0.75, 0), bod)
    C = hexc
    m.box((-0.3, 0.05, -0.25), (0.3, 0.85, 0.25), bod, C('#b07a40'))
    m.box((-0.22, 0.15, -0.27), (0.22, 0.7, -0.24), bod, C('#e8c890'))          # his front
    m.box((-0.28, 0.85, -0.26), (0.28, 1.3, 0.24), head, C('#b07a40'))
    m.box((-0.3, 1.24, -0.28), (0.3, 1.34, 0.26), head, C('#7a4a20'))           # the crust brow
    for x in (-1, 1):
        m.box((x * 0.12 - 0.08, 1.0, -0.28), (x * 0.12 + 0.08, 1.16, -0.26), head, C('#fff4d0'))
        m.box((x * 0.12 - 0.04, 1.03, -0.29), (x * 0.12 + 0.04, 1.12, -0.28), head, C('#101010'))
        m.box((x * 0.2 - 0.03, 1.3, -0.05), (x * 0.2 + 0.03, 1.45, 0.05), head, C('#7a4a20'))   # ear tufts
    m.box((-0.04, 0.92, -0.33), (0.04, 1.0, -0.27), head, C('#e0a020'))         # beak
    m.box((0.3, 0.2, -0.18), (0.38, 0.8, 0.2), wl, C('#8a5a2a'))
    m.box((-0.38, 0.2, -0.18), (-0.3, 0.8, 0.2), wr, C('#8a5a2a'))
    for x in (-1, 1):
        m.box((x * 0.12 - 0.06, 0.0, -0.12), (x * 0.12 + 0.06, 0.06, 0.04), bod, C('#e0a020'))
    m.animation('idle', rotations={head: [(0, R()), (1, R(y=15)), (2, R()), (3, R(y=-15)), (4, R())]},
                translations={bod: [(0, (0, 0, 0)), (2, (0, 0.02, 0)), (4, (0, 0, 0))]})
    m.animation('talk', rotations={wl: [(0, R()), (0.15, R(z=50)), (0.3, R())], wr: [(0, R()), (0.15, R(z=-50)), (0.3, R())],
                                   head: [(0, R()), (0.3, R(x=-10)), (0.6, R())]})
    m.animation('fly', rotations={wl: cycle(4, 0.3, lambda p: R(z=70 * math.sin(2 * math.pi * p))),
                                  wr: cycle(4, 0.3, lambda p: R(z=-70 * math.sin(2 * math.pi * p)))})
    m.save_glb(path('models', 'owl.glb'))


def people():
    s = 1.0
    sprig, b = figure(s, shirt='#4f9a3e', trousers='#d8c8a0', shoes='#6a4422', hair='#a8642a', hat='#5cb84a', apron='#3a7a2a')
    standard_anims(sprig, b, s, hero=True)
    sprig.save_glb(path('models', 'sprig.glb'))
    kinds = {
        'fennel': dict(shirt='#6ac05a', trousers='#5a8a3a', hair='#9ad87a', hat='#7ad06a', girl=True),
        'chive': dict(shirt='#c05a3a', trousers='#7a4a2a', hair='#c86a3a', hat='#d04a3a', hat_kind='spiky'),
        'mint': dict(shirt='#7ad8c8', trousers='#3a7a6a', hair='#e8e0c0', hat='#6ac8a8', girl=True),
        'dill': dict(shirt='#d8d86a', trousers='#7a7a3a', hair='#e8e0c0', hat='#b8c85a'),
        'parsley': dict(shirt='#3a8a5a', trousers='#2a5a3a', hair='#2a4a2a', hat='#4ab86a', big_head=1.15),
        'sage': dict(shirt='#9aa88a', trousers='#5a6a4a', hair='#b0b8a0', hat='#8aa87a', belly=0.04),
    }
    # grown-ups are taller: Basil (Pantry Quest II's hero, now a travelling cook)
    fig, fb = figure(1.35, shirt='#e8e0d0', trousers='#4a5a7a', hair='#5a3a1a', hat='#f4f4f4', hat_kind='tall', apron='#c84a3a', skin='#e8b890')
    standard_anims(fig, fb, 1.35)
    fig.save_glb(path('models', 'basil.glb'))
    # Larder Town and the castle
    adults = {
        'pip': dict(shirt='#f4f0e8', trousers='#3a3a4a', hair='#c08040', hat='#ffffff', hat_kind='tall', apron='#ffffff', belly=0.03),
        'guard': dict(shirt='#3a5aa0', trousers='#2a2a3a', hair='#3a2a1a', hat='#b8b8c8', hat_kind='helmet', apron='#c8c8d8', shoes='#2a2020'),
        'kimchi': dict(shirt='#8a3a4a', trousers='#4a2a30', hair='#c8c8c8', hat='#c8c8c8', hat_kind='bun', skin='#e0b898', apron='#d8c8a0', girl=True, belly=0.02),
        'baker': dict(shirt='#e0c890', trousers='#6a4a2a', hair='#3a2a1a', hat='#f4f4f4', hat_kind='tall', apron='#f0e8d8', belly=0.05),
        'townsman': dict(shirt='#6a8a4a', trousers='#5a4a3a', hair='#2a1a10', skin='#c89070'),
        'townswoman': dict(shirt='#c08a4a', trousers='#7a3a3a', hair='#7a3a1a', girl=True),
        'king': dict(shirt='#a02a3a', trousers='#5a1a2a', hair='#e8e0d0', hat='#f0c040', hat_kind='tiara', belly=0.08),
    }
    for name, kw in adults.items():
        fig, fb = figure(1.4 if name != 'kimchi' else 1.25, **kw)
        standard_anims(fig, fb, 1.4)
        fig.save_glb(path('models', name + '.glb'))
    fig, fb = figure(1.0, shirt='#e8a83a', trousers='#c8603a', hair='#e8c050', hat='#f0d040', hat_kind='tiara', girl=True, apron='#f4e0a0')
    standard_anims(fig, fb, 1.0)
    fig.save_glb(path('models', 'saffron.glb'))
    # a Stalebie: a loaf gone stale and walking, that rises from the field at night
    fig, fb = figure(1.2, shirt='#9a7a4a', trousers='#7a5a34', hair='#5a4020', skin='#c8a870', shoes='#4a3018', eyes='#ff3020', belly=0.03)
    standard_anims(fig, fb, 1.2, hero=True)
    fig.save_glb(path('models', 'stalebie.glb'))
    for name, kw in kinds.items():
        fig, fb = figure(0.95 if name != 'parsley' else 0.9, **kw)
        standard_anims(fig, fb, 0.95)
        fig.save_glb(path('models', name + '.glb'))


def statics():
    """Things without skeletons: chests, pots, a dummy, the spoon, the pot-lid, the shooter."""
    o = Obj('chest base: 1 x 0.6 x 0.7')
    o.box((-0.5, 0, -0.35), (0.5, 0.55, 0.35), uvs=1.0)
    o.save(path('models', 'chest_base.obj'))
    o = Obj('chest lid (hinged at its back edge, z = 0)')
    o.box((-0.52, 0, -0.72), (0.52, 0.22, 0.0), uvs=1.0)
    o.save(path('models', 'chest_lid.obj'))
    o = Obj('a clay pot')
    o.cylinder((0, 0, 0), 0.22, 0.12, 8, top=False, radius_top=0.3, uvs=2)
    o.cylinder((0, 0.12, 0), 0.3, 0.28, 8, top=False, radius_top=0.18, uvs=2)
    o.cylinder((0, 0.4, 0), 0.16, 0.08, 8, top=True, radius_top=0.18, uvs=2)
    o.save(path('models', 'pot.obj'))
    o = Obj('the wooden spoon: along -z from the hand')
    o.box((-0.025, -0.02, -0.55), (0.025, 0.02, 0.0), uvs=4)
    o.box((-0.07, -0.025, -0.75), (0.07, 0.025, -0.5), uvs=4)
    o.save(path('models', 'spoon.obj'))
    o = Obj('the pot-lid shield: a disc facing -z')
    o.cylinder((0, 0, 0), 0.24, 0.04, 10, top=True, bottom=True, uvs=2)
    o.cylinder((0, 0.04, 0), 0.05, 0.05, 6, top=True, uvs=2)
    o.save(path('models', 'potlid.obj'))
    o = Obj('a training dummy: a post and a sack')
    o.cylinder((0, 0, 0), 0.08, 1.4, 6, uvs=1)
    o.cylinder((0, 0.55, 0), 0.25, 0.6, 8, uvs=1)
    o.box((-0.45, 1.0, -0.05), (0.45, 1.08, 0.05), uvs=1)
    o.sphere((0, 1.35, 0), 0.18, 8, 5)
    o.save(path('models', 'dummy.obj'))
    o = Obj('a pea shooter: a forked stick')
    o.box((-0.02, 0, -0.02), (0.02, 0.18, 0.02), uvs=4)
    o.box((-0.1, 0.16, -0.02), (0.1, 0.2, 0.02), uvs=4)
    o.box((-0.1, 0.16, -0.02), (-0.06, 0.32, 0.02), uvs=4)
    o.box((0.06, 0.16, -0.02), (0.1, 0.32, 0.02), uvs=4)
    o.save(path('models', 'shooter.obj'))
    o = Obj('a heart')
    for i in range(10):
        a0, a1 = 2 * math.pi * i / 10, 2 * math.pi * (i + 1) / 10

        def hp(t):
            x = 16 * math.sin(t) ** 3
            y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
            return (x / 34, y / 34 + 0.25)
        p0, p1 = hp(a0), hp(a1)
        for z, n in ((0.06, 1), (-0.06, -1)):
            if n > 0:
                o.tri((0, 0.25, z), (p0[0], p0[1], z), (p1[0], p1[1], z))
            else:
                o.tri((0, 0.25, z), (p1[0], p1[1], z), (p0[0], p0[1], z))
        o.quad((p0[0], p0[1], -0.06), (p1[0], p1[1], -0.06), (p1[0], p1[1], 0.06), (p0[0], p0[1], 0.06))
    o.save(path('models', 'heart.obj'))
    o = Obj('a bean (a gem of the Pantry Kingdom)')
    o.sphere((0, 0.15, 0), 0.12, 8, 5, squash=1.4)
    o.save(path('models', 'bean.obj'))
    o = Obj('a key')
    o.box((-0.03, 0, -0.02), (0.03, 0.3, 0.02), uvs=4)
    o.box((-0.08, 0.3, -0.02), (0.08, 0.42, 0.02), uvs=4)
    o.box((0.03, 0.04, -0.02), (0.09, 0.08, 0.02), uvs=4)
    o.box((0.03, 0.12, -0.02), (0.08, 0.16, 0.02), uvs=4)
    o.save(path('models', 'key.obj'))


if __name__ == '__main__':
    people()
    owl()
    blob('fuzzball', '#7a9a6a', size=0.6, fuzz='#a8c890')
    blob('larva', '#c8d0a0', size=0.35, legs=4)
    blob('nut', '#7a4a1a', size=0.2, eye='#7a4a1a', pupil='#7a4a1a')
    scrub()
    queen()
    statics()
    print('models written')
