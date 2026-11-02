"""Sprouthollow: the hidden village of the Sprouts, where the game begins.

North is -z. The village green is in the middle; Mother Starter's grove is on a raised
plateau to the north (up the grove path, past Chive); the Kitchen Garden maze is to the
west, the training field to the east, and the bridge out to the south over a ravine.
"""
import math
import random

from areakit import Area, stump_house, box_wall
from kit import drawn, t3, mesh, collider, tags, script, particles, q

R_EDGE = 40.0


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


# The stream: out of the east bank, round the east side of the village (clear of its houses
# and paths), and over the lip into the ravine in a little waterfall.
STREAM_KEYS = [(38.5, 18.0), (31.0, 18.5), (24.0, 17.0), (20.0, 20.5), (18.0, 26.0), (17.0, 31.0), (16.8, 33.2)]


def _stream_line(n=12):
    """STREAM_KEYS smoothed (Catmull-Rom), n points a span."""
    k = [STREAM_KEYS[0]] + STREAM_KEYS + [STREAM_KEYS[-1]]
    out = []
    for i in range(1, len(k) - 2):
        p0, p1, p2, p3 = k[i - 1], k[i], k[i + 1], k[i + 2]
        for j in range(n):
            t = j / n
            out.append(tuple(0.5 * (2 * p1[c] + (-p0[c] + p2[c]) * t + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * t * t
                                    + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * t ** 3) for c in range(2)))
    out.append(STREAM_KEYS[-1])
    return out


STREAM = _stream_line()


def stream_d(x, z):
    """Distance from the stream's middle line."""
    best = 99.0
    for (ax, az), (bx, bz) in zip(STREAM, STREAM[1:]):
        dx, dz = bx - ax, bz - az
        L2 = dx * dx + dz * dz or 1e-9
        t = max(0.0, min(1.0, ((x - ax) * dx + (z - az) * dz) / L2))
        best = min(best, math.hypot(x - ax - dx * t, z - az - dz * t))
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
    # the ravine to the south (closing up at its ends, east and west, before the rim)
    if z > 33 and z < 42:
        h -= 9 * smooth((z - 33) / 1.5) * smooth((42 - z) / 1.5) * smooth((34 - abs(x)) / 4)
    # the stream
    d = stream_d(x, z) if z < 33 else 99
    h -= 0.45 * smooth((1.8 - d) / 1.2)
    # the bowl's rim (further out behind the grove, where Mother Starter sits)
    edge = R_EDGE
    if z < -26:
        edge = R_EDGE + 14 * smooth((16 - abs(x)) / 4)
    if 28 < z < 49:                               # the way out south: a cutting through the rim, level with the bridge
        edge = R_EDGE + 16 * smooth((6.5 - abs(x)) / 3)
    h += 9 * smooth((r - edge) / 5)
    return h


def ground_y(x, z):
    return height(x, z)


def build():
    global height
    random.seed(7)
    a = Area('sprouthollow', 'Sprouthollow', music='music/sprouthollow.wav', kill_y=-6, sky='#b8e0f0ff', fog=(60, 115),
             fog_color='#c8e8d8ff', ambient=('#8898b8ff', 0.55))
    # ---- the ground ----
    for cz in range(-48, 60, 12):
        for cx in range(-48, 48, 12):
            if cz >= 48 and abs(cx + 6) > 12:
                continue                       # (beyond the rim: only behind the way out)
            a.geo('grass', cx + 6, cz + 6).ground(cx, cz, cx + 12, cz + 12, 6, 6, height, uvs=0.25,
                                                   keep=lambda x, z: not (32 < z < 42 and abs(x) < 36))
    # the ravine's sides (cliff faces) and floor (it closes up before x reaches 36 either way),
    # from z 32: the grass's 2m cells would slope its lip down from there under the bridge's end
    for cx in range(-36, 36, 12):
        o = a.geo('cliff', cx + 6, 37)
        o.ground(cx, 32.0, cx + 12, 42.0, 6, 10, height, uvs=0.3)
    height = drawn(height)        # (from here on, things are set on the ground as drawn: none float or sink)
    # dirt paths: thin strips just above the ground
    a.path([(0, 32), (0, 20), (-2, 8), (0, -4), (0, -16), (0, -27), (0, -36)], 2.4)
    a.path([(0, -4), (12, -6), (22, -6), (28, -4)], 1.8)
    a.path([(-2, 8), (-12, 6), (-22, 2), (-25, 0)], 1.8)
    a.path([(-2, 8), (-8, 15)], 1.6)
    a.path([(0, 20), (14, 14)], 1.6)
    # the stream's water (a ribbon along its line), and its fall into the ravine
    W2 = 1.4
    sides = []
    for i, (x, z) in enumerate(STREAM):
        (ax, az), (bx, bz) = STREAM[max(0, i - 1)], STREAM[min(len(STREAM) - 1, i + 1)]
        L = math.hypot(bx - ax, bz - az) or 1
        nx, nz = -(bz - az) / L * W2, (bx - ax) / L * W2
        sides.append(((x - nx, -0.22, z - nz), (x + nx, -0.22, z + nz)))
    run = 0.0
    for i in range(len(STREAM) - 1):
        (l0, r0), (l1, r1) = sides[i], sides[i + 1]
        seg = math.hypot(STREAM[i + 1][0] - STREAM[i][0], STREAM[i + 1][1] - STREAM[i][1])
        o = a.geo('water', STREAM[i][0], STREAM[i][1])
        q4 = [l0, l1, r1, r0]
        if (q4[1][0] - q4[0][0]) * (q4[2][2] - q4[0][2]) - (q4[1][2] - q4[0][2]) * (q4[2][0] - q4[0][0]) > 0:
            q4 = q4[::-1]                             # (facing up)
        uv = {id(l0): (0, run / 3), id(r0): (1, run / 3), id(l1): (0, (run + seg) / 3), id(r1): (1, (run + seg) / 3)}
        o.quad(*q4, *[uv[id(v)] for v in q4])
        run += seg
    fx_, fz_ = STREAM[-1]
    (fl, fr) = sides[-1]
    o = a.geo('water', fx_, fz_ + 1)
    for (y0, y1, dz0, dz1) in [(-0.22, -8.6, 0.0, 1.3)]:      # (down the ravine's north face, leaning out a little)
        A, B = (fl[0], y0, fl[2] + dz0), (fr[0], y0, fr[2] + dz0)
        C, D = (fr[0], y1, fr[2] + dz1), (fl[0], y1, fl[2] + dz1)
        o.quad(A, B, C, D, (0, 0), (1, 0), (1, 3), (0, 3))
    a.entity('Falls Spray', t3((fx_, -8.4, fz_ + 1.6)), particles(rate=14, max=40, lifetime=1.0, speed=1.6, spread=60, area=(2.2, 0.6), gravity=2,
                                                                size_start=0.35, size_end=0.8, color_start='#ffffffb0', color_end='#ffffff00'))
    a.entity('Falls Mist', t3((fx_, -0.1, fz_ + 0.2)), particles(rate=5, max=14, lifetime=1.2, speed=0.5, spread=40, area=(2.4, 0.4), gravity=-0.2,
                                                               size_start=0.2, size_end=0.5, color_start='#ffffff80', color_end='#ffffff00'))
    # the bridge over the ravine
    a.geo('planks', 0, 37).box((-1.4, -0.25, 31.8), (1.4, 0.05, 42.8), uvs=0.6)
    # stone footings under both ends, bedded in the banks
    for (z0, z1) in [(31.8, 33.8), (40.6, 42.8)]:
        a.geo('stone', 0, (z0 + z1) / 2).box((-1.7, -4.5, z0), (1.7, -0.3, z1), uvs=0.4)
    for zz in (32.6, 37.5, 42.4):
        for xx in (-1.5, 1.5):
            a.geo('bark', xx, zz).cylinder((xx, -0.3, zz), 0.12, 1.2, 6, uvs=1)
    a.entity('Rail', t3((-1.5, 0.8, 37.5), (0, 0, 0), (0.1, 0.1, 10)), mesh('cube', '#ffffffff', 'art/bark.png'), collider('box'))
    a.entity('Rail', t3((1.5, 0.8, 37.5), (0, 0, 0), (0.1, 0.1, 10)), mesh('cube', '#ffffffff', 'art/bark.png'), collider('box'))
    # past the bridge, the way out: a cutting through the rim to a dark archway in the herb roots
    a.path([(0, 42.6), (0, 47.6)], 2.4)
    for xx in (-2.3, 2.3):
        a.geo('bark', xx, 47.9).box((xx - 0.35, -0.3, 47.55), (xx + 0.35, 3.4, 48.25), uvs=0.6)
    a.geo('bark', 0, 47.9).box((-2.9, 3.4, 47.5), (2.9, 4.1, 48.3), uvs=0.6)
    # (through it: the fields, the slice of them Area.make_previews puts past the way out)

    # ---- the giant herb stalks round the hollow, and a canopy far overhead ----
    for i in range(30):
        ang = 2 * math.pi * i / 30 + random.uniform(-0.05, 0.05)
        rr = random.uniform(43, 47)
        x, z = math.cos(ang) * rr, math.sin(ang) * rr
        if abs(x) < 4 and z > 30:
            continue
        rad = random.uniform(1.2, 2.2)
        # (its foot below the ground all round it: they stand on the rim's slope)
        base = min(height(x + math.cos(k * math.pi / 4) * rad, z + math.sin(k * math.pi / 4) * rad) for k in range(8)) - 0.6
        a.geo('bark', x, z).cylinder((x, base, z), rad, 26 + height(x, z) - base - 1, 8, top=False, uvs=0.25, radius_top=rad * 0.7)
    for i in range(12):
        ang = 2 * math.pi * i / 12
        x, z = math.cos(ang) * 36, math.sin(ang) * 36
        a.geo('canopy', x, z).sphere((x, 24, z), 16, 8, 4, squash=0.25, uvs=3)

    # ---- the grove plateau's edge: hedges, with a gap for the path ----
    # (thick enough to hold the whole slope up to the plateau inside it: walking down the
    # slope can't push Sprig into one)
    box_wall(a, 'hedge', -18, -26.8, -2.4, -26.8, 0, 3.6, thick=1.6)
    box_wall(a, 'hedge', 2.4, -26.8, 18, -26.8, 0, 3.6, thick=1.6)
    box_wall(a, 'hedge', -18, -26.3, -26, -40, 0, 4.0, thick=1.0)
    box_wall(a, 'hedge', 18, -26.3, 26, -40, 0, 4.0, thick=1.0)
    # the gate posts and Chive's fence
    for xx in (-2.8, 2.8):
        a.geo('bark', xx, -18).cylinder((xx, height(xx, -18) - 0.2, -18), 0.25, 2.2, 8, uvs=1)
    a.blocker(0, height(0, -18), -18, (5.2, 1.4, 0.2), 'chive_moved')
    # hedges along both sides of the grove path, from the gate posts up to the plateau's
    # hedge: no way round Chive's fence on to the path's low end
    for xx in (-2.95, 2.95):
        box_wall(a, 'hedge', xx, -17.84, xx, -26.4, -0.5, 3.6, thick=1.0)
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
        box_wall(a, 'bark', px, pz, qx, qz, deck_y - 0.1, deck_y + 0.75 + 0.012 * (k % 2), thick=0.4)   # (tops a hair apart where they meet)
    a.entity('Bed', t3((tx - 0.6, deck_y + 0.2, tz - 0.6), (0, 30, 0), (1.0, 0.35, 1.8)), mesh('cube', '#ffffffff', 'art/planks.png'), collider('box'))
    # the blanket over its foot end and a pillow at its head: placed along the bed (turned 30 degrees), not the world's axes
    bx, bz, by = tx - 0.6, tz - 0.6, deck_y + 0.2
    along = (math.sin(math.radians(30)), math.cos(math.radians(30)))      # (the bed's own +z: towards its foot)
    a.entity('Blanket', t3((bx + along[0] * 0.3, by + 0.2, bz + along[1] * 0.3), (0, 30, 0), (1.02, 0.1, 1.16)), mesh('cube', '#7ab868ff'))
    a.entity('Pillow', t3((bx - along[0] * 0.62, by + 0.23, bz - along[1] * 0.62), (0, 30, 0), (0.7, 0.12, 0.4)), mesh('cube', '#f0ead8ff'))
    # the vine ladder down the south side (facing +z... out of the deck)
    # (hanging from the deck's edge, which stands out past the stump: he climbs out round it)
    a.vine(tx + 0.0, height(tx, tz + 3.0), tz + 3.0, 1.0, deck_y - height(tx, tz + 3.0), 180, top=deck_y, gap=0.035)   # (on the board's face)
    # (they grow up a board, from the ground to the deck's edge: something to hold on to)
    a.geo('bark', tx, tz + 2.9).box((tx - 0.65, height(tx, tz + 3.0) - 0.3, tz + 2.78), (tx + 0.65, deck_y - 0.21, tz + 3.0), uvs=0.6)
    # the bridge gap on the deck rail: the vines come up there (no rail post in the way)
    a.spawn_point('bed', tx + 0.4, deck_y + 0.05, tz - 0.2, 200)
    # Sprig's savings, by the bed: with the beans about the village (and in the trees), enough
    # for Sage's shield (40) without counting on lucky drops
    a.chest(tx + 1.73, deck_y, tz - 1.0, 120, 'bean20', 'deck_chest')
    for k in range(5):
        ang = 2 * math.pi * k / 5 + 1.2
        a.pickup('bean1', tx + math.cos(ang) * 1.6, deck_y + 0.15, tz + math.sin(ang) * 1.6, id='deck%d' % k)

    # ---- Sage's shop: a stall with a counter and an awning ----
    sx, sz = 13, -7
    sy = height(sx, sz)
    a.geo('planks', sx, sz).box((sx - 2.2, sy - 0.2, sz - 0.4), (sx + 2.2, sy + 1.0, sz + 0.4), uvs=0.8)
    # the awning slopes down to the back; its posts stand right up under it
    aw_y, aw_tilt, aw_z = sy + 3.0, 12.0, sz - 1.3
    def under_awning(zz):              # the awning's underside at zz
        return aw_y - 0.075 / math.cos(math.radians(aw_tilt)) + (zz - aw_z) * math.tan(math.radians(aw_tilt))
    a.geo('planks', sx, sz).box((sx - 2.6, sy - 0.2, sz - 3.6), (sx + 2.6, under_awning(sz - 3.2) - 0.02, sz - 3.2), uvs=0.6)
    for xx in (-2.4, 2.4):
        for zz in (sz + 0.3, sz - 3.2):
            a.geo('bark', sx + xx, sz).cylinder((sx + xx, sy - 0.1, zz), 0.12, under_awning(zz) + 0.05 - (sy - 0.1), 6, uvs=1)
    a.entity('Awning', t3((sx, aw_y, aw_z), (-aw_tilt, 0, 0), (5.8, 0.15, 4.6)), mesh('cube', '#e8a858ff', 'art/thatch.png'))
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
    trees = [(-14, -18, 1.2, 'bean5'), (10, -18, 1.1, 'bean5'), (22, 8, 1.0, 'heart'), (-24, 20, 1.2, 'bean1'), (26, 22, 1.1, 'bean5'),
             (-30, 26, 1.0, ''), (32, 12, 1.2, 'bean5'), (18, -18, 1.0, 'bean5'), (-14, 28, 1.0, 'bean1'), (11, 30, 1.0, '')]
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
    # Fennel at the bridge out: she won't let Sprig leave before the Crock (fennelstop.bs), and
    # gives him her pipe after it; then she steps aside
    a.npc('fennel', 1.0, height(1.0, 31.4), 31.4, 0, until='fennel_bridge')
    a.npc('fennel', 3.2, height(3.2, 30.2), 30.2, 220, needs='fennel_bridge')
    a.entity('Fennel Stop', t3((0, 1.0, 30.6)), collider('box', (5.0, 2.0, 1.2), trigger=True), tags('loadzone'),
             script('scripts/fennelstop.bs'))
    # ... and the bridge itself is shut till then: an unseen wall across its end (gone with the Crock)
    a.entity('Bridge Shut', t3((0, height(0, 31.6) + 1.5, 31.6), (0, 0, 0), (5.0, 3.0, 0.4)), collider('box'),
             script('scripts/blocker.bs', until='crock_done'))
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
    # the Crock's Heart Pie, if Sprig left the Queen's lair without it (the Crock's shut after):
    # it waits beside Mother Starter's mouth (the same id: found in one place, gone from both)
    a.entity('Heart Pie', t3((cx + 2.8, gy + 0.8, cz + 6.2), (0, 0, 0), 2.0), mesh('model', '#ff3048ff', file='models/heart.obj', lit=False),
             script('scripts/pickup.bs', kind='heartpie', id='crock_pie', when='crock_done'))

    # ---- ways out ----
    a.loadzone(0, 0, 45, 4, 3, 1, to='fields', at='sprouthollow', needs='crock_done')
    a.spawn_point('fields', 0, height(0, 30) + 0.1, 30, 0)
    a.spawn_point('start', 0, height(0, 26) + 0.1, 26, 0)
    a.spawn_point('crock', 0, gy + 0.1, cz + 8, 0)
    a.area_map([('FIELDS', 0, 46, 's'), ('MOTHER STARTER', 0, -44, ''), ('HOME', -8, 18, ''), ("SAGE'S", 13, 3, ''),
                ('TRAINING', 30, -19, ''), ('GARDEN', -31, 2, '')], bounds=(-42, -50, 42, 46))
    a.save()
