"""The castle garden: Sprig sneaks through the hedges past patrolling guards to the
courtyard where Princess Saffron waits. Caught, he's marched back to the garden gate.

North is -z. The gate from the castle road is at the south; three hedge rows cross the
garden, each with a gap at alternate ends, and a guard walks each lane between them. The
courtyard (a fountain, the castle's window) is at the north end.
"""
import math

from areakit import Area, box_wall
from kit import t3, mesh, collider, tags, script, particles, q

W = 20.0


def flat(x, z):
    return 0.0


def build():
    a = Area('castle', 'Castle Larder', music='music/castle.wav', kill_y=-20, sky='#b0dcf0ff', fog=(26, 52),
             ambient=('#8898b8ff', 0.6), chunk=20)
    a.entity('Sky', t3((0, 0, 0)), script('scripts/sky.bs', runs=False))
    for cz in range(-44, 40, 12):
        for cx in range(-24, 24, 12):
            a.geo('grass', cx + 6, cz + 6).ground(cx, cz, cx + 12, cz + 12, 2, 2, flat, uvs=0.3)
    # the garden's outer wall, and the castle rising behind the courtyard
    for (x0, z0, x1, z1) in [(-W, 34, -2.5, 34), (2.5, 34, W, 34), (-W, -40, W, -40), (-W, -40, -W, 34), (W, -40, W, 34)]:
        box_wall(a, 'stone', x0, z0, x1, z1, -1, 6, thick=1.6, uvs=0.25)
    a.geo('stone', 0, -46).box((-18, -1, -52), (18, 22, -41), uvs=0.2)
    for xx in (-16, 0, 16):
        a.geo('stone', xx, -46).cylinder((xx, 0, -46), 3.2, 28, 10, top=False, uvs=0.25)
        a.geo('thatch', xx, -46).cone((xx, 28, -46), 3.8, 7, 10, uvs=0.3)
    a.entity('Window', t3((0, 6, -40.86), (0, 0, 0), (2.4, 3.0, 0.1)), mesh('cube', '#f8e8a0ff', lit=False))
    a.loadzone(0, 0, 34.4, 5, 4, 1.2, to='town', at='castle')
    a.spawn_point('start', 0, 0.1, 30, 0)
    a.spawn_point('t_court', 6, 0.1, -25, 0)
    # the hedge rows: (z, gap at the east or west end)
    rows = [(20, 'e'), (8, 'w'), (-4, 'e'), (-16, 'w')]
    for z, gap in rows:
        if gap == 'e':
            box_wall(a, 'hedge', -W, z, W - 5, z, -0.2, 2.6, thick=1.2)
        else:
            box_wall(a, 'hedge', -W + 5, z, W, z, -0.2, 2.6, thick=1.2)
    # shrubs to hide behind in the lanes
    for x, z in [(-8, 14), (6, 14), (-2, 2), (10, 2), (-12, -10), (2, -10)]:
        a.entity('Shrub', t3((x, 0.7, z), (0, x * 20, 0), (1.8, 1.4, 1.4)), mesh('sphere', '#ffffffff', 'art/hedge.png'),
                 collider('sphere', radius=0.5))
    # the guards, one per lane, walking it end to end
    for i, (zl, x0, x1) in enumerate([(14, -16, 16), (2, 16, -16), (-10, -16, 16)]):
        a.entity('Guard', t3((x0, 0, zl), (0, 90 if x1 < x0 else -90, 0)), mesh('model', file='models/guard.glb', shadow=True),
                 ('Animator', [('clip', q('walk')), ('speed', 1), ('loop', True), ('playing', True), ('blend', 0.2)]),
                 collider('capsule', (1, 1.5, 1), 0.35, offset=(0, 0.75, 0)), tags('npc'),
                 script('scripts/guard.bs', path=[(x0, 0, zl), (x1, 0, zl)], speed=1.7 + i * 0.25, wait=1.8 - i * 0.3))
    for x, z in [(-17, 26), (17, 26), (-17, -21), (17, -21)]:
        a.pot(x, 0, z)
    # the courtyard: a gate in the last wall, the fountain, the princess
    box_wall(a, 'stone', -W, -22, -2.5, -22, -0.5, 3.2, thick=1.0)
    box_wall(a, 'stone', 2.5, -22, W, -22, -0.5, 3.2, thick=1.0)
    a.geo('stone', 0, -30).cylinder((0, -0.3, -30), 3.4, 1.0, 16, top=False, uvs=0.5)
    a.geo('stone', 0, -30).cylinder((0, -0.3, -30), 3.0, 0.98, 16, top=False, uvs=0.5, inside=True)
    a.geo('stone', 0, -30).cylinder((0, -0.3, -30), 0.4, 2.6, 8, uvs=0.5)
    a.entity('Fountain Water', t3((0, 0.55, -30), (0, 0, 0), (6.0, 0.02, 6.0)), mesh('cylinder', '#5a90c8ff', lit=False))
    a.entity('Fountain Ring', t3((0, 0.5, -30)), collider('capsule', (1, 1, 1), 3.4), tags('seethrough'))
    a.entity('Fountain Spray', t3((0, 2.4, -30)), particles(rate=30, max=80, lifetime=1.0, speed=2.2, spread=25, gravity=6,
                                                            size_start=0.14, size_end=0.05, color_start='#c8e8ffd0', color_end='#80b0ff00'))
    for x in (-9, 9):
        for z in (-26, -34):
            a.entity('Flowers', t3((x, 0.2, z), (0, 0, 0), (2.4, 0.4, 2.4)), mesh('sphere', '#ffffffff', 'art/flowers.png', uv=(2, 2)))
    a.npc('saffron', 0, 0, -36, 0, until='met_saffron', reach=2.6)
    a.npc('kimchi', 4.5, 0, -36.5, -20, until='met_saffron', reach=2.6)
    a.save()
