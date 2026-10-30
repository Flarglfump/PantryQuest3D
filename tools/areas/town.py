"""Larder Town: the royal capital under Castle Larder.

North is -z. The road from Breadbasket Fields comes in through the south gate; the market
square (the well, the stalls, the townsfolk) is in the middle; the Royal Kitchens (Pip)
are to the west, the Temple of the First Hearth to the east (its door won't open yet),
and the castle road climbs out of the north side to the castle garden.
"""
import math
import random

from areakit import Area, box_wall, town_house, stall
from kit import t3, mesh, collider, tags, script, particles, q

HALF = 40.0


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def height(x, z):
    h = 0.0
    if z < -26 and abs(x) < 4:                 # the castle road climbs
        h = 3.0 * smooth((-26 - z) / 12)
    elif z < -26:
        h = 3.0 * smooth((-26 - z) / 2)
    return h


def build():
    random.seed(5)
    a = Area('town', 'Larder Town', music='music/town.wav', kill_y=-20, sky='#b0dcf0ff', fog=(28, 56),
             ambient=('#8898b8ff', 0.6), chunk=20)
    a.entity('Sky', t3((0, 0, 0)), script('scripts/sky.bs', runs=True))
    for cz in range(-44, 44, 11):
        for cx in range(-44, 44, 11):
            a.geo('cobble', cx + 5.5, cz + 5.5).ground(cx, cz, cx + 11, cz + 11, 2, 2, height, uvs=0.3)
    # the town wall round it all (gaps: south gate, the castle road north)
    for (x0, z0, x1, z1) in [(-HALF, HALF, -3, HALF), (3, HALF, HALF, HALF), (-HALF, -HALF, -3, -HALF), (3, -HALF, HALF, -HALF),
                             (-HALF, -HALF, -HALF, HALF), (HALF, -HALF, HALF, HALF)]:
        box_wall(a, 'stone', x0, z0, x1, z1, -1, 7, thick=1.6, uvs=0.25)
    for xx in (-4, 4):
        a.geo('stone', xx, HALF).box((xx - 1.2, -1, HALF - 1.2), (xx + 1.2, 9, HALF + 1.2), uvs=0.25)
        a.geo('thatch', xx, HALF).cone((xx, 9, HALF), 1.9, 2.5, 8)
    a.loadzone(0, 0, HALF - 0.9, 5, 4, 1.2, to='fields', at='town')
    a.spawn_point('start', 0, 0.1, HALF - 4, 0)
    a.spawn_point('fields', 0, 0.1, HALF - 4, 0)
    a.spawn_point('castle', 0, height(0, -34) + 0.1, -34, 180)
    # the castle road and its gate
    a.loadzone(0, height(0, -HALF + 1), -HALF + 0.9, 5, 4, 1.2, to='castle', at='start')
    a.npc('guard', -3.2, height(-3.2, -36), -36, 160)
    a.sign(3.4, height(3.4, -27), -27, 180, 'sign_castle')

    # ---- the market square ----
    a.geo('stone', 0, 6).cylinder((0, -0.3, 6), 1.4, 1.2, 12, top=False, uvs=0.6)
    a.geo('stone', 0, 6).cylinder((0, -0.3, 6), 1.1, 1.18, 12, top=False, uvs=0.6, inside=True)
    a.entity('Well Water', t3((0, 0.5, 6), (0, 0, 0), (2.1, 0.02, 2.1)), mesh('cylinder', '#4070a0ff', lit=False))
    a.entity('Well Ring', t3((0, 0.45, 6)), collider('capsule', (1, 1, 1), 1.4), tags('seethrough'))
    for xx in (-1.2, 1.2):
        a.geo('bark', xx, 6).cylinder((xx, 0.9, 6), 0.08, 1.6, 5)
    a.entity('Well Roof', t3((0, 2.8, 6), (0, 0, 0), (3.2, 0.12, 1.6)), mesh('cube', '#ffffffff', 'art/thatch.png'))
    stall(a, -9, 12, 0, '#d84a4aff')
    stall(a, -9, 0, 0, '#4a8ad8ff', yaw=180)
    stall(a, 9, 12, 0, '#e0b040ff')
    stall(a, 9, 0, 0, '#5ab85aff', yaw=180)
    for x, z, c in [(-9, 12.4, '#e0503cff'), (9, 12.4, '#f0c850ff'), (-9, -0.4, '#d04060ff'), (9, -0.4, '#80c050ff')]:
        for k in range(3):
            a.entity('Produce', t3((x - 0.8 + k * 0.8, 1.15, z), (0, k * 40, 0), 0.32), mesh('sphere', c))
    a.npc('baker', -9, 0, 13.6, 180)
    a.npc('townswoman', 9, 0, 13.6, 180)
    a.npc('townsman', 3.5, 0, 4, 250)
    a.npc('gossip', -4, 0, 20, 30, model='townswoman')
    a.npc('child', 5, 0, 21, 200, model='mint')
    a.sign(-3, 0, 24, 0, 'sign_town')

    # ---- houses ----
    for x, z, w, d, side in [(-28, 30, 8, 6, 'n'), (-14, 30, 7, 6, 'n'), (14, 30, 7, 6, 'n'), (28, 30, 8, 6, 'n'),
                             (-30, 14, 6, 8, 'e'), (30, 14, 6, 8, 'w'), (-28, -18, 8, 7, 's'), (28, -20, 8, 7, 's'),
                             (-14, -20, 6, 6, 's'), (14, -20, 6, 6, 's')]:
        town_house(a, x, z, w, d, 4.0, 0, wall='planks', roof='thatch', door_side=side)
    # the Royal Kitchens (west): Pip at the door
    town_house(a, -27, 0, 9, 10, 5.0, 0, wall='stone', roof='thatch', door_side='e')
    a.entity('Chimney Smoke', t3((-29, 9, -2)), particles(rate=4, max=20, lifetime=3, speed=0.6, spread=15, gravity=-0.2, size_start=0.4,
                                                           size_end=1.2, color_start='#d0d0d0a0', color_end='#ffffff00'))
    a.npc('pip', -21.2, 0, 0, 270)
    a.sign(-21.5, 0, 3.8, 270, 'sign_kitchens')
    # the Temple of the First Hearth (east)
    tx, tz = 26, -4
    a.geo('stone', tx, tz).box((tx - 6, -0.3, tz - 7), (tx + 6, 7, tz + 7), uvs=0.25, sides=('px', 'nx', 'pz', 'nz', 'py'))
    a.geo('stone', tx, tz).box((tx - 7, -0.3, tz - 8), (tx + 7, 0.4, tz + 8), uvs=0.25)
    for zz in (-5, -1.5, 1.5, 5):
        a.geo('stone', tx - 6.8, tz + zz).cylinder((tx - 6.8, 0.4, tz + zz), 0.45, 6.4, 8, uvs=0.5)
    a.geo('thatch', tx, tz).cylinder((tx, 7, tz), 8.2, 3.2, 4, top=False, radius_top=0.4, uvs=0.25)
    a.entity('Temple Door', t3((tx - 6.05, 2.2, tz), (0, 90, 0), (2.4, 3.6, 0.1)), mesh('cube', '#c8a050ff', 'art/planks.png'),
             tags('interact', 'focusable'), script('scripts/sign.bs', say='temple_door', prompt='Check', reach=2.4))
    a.entity('Hearth Glow', t3((tx - 6.3, 4.4, tz)), particles(rate=6, max=20, lifetime=1.2, speed=0.4, spread=60, area=(0.3, 2.0),
                                                              gravity=-0.4, size_start=0.15, size_end=0, color_start='#ffd080ff',
                                                              color_end='#ff600000', blend='add'))
    # pots, crates and a few things to cut
    for x, z in [(-6, 24), (-5.2, 24.6), (6, 24), (17, 26), (-17, 26), (-20, -14), (20, -14), (12, 8), (-12, 8)]:
        a.pot(x, 0, z)
    for x, z in [(-34, -32), (-30, -34), (32, -33), (34, -30), (-36, 0), (36, 2)]:
        a.grass(x, height(x, z), z)
    for x, z in [(-20, 22), (20, 22)]:
        a.tree(x, 0, z, 1.0)
    a.save()
