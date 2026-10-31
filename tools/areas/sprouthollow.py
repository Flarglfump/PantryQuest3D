"""Sprouthollow: the hidden village of the Sprouts, where the game begins.

North is -z. The village green is in the middle; Mother Starter's grove is on a raised
plateau to the north (up the grove path, past Chive); the Kitchen Garden maze is to the
west, the training field to the east, and the bridge out to the south over a ravine.
"""
import math
import random

from areakit import Area, stump_house, box_wall
from kit import t3, mesh, collider, tags, script, particles, q

R_EDGE = 40.0


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def stream_d(x, z):
    """Distance from the stream's middle line (it runs from the east edge, curving south-west)."""
    best = 99.0
    for i in range(41):
        t = i / 40
        sx = 42 - t * 50
        sz = -6 + 30 * t + 6 * math.sin(t * 5)
        best = min(best, math.hypot(x - sx, z - sz))
    return best


def height(x, z):
    r = math.hypot(x, z)
    h = 0.12 * math.sin(x * 0.31) * math.cos(z * 0.27)
    # the grove plateau (north)
    if z < -26:
        h += 2.5 * smooth((-26 - z) / 1.2) if abs(x) < 18 else 2.5 * smooth((-26 - z) / 1.2)
    # the grove path: a ramp up through the gap at x in -2..2, z from -18 to -26
    if abs(x) < 2.4 and -27 < z < -17:
        h = max(h, 2.5 * smooth((-17 - z) / 9))
    # the ravine to the south
    if z > 33 and z < 42:
        h -= 9 * smooth((z - 33) / 1.5) * smooth((42 - z) / 1.5)
    # the stream
    d = stream_d(x, z) if z < 33 else 99
    h -= 0.45 * smooth((1.8 - d) / 1.2)
    # the bowl's rim (further out behind the grove, where Mother Starter sits)
    edge = R_EDGE
    if z < -26:
        edge = R_EDGE + 14 * smooth((16 - abs(x)) / 4)
    h += 9 * smooth((r - edge) / 5)
    return h


def ground_y(x, z):
    return height(x, z)


def build():
    random.seed(7)
    a = Area('sprouthollow', 'Sprouthollow', music='music/sprouthollow.wav', kill_y=-6, sky='#b8e0f0ff', fog=(26, 58),
             fog_color='#c8e8d8ff', ambient=('#8898b8ff', 0.55))
    # ---- the ground ----
    for cz in range(-48, 48, 12):
        for cx in range(-48, 48, 12):
            a.geo('grass', cx + 6, cz + 6).ground(cx, cz, cx + 12, cz + 12, 6, 6, height, uvs=0.25,
                                                   keep=lambda x, z: not (33.4 < z < 41.6))
    # the ravine's sides (cliff faces) and floor
    for cx in range(-48, 48, 12):
        o = a.geo('cliff', cx + 6, 37)
        o.ground(cx, 33.0, cx + 12, 42.0, 6, 9, height, uvs=0.3)
    # dirt paths: thin strips just above the ground
    def path_strip(points, width):
        for (x0, z0), (x1, z1) in zip(points, points[1:]):
            n = max(1, int(math.hypot(x1 - x0, z1 - z0) / 1.5))
            for i in range(n):
                ax, az = x0 + (x1 - x0) * i / n, z0 + (z1 - z0) * i / n
                bx, bz = x0 + (x1 - x0) * (i + 1) / n, z0 + (z1 - z0) * (i + 1) / n
                dx, dz = bx - ax, bz - az
                L = math.hypot(dx, dz) or 1
                px, pz = -dz / L * width / 2, dx / L * width / 2
                P = [(ax - px, az - pz), (bx - px, bz - pz), (bx + px, bz + pz), (ax + px, az + pz)]
                Y = [(p[0], max(height(p[0] + ox, p[1] + oz) for ox, oz in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1))) + 0.06, p[1]) for p in P]   # (clear of the ground's own triangles round it: no flicker)
                o = a.geo('path', ax, az)
                # (counter-clockwise from above)
                if (P[1][0] - P[0][0]) * (P[2][1] - P[0][1]) - (P[1][1] - P[0][1]) * (P[2][0] - P[0][0]) < 0:
                    o.quad(Y[0], Y[1], Y[2], Y[3], (P[0][0] / 3, P[0][1] / 3), (P[1][0] / 3, P[1][1] / 3), (P[2][0] / 3, P[2][1] / 3), (P[3][0] / 3, P[3][1] / 3))
                else:
                    o.quad(Y[3], Y[2], Y[1], Y[0], (P[3][0] / 3, P[3][1] / 3), (P[2][0] / 3, P[2][1] / 3), (P[1][0] / 3, P[1][1] / 3), (P[0][0] / 3, P[0][1] / 3))
    path_strip([(0, 32), (0, 20), (-2, 8), (0, -4), (0, -16), (0, -27), (0, -36)], 2.4)
    path_strip([(0, -4), (12, -6), (22, -6), (28, -4)], 1.8)
    path_strip([(-2, 8), (-12, 6), (-22, 2), (-25, 0)], 1.8)
    path_strip([(-2, 8), (-8, 15)], 1.6)
    path_strip([(0, 20), (14, 14)], 1.6)
    # the stream's water
    for i in range(40):
        t0, t1 = i / 40, (i + 1) / 40
        def P(t, side):
            sx = 42 - t * 50
            sz = -6 + 30 * t + 6 * math.sin(t * 5)
            tx, tz = -50, 30 + 30 * math.cos(t * 5)
            L = math.hypot(tx, tz)
            return (sx - tz / L * 1.4 * side, -0.22, sz + tx / L * 1.4 * side)
        o = a.geo('water', 42 - t0 * 50, -6 + 30 * t0)
        o.quad(P(t0, -1), P(t1, -1), P(t1, 1), P(t0, 1), (0, t0 * 20), (0, t1 * 20), (1, t1 * 20), (1, t0 * 20))
    # small plank bridges over the stream where the paths cross
    # the bridge over the ravine
    a.geo('planks', 0, 37).box((-1.4, -0.25, 32.5), (1.4, 0.05, 42.5), uvs=0.6)
    for zz in (32.6, 37.5, 42.4):
        for xx in (-1.5, 1.5):
            a.geo('bark', xx, zz).cylinder((xx, -0.3, zz), 0.12, 1.2, 6, uvs=1)
    a.entity('Rail', t3((-1.5, 0.8, 37.5), (0, 0, 0), (0.1, 0.1, 10)), mesh('cube', '#ffffffff', 'art/bark.png'), collider('box'))
    a.entity('Rail', t3((1.5, 0.8, 37.5), (0, 0, 0), (0.1, 0.1, 10)), mesh('cube', '#ffffffff', 'art/bark.png'), collider('box'))

    # ---- the giant herb stalks round the hollow, and a canopy far overhead ----
    for i in range(30):
        ang = 2 * math.pi * i / 30 + random.uniform(-0.05, 0.05)
        rr = random.uniform(43, 47)
        x, z = math.cos(ang) * rr, math.sin(ang) * rr
        if abs(x) < 4 and z > 30:
            continue
        rad = random.uniform(1.2, 2.2)
        a.geo('bark', x, z).cylinder((x, height(x, z) - 1, z), rad, 26, 8, top=False, uvs=0.25, radius_top=rad * 0.7)
    for i in range(12):
        ang = 2 * math.pi * i / 12
        x, z = math.cos(ang) * 36, math.sin(ang) * 36
        a.geo('canopy', x, z).sphere((x, 24, z), 16, 8, 4, squash=0.25, uvs=3)

    # ---- the grove plateau's edge: hedges, with a gap for the path ----
    box_wall(a, 'hedge', -18, -26.3, -2.6, -26.3, 0, 3.6, thick=1.0)
    box_wall(a, 'hedge', 2.6, -26.3, 18, -26.3, 0, 3.6, thick=1.0)
    box_wall(a, 'hedge', -18, -26.3, -26, -40, 0, 4.0, thick=1.0)
    box_wall(a, 'hedge', 18, -26.3, 26, -40, 0, 4.0, thick=1.0)
    # the gate posts and Chive's fence
    for xx in (-2.8, 2.8):
        a.geo('bark', xx, -18).cylinder((xx, height(xx, -18) - 0.2, -18), 0.25, 2.2, 8, uvs=1)
    a.blocker(0, height(0, -18), -18, (5.2, 1.4, 0.2), 'chive_moved')
    a.npc('chive', 1.2, height(1.2, -16.6), -16.6, 180, until='chive_moved')
    a.npc('chive', 4.2, height(4.2, -15.5), -15.5, 150, needs='chive_moved')
    a.sign(-3.6, height(-3.6, -16.2), -16.2, 180, 'sign_grove')

    # ---- houses ----
    houses = [(14, 14, 2.4, 120), (8, 24, 2.2, 160), (-17, -6, 2.4, 260), (-19, 13, 2.2, 240), (-6, -10, 2.0, 200)]
    for x, z, r, door in houses:
        stump_house(a, x, z, ground_y, r=r, h=2.8, door_yaw=door)
    houses.append((-8, 15, 2.2, 30))
    # Sprig's tree-house: a platform up a tree, with a ladder of vines
    tx, tz = -8, 15
    a.sign(-5.4, height(-5.4, 18.4), 18.4, 30, 'sign_house')
    # (the house above is the stump house at -8, 15; Sprig's bed is on its roof deck)
    deck_y = height(tx, tz) + 3.1
    stump_house(a, tx, tz, ground_y, r=2.2, h=2.85, door_yaw=30, roof=None)   # (its top just under the deck: not in the same plane)
    a.geo('planks', tx, tz).cylinder((tx, deck_y - 0.2, tz), 3.0, 0.2, 12, top=True, bottom=True, uvs=0.6)
    for k in range(12):                       # the rail, open where the vines come up (south, +z)
        ang0, ang1 = 2 * math.pi * (k + 0.5) / 12, 2 * math.pi * (k + 1.5) / 12
        px, pz = tx + math.cos(ang0) * 2.85, tz + math.sin(ang0) * 2.85
        a.geo('bark', px, pz).cylinder((px, deck_y, pz), 0.08, 0.85, 5, uvs=1)
        if k == 2:
            continue
        qx, qz = tx + math.cos(ang1) * 2.85, tz + math.sin(ang1) * 2.85
        box_wall(a, 'bark', px, pz, qx, qz, deck_y - 0.1, deck_y + 0.75, thick=0.4)
    a.entity('Bed', t3((tx - 0.6, deck_y + 0.2, tz - 0.6), (0, 30, 0), (1.0, 0.35, 1.8)), mesh('cube', '#ffffffff', 'art/planks.png'), collider('box'))
    a.entity('Blanket', t3((tx - 0.6, deck_y + 0.4, tz - 0.4), (0, 30, 0), (0.95, 0.1, 1.2)), mesh('cube', '#7ab868ff'))
    # the vine ladder down the south side (facing +z... out of the deck)
    a.vine(tx + 0.0, height(tx, tz + 2.5), tz + 2.45, 1.0, deck_y - height(tx, tz + 2.5), 180, top=deck_y)
    # the bridge gap on the deck rail: the vines come up there (no rail post in the way)
    a.spawn_point('bed', tx + 0.4, deck_y + 0.05, tz - 0.2, 200)
    for k in range(5):
        ang = 2 * math.pi * k / 5 + 1.2
        a.pickup('bean1', tx + math.cos(ang) * 1.6, deck_y + 0.15, tz + math.sin(ang) * 1.6, id='deck%d' % k)

    # ---- Sage's shop: a stall with a counter and an awning ----
    sx, sz = 13, -7
    sy = height(sx, sz)
    a.geo('planks', sx, sz).box((sx - 2.2, sy - 0.2, sz - 0.4), (sx + 2.2, sy + 1.0, sz + 0.4), uvs=0.8)
    a.geo('planks', sx, sz).box((sx - 2.6, sy - 0.2, sz - 3.6), (sx + 2.6, sy + 2.6, sz - 3.2), uvs=0.6)
    for xx in (-2.4, 2.4):
        a.geo('bark', sx + xx, sz).cylinder((sx + xx, sy, sz + 0.3), 0.12, 2.8, 6, uvs=1)
        a.geo('bark', sx + xx, sz).cylinder((sx + xx, sy, sz - 3.2), 0.12, 2.8, 6, uvs=1)
    a.entity('Awning', t3((sx, sy + 3.0, sz - 1.3), (-12, 0, 0), (5.8, 0.15, 4.6)), mesh('cube', '#e8a858ff', 'art/thatch.png'))
    a.npc('sage', sx, sy, sz - 1.4, 0, reach=2.9)
    for k, (xx, c) in enumerate([(-1.4, '#c0c0c8ff'), (1.3, '#80d050ff')]):
        a.entity('Wares', t3((sx + xx, sy + 1.15, sz), (0, 20, 0), 0.6), mesh('cylinder', c))
    a.sign(sx - 3.4, sy, sz + 0.8, 20, 'sign_shop')

    # ---- the training field (east) ----
    fx, fz = 29, -4
    for k, (dx, dz) in enumerate([(-3, -3), (0, -4), (3, -3)]):
        a.dummy(fx + dx, height(fx + dx, fz + dz), fz + dz, 180)
    for zz in (-10, 2):
        box_wall(a, 'planks', fx - 6, zz, fx + 6, zz, height(fx, zz) - 0.2, height(fx, zz) + 0.7, thick=0.4)
    a.sign(fx - 5, height(fx - 5, fz + 4), fz + 4, 90, 'sign_field')
    a.sign(fx - 6, height(fx - 6, fz - 6), fz - 6, 90, 'sign_spin')

    # ---- the Kitchen Garden maze (west) ----
    mx0, mx1, mz0, mz1 = -38, -24, -10, 10
    hh = 2.2
    box_wall(a, 'hedge', mx1, mz0, mx1, -1.0, 0, hh, 0.8)          # the east wall, with a gap
    box_wall(a, 'hedge', mx1, 1.0, mx1, mz1, 0, hh, 0.8)
    box_wall(a, 'hedge', mx0, mz0, mx1, mz0, 0, hh, 0.8)
    box_wall(a, 'hedge', mx0, mz1, mx1, mz1, 0, hh, 0.8)
    box_wall(a, 'hedge', mx0, mz0, mx0, mz1, 0, hh, 0.8)
    inner = [(-28, -10, -28, 6), (-32, -6, -32, 10), (-35.5, -10, -35.5, 6)]
    for x0, z0, x1, z1 in inner:
        box_wall(a, 'hedge', x0, z0, x1, z1, 0, hh, 0.7)
    a.sign(-22.2, height(-22.2, 2.2), 2.2, 270, 'sign_garden')
    # the rolling pea: back and forth along the second corridor
    a.entity('Rolling Pea', t3((-30, 0.75, -8)), mesh('sphere', '#78c040ff', uv=(1, 1)), collider('sphere', radius=0.5),
             ('RigidBody3D', [('type', 'kinematic')]), tags('platform_no'), script('scripts/roller.bs', a=(-30, 0.75, -8.5), b=(-30, 0.75, 8.5), speed=4.5, size=1.5))
    a.entity('Rolling Pea', t3((-33.75, 0.75, 8)), mesh('sphere', '#78c040ff'), collider('sphere', radius=0.5),
             ('RigidBody3D', [('type', 'kinematic')]), script('scripts/roller.bs', a=(-33.75, 0.75, 8.5), b=(-33.75, 0.75, -8.5), speed=5.0, size=1.5))
    a.chest(-37, 0, -8.6, 180, 'spoon', 'spoon')
    for x, z in [(-26, -8), (-26, 8), (-30, -9), (-33.75, 8.5), (-37, 8)]:
        a.grass(x, 0, z, 0.5)
    a.pot(-35, 0, -1)

    # ---- trees, grass and pots round the village ----
    trees = [(-14, -18, 1.2, 'bean5'), (10, -18, 1.1, ''), (22, 8, 1.0, 'heart'), (-24, 20, 1.2, 'bean1'), (26, 22, 1.1, ''),
             (-30, 26, 1.0, ''), (32, 12, 1.2, 'bean5'), (18, -18, 1.0, ''), (-14, 28, 1.0, 'bean1'), (14, 30, 1.0, '')]
    for x, z, s, drop in trees:
        a.tree(x, height(x, z), z, s, drop)
    spots = []
    while len(spots) < 46:
        x, z = random.uniform(-36, 36), random.uniform(-24, 31)
        if math.hypot(x, z) > 37 or stream_d(x, z) < 2.5 or (mx0 - 1 < x < mx1 + 1 and mz0 - 1 < z < mz1 + 1):
            continue
        if any(math.hypot(x - hx, z - hz) < hr + 1.2 for hx, hz, hr, _ in houses) or abs(x) < 2 and z < 31:
            continue
        if fx - 7 < x < fx + 7 and -11 < z < 3:
            continue
        if sx - 3 < x < sx + 3 and sz - 4 < z < sz + 2:
            continue
        spots.append((x, z))
    for x, z in spots:
        a.grass(x, height(x, z), z)
    for x, z in [(-11.5, -6.5), (-12.3, -5.6), (10.5, 16), (11.2, 17), (5.5, 21.5), (-15.8, 11), (11, -8.6), (15.4, -8.6)]:
        a.pot(x, height(x, z), z)
    a.sign(-3.4, height(-3.4, 30.5), 30.5, 0, 'sign_bridge')
    a.sign(-4, height(-4, -2), -2, 300, 'sign_roll')

    # ---- people ----
    a.npc('fennel', -3.5, height(-3.5, 4), 4, 150, until='crock_done')
    a.npc('fennel', 2.2, height(2.2, 30.5), 30.5, 200, needs='crock_done')
    a.npc('mint', -15, height(-15, -2.5), -2.5, 220)
    a.npc('dill', -13.8, height(-13.8, -3.6), -3.6, 230)
    a.npc('parsley', 8, height(8, 6), 6, 250)

    # ---- the grove path and the grove ----
    gy = 2.5
    a.enemy('fuzzball', -5, gy, -31, hp=2)
    a.enemy('fuzzball', 6, gy, -33, hp=2)
    a.enemy('scrub', 9, gy, -38, hp=1)
    for x, z in [(-8, -30), (-10, -33), (8, -29), (11, -31), (-6, -39), (6, -40), (-12, -37)]:
        a.grass(x, gy, z, 0.4)
    for x, z in [(-12, -29), (13, -35), (-14, -42)]:
        a.tree(x, gy, z, 1.1)
    # Mother Starter: a great crock with a face in the dough
    cx, cz = 0, -47
    a.geo('crock', cx, cz).cylinder((cx, gy - 0.3, cz), 4.2, 5.0, 18, top=False, radius_top=3.8, uvs=0.4)
    a.geo('crock', cx, cz).cylinder((cx, gy + 4.7, cz), 3.8, 0.35, 18, top=False, radius_top=4.2, uvs=0.4)
    a.geo('dough', cx, cz).sphere((cx, gy + 4.8, cz), 4.0, 16, 6, squash=0.5, uvs=2)
    a.entity('Mother Starter', t3((cx, gy, cz + 4.2)), collider('box', (3, 2.5, 1), offset=(0, 1.25, 0.2), trigger=True),
             tags('interact', 'focusable', 'npc'), script('scripts/starter.bs'))
    for side in (-1, 1):
        a.entity('Starter Eye', t3((cx + side * 1.3, gy + 3.4, cz + 4.0), (0, 0, 0), (0.7, 0.45, 0.2)), mesh('sphere', '#3a2a18ff', lit=False))
    a.entity('Starter Mouth', t3((cx, gy + 1.0, cz + 4.12), (0, 0, 0), (2.0, 0.25, 0.12)), mesh('cube', '#2a1a0aff', lit=False), collider('box'))
    a.entity('Starter Bubbles', t3((cx, gy + 6.2, cz)), particles(rate=3, max=20, lifetime=1.6, speed=0.3, spread=40, area=(5, 5),
                                                                gravity=-0.1, size_start=0.25, size_end=0.0,
                                                                color_start='#f0f0e0c0', color_end='#a0a09000'))
    a.loadzone(cx, gy, cz + 4.6, 1.8, 1.8, 0.8, to='crock', at='start', needs='starter_open', until='crock_done')
    a.spawn_point('grove', 0, gy + 0.1, cz + 9, 0)

    # ---- ways out ----
    a.loadzone(0, 0, 45, 4, 3, 1, to='fields', at='sprouthollow', needs='crock_done')
    a.loadzone(0, 0, 44.4, 4, 3, 1, to='', say='sprout_exit_block', until='crock_done')
    a.spawn_point('fields', 0, height(0, 30) + 0.1, 30, 0)
    a.spawn_point('start', 0, height(0, 26) + 0.1, 26, 0)
    a.spawn_point('crock', 0, gy + 0.1, cz + 8, 0)
    a.save()
