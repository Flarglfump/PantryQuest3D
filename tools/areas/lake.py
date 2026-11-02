"""Lake Brine: the great salt lake at the south-west of the kingdom.

North is -z. Brine Valley's river comes in at the north. The lake fills the middle, with
an island in it (a sunken door: the Fizzwater Temple, shut for now) joined to the south
shore by a long plank bridge. Professor Brineworth's lab stands on the east shore, the
fishing pond's hut on the west. Something glints on the lake bed near the island.
"""
import math
import random

from areakit import Area, town_house
from kit import drawn, t3, mesh, collider, tags, script, particles

HALF = 70.0
SURF = 0.0
CX, CZ = 0.0, -6.0


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def height(x, z):
    r = math.hypot(x - CX, z - CZ)
    h = -7.0 + 8.2 * smooth((r - 36) / 10)                      # the lake bowl; shore at 1.2
    ri = math.hypot(x - CX, z - CZ)
    h = max(h, 1.6 - 9 * smooth((ri - 7) / 5))                   # the island
    if abs(x) < 7 and z < -HALF + 18:                            # the river coming in
        h = min(h, -2.5 + 3.7 * smooth((abs(x) - 4) / 3))
    d = max(abs(x), abs(z)) - (HALF - 6)
    if d > 0 and not (abs(x) < 12 and z < 0):
        h += 10 * smooth(d / 4)
    return h + 0.3 * math.sin(x * 0.3) * math.cos(z * 0.25) * smooth((r - 46) / 4)


def build(era='fresh'):
    global height
    random.seed(53)
    risen = era == 'risen'
    a = Area('lake', 'Lake Brine', music='music/brine.wav', kill_y=-20, sky='#b8e0f8ff' if not risen else '#a0b0c0ff', fog=(80, 170),
             ambient=('#8898b8ff', 0.55), chunk=28, variant=era if risen else '')
    a.entity('Sky', t3((0, 0, 0)), script('scripts/sky.bs'))
    for cz in range(-70, 70, 14):
        for cx in range(-70, 70, 14):
            r = math.hypot(cx + 7 - CX, cz + 7 - CZ)
            mat = 'sand' if r < 46 else 'grass'
            a.geo(mat, cx + 7, cz + 7).ground(cx, cz, cx + 14, cz + 14, 5, 5, height, uvs=0.25)
    height = drawn(height)        # (from here on, things are set on the ground as drawn: none float or sink)
    a.water(-48, -54, 48, 40, SURF, depth=9)
    a.water(-7, -70, 7, -54, SURF, depth=4)
    # ---- the way in from Brine Valley (north) ----
    a.loadzone(-9.5, height(-9.5, -HALF + 2), -HALF + 1.5, 4, 5, 1.5, to='gorge', at='lake')
    a.spawn_point('start', -9.5, height(-9.5, -60) + 0.1, -60, 180)
    a.spawn_point('gorge', -9.5, height(-9.5, -60) + 0.1, -60, 180)
    a.sign(-12.5, height(-12.5, -57), -57, 180, 'sign_lake')
    # the bridge from the south shore to the island
    a.geo('planks', 0, 20).box((-1.4, 1.0, CZ + 6), (1.4, 1.35, 46), uvs=0.5)
    for z in range(int(CZ) + 8, 46, 5):
        for xx in (-1.3, 1.3):
            a.geo('bark', xx, z).cylinder((xx, -7, z), 0.18, 8.9, 6, uvs=1)
            a.geo('bark', xx, z).box((xx - 0.08, 1.35, z - 2.5), (xx + 0.08, 2.0, z + 2.5), uvs=0.5)
    # the island and its sunken door
    a.geo('stone', CX, CZ).cylinder((CX, 1.4, CZ), 3.0, 0.4, 12, uvs=0.4)
    a.spawn_point('island', CX, 1.9, CZ + 1.5, 180)
    if risen:      # the temple's door, down on the lake bed north of the island
        tz = CZ - 15
        ty = height(CX, tz)
        a.geo('stone', CX, tz).box((CX - 3, ty - 0.5, tz - 2), (CX + 3, ty + 5, tz - 1), uvs=0.3)
        a.entity('Temple Door', t3((CX, ty + 1.6, tz - 0.95), (0, 0, 0), (2.6, 3.0, 0.1)), mesh('cube', '#0a1828ff', lit=False))
        a.loadzone(CX, ty, tz - 0.6, 2.4, 3, 0.6, to='brinetemple', at='start')
        a.spawn_point('brinetemple', CX, ty + 0.1, tz + 2, 180)
        a.entity('Temple Door Sign', t3((CX, 0.99, CZ - 2.6), (0, 0, 0), (2.2, 1.56, 0.2)), mesh('cube', '#4a6a8aff', 'art/stone.png'),
                 collider('box'), tags('interact'), script('scripts/sign.bs', say='lake_temple_door', prompt='Look', reach=2.4))
    else:
        a.entity('Temple Door', t3((CX, 0.99, CZ - 2.6), (0, 0, 0), (2.2, 1.56, 0.2)), mesh('cube', '#4a6a8aff', 'art/stone.png'),
                 collider('box'), tags('interact'), script('scripts/sign.bs', say='tbc_lake_temple', prompt='Look', reach=2.4))
    a.tree(CX + 4, height(CX + 4, CZ + 3), CZ + 3, 1.4, 'heart')
    # what glints on the lake bed: a jar with a letter in it
    jx, jz = 14.0, CZ - 12.0
    if not risen:
      a.entity('Sunken Jar', t3((jx, height(jx, jz) + 0.3, jz)), mesh('model', '#c8e8ffd0', file='models/jar.obj', lit=False),
             script('scripts/sunken.bs', item='jar1', id='lake_jar', then='fizzy_letter_read'))
    if not risen:
      a.entity('Glint', t3((jx, height(jx, jz) + 0.6, jz)), particles(rate=3, max=8, lifetime=1.0, speed=0.3, spread=40, area=(0.4, 0.4),
                                                                     size_start=0.25, size_end=0, color_start='#ffffffff', color_end='#a0e0ff00', blend='add'))
    # Professor Brineworth's lab (east shore)
    lx, lz = 52, 10
    town_house(a, lx, lz, 7, 6, 4.0, height(lx, lz), wall='stone', roof='planks', door_side='w')
    a.npc('professor', lx - 5, height(lx - 5, lz + 2), lz + 2, -100)
    # the fishing pond's hut (west shore)
    fx, fz = -52, 12
    town_house(a, fx, fz, 6, 6, 3.6, height(fx, fz), wall='planks', roof='thatch', door_side='e')
    a.sign(fx + 5, height(fx + 5, fz - 2), fz - 2, -90, 'sign_fishing')
    for x, z in [(30, -40), (-34, -44), (40, 40), (-40, 44), (56, -20), (-58, -16), (24, 52), (-22, 54)]:
        a.tree(x, height(x, z), z, random.uniform(1.0, 1.5), random.choice(['', 'bean1', 'heart']))
    for x, z in [(-28, 44), (34, -48), (-46, -30)]:
        a.enemy('fuzzball', x, height(x, z) + 0.1, z, hp=2, damage=2)
    for x, z in [(lx - 4, lz - 4), (lx - 4.6, lz - 3.2), (fx + 4, fz + 4)]:
        a.pot(x, height(x, z), z)
    n = 0
    while n < 30:
        x, z = random.uniform(-60, 60), random.uniform(-60, 60)
        if math.hypot(x - CX, z - CZ) < 47 or abs(x) < 3:
            continue
        a.grass(x, height(x, z), z)
        n += 1
    a.save()


def build_risen():
    build('risen')
