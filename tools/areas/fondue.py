"""The Mount Fondue trail: a switchback road up the cheese volcano.

The trail climbs from Peppermill's gate (south) in three legs: the first to a bend with the
door of Hardtack City cut into the mountain, the second past molten-cheese pools and
rolling boulders to the mouth of Hardtack Caverns (blocked by a boulder; bomb flowers grow
near it), the third up to the crater (not yet open).
"""
import math
import random

from areakit import Area, box_wall
from kit import t3, mesh, collider, tags, script, particles, q


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


# the trail: a polyline of (x, z, height)
TRAIL = [(0, 44, 0), (0, 20, 4), (-18, 6, 7), (-18, -10, 10), (6, -18, 14), (22, -30, 17), (22, -44, 20)]


def trail_at(x, z):
    """(distance from the trail, the trail's height there)."""
    best, hy = 1e9, 0
    for (x0, z0, y0), (x1, z1, y1) in zip(TRAIL, TRAIL[1:]):
        dx, dz = x1 - x0, z1 - z0
        L2 = dx * dx + dz * dz
        t = max(0.0, min(1.0, ((x - x0) * dx + (z - z0) * dz) / L2))
        px, pz = x0 + dx * t, z0 + dz * t
        d = math.hypot(x - px, z - pz)
        if d < best:
            best, hy = d, y0 + (y1 - y0) * t
    return best, hy


PADS = [(-21.5, 6, 4.5, 7), (25.0, -30, 4.5, 17)]     # flat ground before the city door and the caverns


def height(x, z):
    d, hy = trail_at(x, z)
    for px, pz, pr, py in PADS:
        if math.hypot(x - px, z - pz) < pr:
            d, hy = 0, py
    mountain = 12 + (-z) * 0.35 + 2 * math.sin(x * 0.2) * math.cos(z * 0.17)
    flat = smooth((d - 3.5) / 5)
    return hy * (1 - flat) + max(hy, mountain) * flat if d > 3.5 else hy


def build():
    random.seed(23)
    a = Area('fondue', 'Mount Fondue', music='music/fondue.wav', kill_y=-25, sky='#e8b080ff', fog=(26, 54),
             fog_color='#d8a070ff', ambient=('#a88870ff', 0.55), sun=('#ffd8a0ff', 0.9), chunk=22)
    a.entity('Sky', t3((0, 0, 0)), script('scripts/sky.bs', runs=False))
    for cz in range(-52, 52, 13):
        for cx in range(-36, 40, 13):
            a.geo('rock', cx + 6.5, cz + 6.5).ground(cx, cz, cx + 13, cz + 13, 4, 4, height, uvs=0.22)
    # molten cheese pools beside the second leg (they hurt)
    for (x, z, r) in [(-8, -20, 3.5), (12, -10, 3.0)]:
        y = height(x, z) - 0.6
        a.geo('lava', x, z).cylinder((x, y, z), r, 0.01, 12, top=True, uvs=0.4)
        a.entity('Cheese Pool', t3((x, y + 0.4, z)), collider('box', (r * 1.5, 1.0, r * 1.5), trigger=True), tags('lava'))
        a.entity('Steam', t3((x, y + 0.3, z)), particles(rate=8, max=30, lifetime=1.6, speed=0.8, spread=25, area=(r, r), gravity=-0.4,
                                                       size_start=0.4, size_end=1.0, color_start='#ffd890a0', color_end='#ffffff00'))
    # the way down to Peppermill
    a.loadzone(0, 0, 45, 6, 4, 1.2, to='peppermill', at='fondue')
    a.spawn_point('start', 0, 0.1, 40, 0)
    a.sign(3, height(3, 36), 36, 0, 'sign_fondue')
    # ---- Hardtack City's door, at the first bend ----
    cx, cz = -18, 6
    cy = height(cx, cz)
    a.geo('stone', cx - 5, cz).box((cx - 9, cy - 1, cz - 4), (cx - 5.2, cy + 6, cz + 4), uvs=0.3)
    a.entity('City Door', t3((cx - 5.1, cy + 1.5, cz), (0, 90, 0), (2.6, 3.0, 0.1)), mesh('cube', '#20140aff', lit=False))
    a.loadzone(cx - 4.9, cy, cz, 0.8, 3, 2.6, to='hardtack', at='start')
    a.spawn_point('city', cx - 2.5, cy + 0.1, cz, -90)
    a.npc('hardtack', cx + 1.5, cy, cz + 3.2, 150)
    # ---- the caverns' mouth, at the second bend ----
    vx, vz = 22, -30
    vy = height(vx, vz)
    a.geo('stone', vx + 5, vz).box((vx + 5.2, vy - 1, vz - 4.5), (vx + 9, vy + 7, vz + 4.5), uvs=0.3)
    a.entity('Cave Mouth', t3((vx + 5.1, vy + 1.6, vz), (0, -90, 0), (3.0, 3.2, 0.1)), mesh('cube', '#100804ff', lit=False))
    a.cracked(vx + 3.6, vy, vz, 3.2, 3.2, 3.0, 'caves_boulder', boulder=True)
    a.loadzone(vx + 4.9, vy, vz, 0.8, 3, 2.8, to='hardcaves', at='start')
    a.spawn_point('caves', vx + 1.5, vy + 0.1, vz - 2, -90)
    a.sign(vx - 2.5, vy, vz + 3.5, 90, 'sign_caves')
    for dz in (-3.5, 3.0):
        a.bombflower(vx - 1.0, height(vx - 1, vz + dz), vz + dz)
    a.npc('biscotti', vx - 1, vy, vz - 4.5, -60, needs='hardcaves_done', reach=3.0)
    # rolling boulders down the third leg
    for k, (t0, sp) in enumerate([(0.0, 5.0), (0.5, 6.0)]):
        A = (22 + (k - 0.5) * 2.4, height(22, -46) + 0.9, -46)
        B = (22 + (k - 0.5) * 2.4, height(22, -38.5) + 0.9, -38.5)
        a.entity('Boulder', t3(A), mesh('sphere', '#c89870ff', 'art/stone.png'), collider('sphere', radius=0.5),
                 ('RigidBody3D', [('type', 'kinematic')]), script('scripts/roller.bs', a=A, b=B, speed=sp, size=1.6, damage=4))
    a.loadzone(22, height(22, -47), -48, 6, 4, 1.2, to='', say='tbc_summit')
    # Hardtack rollers on the second leg
    for x, z in [(-12, -14), (6, -14)]:
        a.enemy('roller', x, height(x, z), z, hp=2, damage=4)
    # rocks and grass on the trail's edges
    for (x0, z0, y0), (x1, z1, y1) in zip(TRAIL, TRAIL[1:]):
        for i in range(3):
            t = (i + 0.5) / 3
            x, z = x0 + (x1 - x0) * t, z0 + (z1 - z0) * t
            dx, dz = x1 - x0, z1 - z0
            L = math.hypot(dx, dz)
            side = 1 if i % 2 else -1
            px, pz = x - dz / L * 3.2 * side, z + dx / L * 3.2 * side
            s = random.uniform(0.8, 1.6)
            a.entity('Rock', t3((px, height(px, pz) + s * 0.25, pz), (0, random.uniform(0, 360), 0), (s, s * 0.7, s)),
                     mesh('sphere', '#d0a880ff', 'art/stone.png'), collider('sphere', radius=0.5))
    a.save()
