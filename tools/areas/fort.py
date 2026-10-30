"""The Raider Fort: the Paprika Raiders' stronghold in a desert canyon west of Brine Valley.

The canyon runs east (Brine Valley) to west (the gate to the Haunted Flats, shut). The fort
is on the north side: Raiders patrol inside (their sight sends you back out), and the lever
that opens the Flats gate is at the back.
"""
import math
import random

from areakit import Area, box_wall
from kit import t3, mesh, collider, tags, script, particles, q


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def height(x, z):
    h = 0.3 * math.sin(x * 0.2) * math.cos(z * 0.3)
    infort = -16 < x < 16 and -36 < z < -10
    if not infort:
        d = abs(z) - 10
        if d > 0:
            h += 9 * smooth(d / 3)
    if abs(x) > 44:
        h += 9 * smooth((abs(x) - 44) / 3)
    return h


def build():
    random.seed(71)
    a = Area('fort', 'Raider Fort', music='music/castle.wav', kill_y=-20, sky='#f0d0a0ff', fog=(26, 60), fog_color='#e8c898ff',
             ambient=('#c0a080ff', 0.6), sun=('#fff0d0ff', 1.0), chunk=22)
    for cz in range(-44, 22, 11):
        for cx in range(-55, 55, 11):
            a.geo('sand', cx + 5.5, cz + 5.5).ground(cx, cz, cx + 11, cz + 11, 4, 4, height, uvs=0.25)
    # the way back east
    a.loadzone(46, height(45, 0), 0, 1.5, 4, 8, to='gorge', at='fort')
    a.spawn_point('start', 40, height(40, 0) + 0.1, 0, 90)
    a.spawn_point('gorge', 40, height(40, 0) + 0.1, 0, 90)
    a.sign(38, height(38, 3), 3, 90, 'sign_fort')
    # the fort: walls round the compound, the way in on the south
    for (x0, z0, x1, z1) in [(-14, -12, -2, -12), (2, -12, 14, -12), (-14, -34, 14, -34), (-14, -34, -14, -12), (14, -34, 14, -12)]:
        box_wall(a, 'planks', x0, z0, x1, z1, -0.5, 4.0, thick=0.8, uvs=0.3)
    for xx in (-2.8, 2.8):
        a.geo('planks', xx, -12).box((xx - 0.8, -0.5, -12.8), (xx + 0.8, 6, -11.2), uvs=0.3)
    # the Raiders on patrol (their sight: guard.bs)
    for i, (zl, x0, x1) in enumerate([(-18, -12, 12), (-26, 12, -12)]):
        a.entity('Raider', t3((x0, 0, zl), (0, 90 if x1 < x0 else -90, 0)), mesh('model', file='models/raider.glb', shadow=True),
                 ('Animator', [('clip', q('walk')), ('speed', 1), ('loop', True), ('playing', True), ('blend', 0.2)]),
                 collider('capsule', (1, 1.5, 1), 0.35, offset=(0, 0.75, 0)), tags('npc'),
                 script('scripts/guard.bs', path=[(x0, 0, zl), (x1, 0, zl)], speed=1.8 + i * 0.3, wait=1.4, say='raider_caught'))
    for x, z in [(-8, -22), (8, -22), (-4, -30), (6, -15)]:       # crates to hide behind
        a.geo('planks', x, z).box((x - 1, 0, z - 1), (x + 1, 1.8, z + 1), uvs=0.5)
    a.entity('Lever', t3((0, 0.6, -31), (0, 0, 0), (0.2, 1.2, 0.2)), mesh('cube', '#8a5a3aff', 'art/planks.png'), tags('interact', 'focusable'),
             script('scripts/lever.bs', id='fort_gate'))
    # the gate to the Haunted Flats (west)
    for zz in (-6, 6):
        a.geo('stone', -42, zz).box((-43.5, -0.5, zz - 1.5), (-40.5, 8, zz + 1.5), uvs=0.3)
    a.blocker(-42, 0, 0, (0.6, 5, 9), 'fort_gate', material='planks', yaw=0)
    a.sign(-38, 0, 5, 90, 'fort_gate')
    a.loadzone(-46, height(-45, 0), 0, 1.5, 4, 8, to='flats', at='start')
    a.spawn_point('flats', -38, height(-38, 0) + 0.1, 0, -90)
    for x, z in [(20, 6), (-24, -7), (30, -7)]:
        s = random.uniform(1.4, 2.4)
        a.entity('Rock', t3((x, height(x, z) + s * 0.25, z), (0, random.uniform(0, 360), 0), (s, s * 0.7, s)),
                 mesh('sphere', '#e0b080ff', 'art/stone.png'), collider('sphere', radius=0.5))
    a.save()
