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


MOAT = -24.0          # the castle moat crosses the town below the castle road
MOAT_SURF = -0.5


def height(x, z):
    h = 0.0
    if abs(z - MOAT) < 2.6 and abs(x) < 37:
        return -3.2 + 3.2 * smooth((abs(z - MOAT) - 1.6) / 1.0)
    if z < -26 and abs(x) < 4:                 # the castle road climbs
        h = 3.0 * smooth((-26 - z) / 12)
    elif z < -26:
        h = 3.0 * smooth((-26 - z) / 2)
    return h


def build(era='fresh'):
    random.seed(5)
    risen = era == 'risen'
    if risen:
        a = Area('town', 'Larder Town', music='music/castle.wav', kill_y=-20, sky='#2a2a30ff', fog=(20, 72), fog_color='#30302aff',
                 ambient=('#707860ff', 0.5), sun=('#a0a890ff', 0.4), chunk=20, variant='risen')
    else:
        a = Area('town', 'Larder Town', music='music/town.wav', kill_y=-20, sky='#b0dcf0ff', fog=(28, 56),
                 ambient=('#8898b8ff', 0.6), chunk=20)
        a.entity('Sky', t3((0, 0, 0)), script('scripts/sky.bs', runs=True))
    ground = 'rot' if risen else 'cobble'
    for cz in range(-44, 44, 11):
        for cx in range(-44, 44, 11):
            fine = 5 if cz in (-33, -22) else 1
            a.geo(ground, cx + 5.5, cz + 5.5).ground(cx, cz, cx + 11, cz + 11, 2 * fine, 2 * fine, height, uvs=0.3)
    # the moat and the castle road's bridge over it
    a.water(-37, MOAT - 2.6, 37, MOAT + 2.6, MOAT_SURF, depth=3)
    a.geo('planks', 0, MOAT).box((-3, -0.4, MOAT - 2.8), (3, 0.05, MOAT + 2.8), uvs=0.5)
    for xx in (-3, 3):
        a.geo('planks', xx, MOAT).box((xx - 0.12, 0.05, MOAT - 2.8), (xx + 0.12, 0.8, MOAT + 2.8), uvs=0.5)
    # the town wall round it all (gaps: south gate, the castle road north)
    for (x0, z0, x1, z1) in [(-HALF, HALF, -3, HALF), (3, HALF, HALF, HALF), (-HALF, -HALF, -3, -HALF), (3, -HALF, HALF, -HALF),
                             (-HALF, -HALF, -HALF, HALF), (HALF, -HALF, HALF, HALF)]:
        box_wall(a, 'stone', x0, z0, x1, z1, -1, 7, thick=1.6, uvs=0.25)
    for xx in (-4, 4):
        a.geo('stone', xx, HALF).box((xx - 1.2, -1, HALF - 1.2), (xx + 1.2, 9, HALF + 1.2), uvs=0.25)
        a.geo('thatch', xx, HALF).cone((xx, 9, HALF), 1.9, 2.5, 8)
    if era == 'fresh':
        a.loadzone(0, 0, HALF - 0.9, 5, 4, 1.2, to='fields', at='town')
    a.spawn_point('start', 0, 0.1, HALF - 4, 0)
    a.spawn_point('fields', 0, 0.1, HALF - 4, 0)
    a.spawn_point('castle', 0, height(0, -34) + 0.1, -34, 180)
    # the castle road and its gate
    if risen:
        a.blocker(0, height(0, -36), -36, (7.6, 3.0, 0.6), 'never', material='hedge', color='#506040ff')
        a.entity('Spire', t3((0, -4, -58)), mesh('model', '#5a6a48ff', 'art/mould.png', file='models/spire.obj', cast=False))
        a.sign(3.4, height(3.4, -27), -27, 180, 'spire')
    else:
        a.loadzone(0, height(0, -HALF + 1), -HALF + 0.9, 5, 4, 1.2, to='castle', at='start', until='storm_now')
        a.npc('guard', -3.2, height(-3.2, -36), -36, 160, until='storm_now')
        a.sign(3.4, height(3.4, -27), -27, 180, 'sign_castle')
        # the night of the storm (storm.bs): the runners wait out of sight
        a.entity('Storm', t3((0, 0, 0)), script('scripts/storm.bs'))
        for name, model in [('Saffron Runner', 'saffron'), ('Kimchi Runner', 'kimchi'), ('Mildew', 'mildew')]:
            a.entity(name, t3((0, -50, 0)), mesh('model', file='models/%s.glb' % model, shadow=True),
                     ('Animator', [('clip', q('idle')), ('speed', 1), ('loop', True), ('playing', True), ('blend', 0.2)]))
        a.entity('Kettle Whistle', t3((6, -2.9, MOAT)), mesh('model', '#c0c8e0ff', file='models/jar.obj', lit=False),
                 script('scripts/sunken.bs', item='whistle', id='moat_whistle', then='whistle_vision', when='whistle_thrown'))

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
    if risen:
        for x, z in [(-6, 16), (-2, 4), (-12, -8), (-4, -14)]:
            a.enemy('stalebie', x, 0, z, hp=4, damage=2, always=True)
    else:
        a.npc('baker', -9, 0, 13.6, 180, until='storm_now')
        a.npc('townswoman', 9, 0, 13.6, 180, until='storm_now')
        a.npc('townsman', 3.5, 0, 4, 250, until='storm_now')
        a.npc('gossip', -4, 0, 20, 30, model='townswoman', until='storm_now')
        a.npc('child', 5, 0, 21, 200, model='mint', until='storm_now')
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
    if not risen:
        a.npc('pip', -21.2, 0, 0, 270, until='storm_now')
    a.sign(-21.5, 0, 3.8, 270, 'sign_kitchens')
    # the Temple of the First Hearth (east)
    tx, tz = 26, -4
    a.geo('stone', tx, tz).box((tx - 6, -0.3, tz - 7), (tx + 6, 7, tz + 7), uvs=0.25, sides=('px', 'nx', 'pz', 'nz', 'py'))
    a.geo('stone', tx, tz).box((tx - 7, -0.3, tz - 8), (tx + 7, 0.4, tz + 8), uvs=0.25)
    for zz in (-5, -1.5, 1.5, 5):
        a.geo('stone', tx - 6.8, tz + zz).cylinder((tx - 6.8, 0.4, tz + zz), 0.45, 6.4, 8, uvs=0.5)
    a.geo('thatch', tx, tz).cylinder((tx, 7, tz), 8.2, 3.2, 4, top=False, radius_top=0.4, uvs=0.25)
    a.entity('Temple Door', t3((tx - 6.05, 2.2, tz), (0, 90, 0), (2.4, 3.6, 0.1)), mesh('cube', '#201810ff', lit=False))
    a.loadzone(tx - 6.5, 0.4, tz, 0.8, 3, 2.4, to='temple', at='start')
    a.spawn_point('temple', tx - 9, 0.5, tz, 90)
    if risen:
        a.npc('cinder', tx - 9, 0.4, tz + 3.5, 100, needs='met_mozz', reach=2.4)
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
    if risen:
        a.loadzone(0, 0, HALF - 0.9, 5, 4, 1.2, to='', say='tbc_risen')
    a.save()


def build_risen():
    build('risen')
