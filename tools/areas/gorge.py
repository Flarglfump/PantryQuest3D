"""Brine Valley: a river gorge west of Breadbasket Fields.

North is -z. The road from the field comes in through a gap in the east cliff. The river
runs down the middle of the gorge from Fizzwater Falls (north) to Lake Brine (south). A log
bridge crosses it; on the west bank a path climbs to a ledge before the falls, where the
Fizzlings' royal seal waits for a song of the royal family. Frogs sing on the logs.
"""
import math
import random

from areakit import Area
from kit import drawn, t3, mesh, collider, tags, script, particles, q

SURF = -1.2          # the river's surface
BED = -4.2
LEDGE = 5.0          # the ledge before the falls


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def river_x(z):
    return 2.0 * math.sin(z * 0.05)


def height(x, z):
    h = 0.3 * math.sin(x * 0.4) * math.cos(z * 0.13)
    d = abs(x - river_x(z))
    h = BED + (h - BED) * smooth((d - 4) / 3)              # the river's channel
    # the path up to the ledge, on the west bank
    if x < -6.5:
        h = max(h, LEDGE * smooth((-14 - z) / 34))
    # the cliffs either side, with a gap east for the road from the field
    side = abs(x) - 11
    if side > 0:                                   # (the gaps' sides gently banked, not sheer)
        gap = smooth((abs(z - 40) - 3) / 6) if x > 0 else smooth((abs(z - 20) - 3) / 6)
        h += 12 * smooth(side / 3) * gap
    # the cliff behind the falls
    if z < -58:
        h = max(h, BED + (16 - BED) * smooth((-58 - z) / 3)) if abs(x - river_x(z)) > 3.5 or z < -63 else h
    return h


def build():
    global height
    random.seed(31)
    a = Area('gorge', 'Brine Valley', music='music/brine.wav', kill_y=-20, sky='#a8d8f0ff', fog=(60, 130),
             ambient=('#8898b8ff', 0.55), chunk=20)
    a.entity('Sky', t3((0, 0, 0)), script('scripts/sky.bs'))
    for cz in range(-72, 76, 12):
        for cx in range(-20, 20, 10):
            mat = 'cliff' if cx in (-20, 10) and not (cx == 10 and 30 <= cz <= 42) and not (cx == -20 and 12 <= cz <= 24) else 'grass'
            fine = 2 if cz < -56 else 1
            a.geo(mat, cx + 5, cz + 6).ground(cx, cz, cx + 10, cz + 12, 5 * fine, 6 * fine, height, uvs=0.25)
    height = drawn(height)        # (from here on, things are set on the ground as drawn: none float or sink)
    # the river
    a.water(-9, -64, 9, 76, SURF, depth=5)
    a.entity('Current', t3((0, SURF + 0.05, 20)), particles(rate=6, max=40, lifetime=4, speed=3, spread=5, area=(4, 60),
                                                          size_start=0.15, size_end=0.0, color_start='#ffffffa0', color_end='#ffffff00'))
    # ---- the way in from the field ----
    a.loadzone(13.5, height(13, 40), 40, 1.5, 4, 7, to='fields', at='gorge')
    a.spawn_point('start', 9, height(9, 40) + 0.1, 40, 90)
    a.spawn_point('fields', 9, height(9, 40) + 0.1, 40, 90)
    a.sign(8, height(8, 36.5), 36.5, 90, 'sign_brine')
    # the way west, to the Raider Fort and the Sugar Dunes
    a.loadzone(-13.5, height(-13, 20), 20, 1.5, 4, 7, to='fort', at='gorge')
    a.spawn_point('fort', -9, height(-9, 20) + 0.1, 20, -90)
    a.sign(-8.5, height(-8.5, 16.5), 16.5, -90, 'sign_fort')
    # the log bridge
    bz = 4.0
    a.geo('planks', 0, bz).box((-7.5, -0.35, bz - 1.4), (7.5, 0.05, bz + 1.4), uvs=0.5)
    for x in (-6, -2, 2, 6):
        for dz in (-1.5, 1.5):
            a.geo('bark', x, bz + dz).cylinder((x, BED, bz + dz), 0.18, 5.4, 6, uvs=1)
    for dz in (-1.45, 1.45):
        a.geo('planks', 0, bz + dz).box((-7.5, 0.05, bz + dz - 0.1), (7.5, 0.75, bz + dz + 0.1), uvs=0.5)
    # ---- the falls (north) ----
    fz = -62.0
    a.geo('water', 0, fz).quad((-3.2, 16, fz + 0.3), (3.2, 16, fz + 0.3), (3.2, LEDGE + 3.4, fz + 0.3), (-3.2, LEDGE + 3.4, fz + 0.3),
                               (0, 0), (2, 0), (2, 3), (0, 3))
    a.entity('Falls', t3((0, (LEDGE + 3.4 + SURF) / 2, fz + 0.5), (0, 0, 0), (6.4, LEDGE + 3.4 - SURF, 0.3)),
             mesh('cube', '#c0e8ffd0', 'art/water.png', uv=(2, 4), cast=False),
             collider('box'), tags('interact', 'focusable'), script('scripts/songdoor.bs', song='lullaby', id='door:falls', say='falls_seal', reach=4.0))
    a.entity('Spray', t3((0, SURF + 0.3, fz + 1.2)), particles(rate=20, max=60, lifetime=1.2, speed=2.5, spread=50, area=(5, 1), gravity=2,
                                                              size_start=0.3, size_end=0.8, color_start='#ffffffb0', color_end='#ffffff00'))
    for xx in (-2.1, 2.1):         # the cave's jambs
        a.geo('stone', xx, fz - 1).box((xx - 0.4, LEDGE - 0.5, fz - 1.2), (xx + 0.4, LEDGE + 3.0, fz + 0.2), uvs=0.4)     # (up to the lintel, not into it: no shared faces)
    a.geo('stone', 0, fz - 1).box((-2.5, LEDGE + 3.0, fz - 1.2), (2.5, LEDGE + 3.6, fz + 0.2), uvs=0.4)
    a.entity('Cave', t3((0, LEDGE + 1.5, fz - 0.95), (0, 0, 0), (3.4, 3.0, 0.1)), mesh('cube', '#081018ff', lit=False))
    a.loadzone(0, LEDGE, fz - 0.5, 3, 3, 0.6, to='fizzdomain', at='start', needs='door:falls')
    a.spawn_point('falls', -2.5, LEDGE + 0.1, fz + 4.5, 160)
    # the ledge before the falls, joined to the path
    a.geo('stone', -4, fz + 4).box((-11, BED, fz - 1.0), (2.6, LEDGE - 0.03, fz + 7), uvs=0.3)   # (just under the ground where they meet: no flicker)
    a.sign(-5.5, LEDGE, fz + 5.5, 180, 'falls_seal')
    # a low wall along the path's edge, above the drop to the river
    for i in range(12):
        z0, z1 = -16 - i * 3, -19 - i * 3
        y0, y1 = height(-7.6, z0), height(-7.6, z1)
        o = a.geo('stone', -6.4, z0)
        o.box((-6.6, min(y0, y1) - 1.0, z1), (-6.1, max(y0, y1) + 0.8, z0), uvs=0.4)
    # ---- the way south to Lake Brine ----
    a.loadzone(0, BED, 75, 22, 12, 1.5, to='lake', at='gorge')
    a.spawn_point('lake', -7, height(-7, 66) + 0.1, 66, 0)
    # frogs on the logs
    for i, (x, z) in enumerate([(-1.5, 30), (0.8, 31.5), (2.4, 29.8)]):
        a.geo('bark', x, z).cylinder((x - 1.2, SURF - 0.1, z), 0.4, 0.4, 8)
        a.npc('frog', x, SURF + 0.15, z, 0, reach=2.6)
    # the valley's critters
    for x, z in [(-8, 18), (7, -14), (-8, -8), (6, 22)]:
        a.enemy('fuzzball', x, height(x, z) + 0.1, z, hp=2, damage=2)
    for x, z in [(8, 10), (-8, 28), (8, -30)]:
        a.tree(x, height(x, z), z, random.uniform(0.9, 1.3), random.choice(['', 'bean1', 'heart']))
    for x, z in [(9, -40), (9.5, -41), (-9, 50)]:
        a.pot(x, height(x, z), z)
    n = 0
    while n < 26:
        x, z = random.uniform(-10, 10), random.uniform(-50, 70)
        if abs(x - river_x(z)) < 7.5 or (x < -6.5 and z < -14):
            continue
        a.grass(x, height(x, z), z)
        n += 1
    a.save()
