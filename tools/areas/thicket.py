"""The Thicket of Thyme: the deep wood east of Breadbasket Fields.

North is -z. The way in from the field is at the west. Hedge-walled paths wind east
through the wood (with dead ends), to the Glade: a clearing where an old stair climbs
toward the Thyme Temple's door on a high ledge. The stair crumbled long ago; a wooden
target on the ledge is the only way across (the Licorice Lash, in the Risen era). In the
Risen era the wood is crawling with mould.
"""
import math
import random

from areakit import Area
from kit import drawn, t3, mesh, collider, tags, script, particles

PATHS = [[(-50, 0), (-20, 0), (-20, -20), (10, -20), (10, 10), (32, 10), (40, 0)],
         [(-20, -10), (-36, -10), (-36, -22)],          # a dead end (a chest)
         [(10, -6), (24, -12)]]                           # a dead end (pots)
GLADE = (40.0, 0.0, 11.0)
LEDGE_X = 47.0
LEDGE_Y = 5.0


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def path_dist(x, z):
    best = 1e9
    for path in PATHS:
        for (x0, z0), (x1, z1) in zip(path, path[1:]):
            dx, dz = x1 - x0, z1 - z0
            L2 = dx * dx + dz * dz
            t = max(0.0, min(1.0, ((x - x0) * dx + (z - z0) * dz) / L2))
            best = min(best, math.hypot(x - (x0 + dx * t), z - (z0 + dz * t)))
    return best


def is_open(x, z):
    return path_dist(x, z) < 3.4 or math.hypot(x - GLADE[0], z - GLADE[1]) < GLADE[2]


def height(x, z):
    return 0.25 * math.sin(x * 0.3) * math.cos(z * 0.27)


def build(era='fresh'):
    global height
    random.seed(61)
    risen = era == 'risen'
    a = Area('thicket', 'Thicket of Thyme', music='music/sprouthollow.wav', kill_y=-20, sky='#5a7a50ff', fog=(12, 36),
             fog_color='#4a6a44ff', ambient=('#90b080ff', 0.6), sun=('#e0f0c0ff', 0.6), chunk=20, variant=era if risen else '')
    if risen:
        a = Area('thicket', 'Thicket of Thyme', music='music/castle.wav', kill_y=-20, sky='#3a4a38ff', fog=(10, 32),
                 fog_color='#2a3a28ff', ambient=('#708868ff', 0.55), sun=('#c0d0a0ff', 0.45), chunk=20, variant='risen')
    for cz in range(-32, 28, 10):
        for cx in range(-56, 56, 10):
            a.geo('grass', cx + 5, cz + 5).ground(cx, cz, cx + 10, cz + 10, 3, 3, height, uvs=0.3)
    height = drawn(height)        # (from here on, things are set on the ground as drawn: none float or sink)
    # hedges fill everything that isn't path or glade (only the blocks that face a path are built)
    S = 4.0
    for i in range(-14, 14):
        for j in range(-8, 7):
            x, z = i * S + S / 2, j * S + S / 2
            if is_open(x, z) or x > LEDGE_X - 2 and abs(z) < 6:
                continue
            near = any(is_open(x + dx * S, z + dz * S) for dx, dz in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)])
            if not near:
                continue
            a.geo('hedge', x, z).box((x - S / 2, -0.5, z - S / 2), (x + S / 2, 4.5, z + S / 2), uvs=0.4)
            if random.random() < 0.25:
                a.geo('canopy', x, z).sphere((x, 6.0, z), 3.2, 8, 5, squash=0.6)
    # the way in from the field (west)
    a.loadzone(-52, 0, 0, 1.0, 4, 6, to='fields', at='thicket')
    a.spawn_point('start', -46, 0.1, 0, -90)
    a.spawn_point('fields', -46, 0.1, 0, -90)
    a.sign(-44, 0, -2.6, -90, 'sign_thicket')
    a.npc('thicket_kid', -40, 0, 2.2, -120, model='dill')
    # the dead ends
    a.chest(-36, 0, -21, 0, 'slice', 'th_slice')
    for x, z in [(23, -11), (24.5, -12.5), (22.5, -13)]:
        a.pot(x, 0, z)
    # the Glade, and the crumbled stair to the temple
    gx, gz, gr = GLADE
    o = a.geo('stone', gx + 3, gz)
    x0, x1, y1 = gx - 4.0, gx + 2.0, 3.0                   # the stair: a ramp up to its broken end
    o.quad((x0, -0.4, -1.6), (x0, -0.4, 1.6), (x1, y1, 1.6), (x1, y1, -1.6), (0, 0), (0, 1), (2, 1), (2, 0))
    o.box((x1 - 0.01, -0.5, -1.62), (x1 + 0.4, y1, 1.62), uvs=0.4)      # (a hair wider than the ramp: its sides not in the ramp's)
    for sz in (-1.6, 1.6):
        o.tri((x0, 0.05, sz), (x1, -0.3, sz), (x1, y1, sz)) if sz > 0 else o.tri((x0, 0.05, sz), (x1, y1, sz), (x1, -0.3, sz))
    a.geo('stone', LEDGE_X + 3, gz).box((LEDGE_X, -0.5, gz - 6), (LEDGE_X + 6, LEDGE_Y, gz + 6), uvs=0.3)
    a.target(LEDGE_X + 1.2, LEDGE_Y + 1.39, gz + 3.5, 90)     # (its top just under the post's)
    a.geo('bark', LEDGE_X + 1.2, gz + 3.5).cylinder((LEDGE_X + 1.35, LEDGE_Y, gz + 3.5), 0.25, 1.8, 6)
    a.sign(gx - 5, 0, gz + 2.6, -90, 'sign_temple_stair')
    # the temple's door, on the ledge
    a.geo('stone', LEDGE_X + 5, gz).box((LEDGE_X + 5, LEDGE_Y, gz - 3), (LEDGE_X + 6, LEDGE_Y + 5, gz + 3), uvs=0.3)
    a.entity('Temple Door', t3((LEDGE_X + 4.95, LEDGE_Y + 1.6, gz), (0, -90, 0), (2.4, 3.2, 0.1)), mesh('cube', '#101808ff', lit=False))
    a.loadzone(LEDGE_X + 4.6, LEDGE_Y, gz, 0.8, 3, 2.4, to='thymetemple', at='start')
    a.spawn_point('temple', LEDGE_X + 3.0, LEDGE_Y + 0.1, gz, 90)
    a.spawn_point('glade', gx - 6, 0.1, gz, -90)
    if risen:
        a.npc('cinder', gx - 2, 0, gz - 6, 30, needs='keeper_bitter', reach=2.4)
        for x, z in [(-28, 0), (-20, -14), (0, -20), (10, -2), (20, 10)]:
            a.enemy('fuzzball', x, 0.1, z, hp=3, damage=2)
        for x, z in [(-36, -16), (10, 4)]:
            a.enemy('larva', x, 0.1, z, hp=2, damage=2)
    else:
        a.npc('thicket_kid', gx - 3, 0, gz - 5, 60, model='mint')
    for x, z in [(gx - 8, gz - 6), (gx - 8, gz + 7), (gx + 2, gz - 8)]:
        a.tree(x, 0, z, 1.3, random.choice(['', 'heart', 'bean1']))
    n = 0
    while n < 30:
        x, z = random.uniform(-48, 40), random.uniform(-26, 18)
        if not is_open(x, z) or path_dist(x, z) < 1.2:
            continue
        a.grass(x, height(x, z), z)
        n += 1
    a.save()


def build_risen():
    build('risen')
