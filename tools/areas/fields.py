"""Breadbasket Fields: the open field at the heart of the kingdom, joining every region.

North is -z. Sprouthollow's bridge comes in at the south; Larder Town's gate (shut at
night) is at the north end; Buttercup Dairy sits on a hill to the east; roads lead west
to Lake Brine, north-east to Peppermill and east to the Thicket. Time passes here: at
night Stalebies rise out of the ground.
"""
import math
import random

from areakit import Area, box_wall
from kit import t3, mesh, collider, tags, script, particles, q

HALF = 96.0


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


EXITS = [  # (x, z, half-width, direction) gaps in the rim
    (0, HALF, 5, 's'), (0, -HALF, 7, 'n'), (-HALF, 60, 6, 'w'), (78, -HALF, 6, 'n'), (HALF, 40, 6, 'e')]


def rim(x, z):
    """How far into the rim a point is (0 inside the field)."""
    d = max(abs(x), abs(z)) - (HALF - 8)
    if d <= 0:
        return 0.0
    for ex, ez, w, side in EXITS:
        along = abs(x - ex) if side in 'ns' else abs(z - ez)
        near = abs(z - ez) < 14 if side in 'ns' else abs(x - ex) < 14
        if near and along < w:
            return 0.0
        if near and along < w + 4:
            d *= (along - w) / 4
    return d


def dairy_hill(x, z):
    d = math.hypot(x - 46, z - 4)
    return 4.0 * smooth((20 - d) / 8)


def height(x, z):
    h = 1.4 * math.sin(x * 0.05) * math.cos(z * 0.045) + 0.7 * math.sin(x * 0.11 + z * 0.07)
    # flatter along the main road
    road = abs(x) < 6
    if road:
        h *= 0.4 + 0.6 * smooth((abs(x) - 2) / 4)
    h = max(h, dairy_hill(x, z)) if dairy_hill(x, z) > 0.3 else h
    h += 10 * smooth(rim(x, z) / 6)
    return h


def build(era='fresh'):
    random.seed(11)
    risen = era == 'risen'
    a = Area('fields', 'Breadbasket Fields', music='music/fields.wav', kill_y=-20, sky='#b0dcf0ff', fog=(30, 64),
             ambient=('#8898b8ff', 0.55), chunk=40, variant=era if risen else '')
    a.entity('Sky', t3((0, 0, 0)), script('scripts/sky.bs'))
    for cz in range(-104, 104, 26):
        for cx in range(-104, 104, 26):
            a.geo('grass', cx + 13, cz + 13).ground(cx, cz, cx + 26, cz + 26, 4, 4, height, uvs=0.2)

    def path_strip(points, width):
        for (x0, z0), (x1, z1) in zip(points, points[1:]):
            n = max(1, int(math.hypot(x1 - x0, z1 - z0) / 4))
            for i in range(n):
                ax, az = x0 + (x1 - x0) * i / n, z0 + (z1 - z0) * i / n
                bx, bz = x0 + (x1 - x0) * (i + 1) / n, z0 + (z1 - z0) * (i + 1) / n
                dx, dz = bx - ax, bz - az
                L = math.hypot(dx, dz) or 1
                px, pz = -dz / L * width / 2, dx / L * width / 2
                P = [(ax - px, az - pz), (bx - px, bz - pz), (bx + px, bz + pz), (ax + px, az + pz)]
                Y = [(p[0], height(*p) + 0.06, p[1]) for p in P]
                U = [(p[0] / 3, p[1] / 3) for p in P]
                o = a.geo('dirt', ax, az)
                if (P[1][0] - P[0][0]) * (P[2][1] - P[0][1]) - (P[1][1] - P[0][1]) * (P[2][0] - P[0][0]) < 0:
                    o.quad(Y[0], Y[1], Y[2], Y[3], *U)
                else:
                    o.quad(Y[3], Y[2], Y[1], Y[0], U[3], U[2], U[1], U[0])
    path_strip([(0, 100), (0, 60), (-2, 30), (0, 0), (2, -40), (0, -100)], 3.2)
    path_strip([(0, 8), (16, 6), (30, 5), (38, 4)], 2.6)
    path_strip([(-1, 58), (-30, 62), (-60, 58), (-100, 60)], 2.6)
    path_strip([(1, -30), (30, -50), (60, -72), (78, -100)], 2.6)
    path_strip([(0, 78), (40, 60), (70, 44), (100, 40)], 2.6)

    # ---- Larder Town's wall and gate, at the north end ----
    wz = -HALF + 4
    for x0, x1 in [(-60, -6.5), (6.5, 60)]:
        box_wall(a, 'stone', x0, wz, x1, wz, height(x0 / 2 + x1 / 2, wz) - 2, 9, thick=2.0, uvs=0.25)
    for xx in (-7.5, 7.5):
        a.geo('stone', xx, wz).box((xx - 1.5, -2, wz - 1.5), (xx + 1.5, 11, wz + 1.5), uvs=0.25)
        a.geo('thatch', xx, wz).cone((xx, 11, wz), 2.4, 3, 8)
    a.geo('stone', 0, wz).box((-6, 7.4, wz - 1), (6, 9.5, wz + 1), uvs=0.25)
    a.entity('Town Gate', t3((0, 3.7, wz), (0, 0, 0), (12, 7.4, 0.4)), mesh('cube', '#9a8a70ff', 'art/planks.png', uv=(6, 4)),
             collider('box'), ('RigidBody3D', [('type', 'kinematic')]), script('scripts/gate.bs'))
    a.loadzone(0, height(0, -HALF + 1), -HALF + 0.5, 10, 4, 1.5, to='town', at='fields')
    a.sign(-5, height(-5, wz + 8), wz + 8, 180, 'gate_shut')

    # ---- Buttercup Dairy's hill: a fence round the top, the gate on the west ----
    hx, hz, hr = 46, 4, 10.5
    for k in range(28):
        a0, a1 = 2 * math.pi * k / 28, 2 * math.pi * (k + 1) / 28
        mid = (a0 + a1) / 2
        if abs(math.atan2(math.sin(mid), math.cos(mid)) - math.pi) < 0.25 or abs(math.atan2(math.sin(mid), math.cos(mid)) + math.pi) < 0.25:
            continue
        x0, z0 = hx + math.cos(a0) * hr, hz + math.sin(a0) * hr
        x1, z1 = hx + math.cos(a1) * hr, hz + math.sin(a1) * hr
        box_wall(a, 'planks', x0, z0, x1, z1, height(x0, z0) - 0.3, height(x0, z0) + 1.1, thick=0.4)
    for k in range(2):
        ang = math.pi + (0.3 if k else -0.3)
        a.geo('bark', hx + math.cos(ang) * hr, hz).cylinder((hx + math.cos(ang) * hr, height(hx - hr, hz) - 0.2, hz + math.sin(ang) * hr), 0.25, 2.2, 6)
    a.sign(hx - hr - 3, height(hx - hr - 3, hz + 3), hz + 3, 270, 'sign_dairy')
    # the barn's roof over the hill (the dairy itself is its own place, later)
    a.geo('planks', hx + 4, hz).box((hx + 1, height(hx, hz), hz - 4), (hx + 8, height(hx, hz) + 4, hz + 4), uvs=0.3)
    a.geo('thatch', hx + 4, hz).cylinder((hx + 4.5, height(hx, hz) + 4, hz), 5.0, 0.2, 4, top=False, radius_top=0.5, uvs=0.3)
    a.loadzone(hx - 2, height(hx - 2, hz), hz, 2.5, 3, 4, to='', say='tbc_dairy')

    # ---- the other roads out ----
    a.loadzone(-HALF + 0.5, height(-HALF + 2, 60), 60, 1.5, 4, 12, to='gorge', at='fields')
    a.spawn_point('gorge', -86, height(-86, 60) + 0.1, 60, -90)
    a.loadzone(78, height(78, -HALF + 2), -HALF + 0.5, 12, 4, 1.5, to='peppermill', at='fields')
    a.spawn_point('peppermill', 74, height(74, -84) + 0.1, -84, 150)
    a.loadzone(HALF - 0.5, height(HALF - 2, 40), 40, 1.5, 4, 12, to='thicket', at='fields')
    a.spawn_point('thicket', 86, height(86, 40) + 0.1, 40, 90)
    a.sign(-84, height(-84, 56), 56, 270, 'sign_lake')
    a.sign(70, height(70, -80), -80, 225, 'sign_peppermill')
    a.sign(4, height(4, 70), 70, 0, 'sign_fields')

    # ---- back to Sprouthollow (south) ----
    a.loadzone(0, height(0, HALF - 1), HALF - 0.5, 10, 4, 1.5, to='sprouthollow', at='fields')
    a.spawn_point('start', 0, height(0, 86) + 0.1, 86, 0)
    a.spawn_point('sprouthollow', 0, height(0, 86) + 0.1, 86, 0)
    a.spawn_point('town', 0, height(0, -80) + 0.1, -80, 180)

    # ---- Basil's travelling kitchen ----
    cx, cz = 9, 48
    cy = height(cx, cz)
    a.geo('planks', cx, cz).box((cx - 1.6, cy + 0.6, cz - 1.0), (cx + 1.6, cy + 1.7, cz + 1.0), uvs=0.6)
    for dx in (-1.1, 1.1):
        for dz in (-1.05, 1.05):
            a.entity('Wheel', t3((cx + dx, cy + 0.5, cz + dz), (0, 0, 90), (1.0, 0.12, 1.0)), mesh('cylinder', '#ffffffff', 'art/bark.png'))
    a.entity('Cart Roof', t3((cx, cy + 2.9, cz), (0, 0, 8), (3.8, 0.12, 2.6)), mesh('cube', '#d84a3aff', 'art/thatch.png'))
    for dx in (-1.5, 1.5):
        a.geo('bark', cx + dx, cz).cylinder((cx + dx, cy + 1.6, cz - 0.9), 0.07, 1.3, 5)
    a.entity('Pot', t3((cx - 0.6, cy + 1.7, cz), (0, 0, 0), (0.5, 0.4, 0.5)), mesh('cylinder', '#505058ff'))
    a.entity('Steam', t3((cx - 0.6, cy + 2.1, cz)), particles(rate=5, max=20, lifetime=1.6, speed=0.5, spread=20, gravity=-0.3,
                                                              size_start=0.2, size_end=0.5, color_start='#ffffff90', color_end='#ffffff00'))
    if not risen:
        a.npc('basil', cx - 0.3, cy, cz - 1.9, 200, reach=2.6)

    # ---- the owl, on a post by the road from Sprouthollow ----
    ox, oz = 3.5, 78
    a.geo('bark', ox, oz).cylinder((ox, height(ox, oz) - 0.2, oz), 0.2, 2.2, 6)
    if not risen:
        a.entity('Owl', t3((ox, height(ox, oz) + 2.0, oz), (0, 160, 0), 0.9), mesh('model', file='models/owl.glb'),
                 ('Animator', [('clip', q('idle')), ('speed', 1), ('loop', True), ('playing', True), ('blend', 0.2)]),
                 tags('npc', 'focusable'), script('scripts/npc.bs', who='owl', auto=True, leaves=True))

    # ---- trees, rocks, grass ----
    def clear(x, z, r):
        if abs(x) < 5 + r or rim(x, z) > 0 or max(abs(x), abs(z)) > HALF - 10:
            return False
        if math.hypot(x - 46, z - 4) < 22:
            return False
        if math.hypot(x - cx, z - cz) < 6 or math.hypot(x - ox, z - oz) < 4:
            return False
        return True
    n = 0
    while n < 34:
        x, z = random.uniform(-86, 86), random.uniform(-82, 86)
        if not clear(x, z, 3):
            continue
        a.tree(x, height(x, z), z, random.uniform(1.0, 1.5), random.choice(['', '', 'bean1', 'bean5', 'heart']))
        n += 1
    n = 0
    while n < 14:
        x, z = random.uniform(-86, 86), random.uniform(-82, 86)
        if not clear(x, z, 2):
            continue
        s = random.uniform(1.2, 2.6)
        a.entity('Rock', t3((x, height(x, z) + s * 0.25, z), (0, random.uniform(0, 360), 0), (s, s * 0.7, s)),
                 mesh('sphere', '#ffffffff', 'art/stone.png'), collider('sphere', radius=0.5))
        n += 1
    n = 0
    while n < 50:
        x, z = random.uniform(-80, 80), random.uniform(-80, 86)
        if rim(x, z) > 0 or math.hypot(x - 46, z - 4) < 12 or abs(x) < 2.5:
            continue
        a.grass(x, height(x, z), z, 0.35)
        n += 1
    # ---- Stalebies, waiting under the field for night ----
    for x, z in [(-14, 30), (16, 20), (-20, -10), (12, -30), (-10, -55), (24, -60), (-40, 50), (50, 40)]:
        a.enemy('stalebie', x, height(x, z), z, hp=4, damage=4, model='stalebie')
    if risen:              # seven years of rot: more of the field is crawling
        for x, z in [(30, 70), (-60, 20), (60, -20), (-30, -70)]:
            a.enemy('stalebie', x, height(x, z), z, hp=4, damage=4, model='stalebie')
        for x, z in [(-30, 30), (40, -50), (-50, -30), (20, 60)]:
            a.enemy('fuzzball', x, height(x, z) + 0.1, z, hp=3, damage=2)
    a.save()


def build_risen():
    build('risen')
