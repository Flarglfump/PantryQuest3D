"""The ruins of Castle Larder: where the Spire fell, and Gorgemold rises.

An open, broken courtyard under a black sky. Saffron stands at the edge, ready with her light.
"""
import math
import random

from areakit import Area
from kit import drawn, t3, mesh, collider, tags, script, particles, q


def height(x, z):
    r = math.hypot(x, z)
    return 0.3 * math.sin(x * 0.4) * math.cos(z * 0.3) + 8 * max(0.0, min(1.0, (r - 22) / 4))


def build():
    global height
    random.seed(81)
    a = Area('ruins', 'Castle Ruins', music='music/boss.wav', kill_y=-20, sky='#100808ff', fog=(40, 95), fog_color='#201010ff',
             ambient=('#a07070ff', 0.6), sun=('#ffa080ff', 0.4), chunk=20)
    for cz in range(-30, 30, 10):
        for cx in range(-30, 30, 10):
            a.geo('rot', cx + 5, cz + 5).ground(cx, cz, cx + 10, cz + 10, 4, 4, height, uvs=0.3)
    height = drawn(height)        # (from here on, things are set on the ground as drawn: none float or sink)
    for k in range(10):
        ang = k * 36 + random.uniform(-8, 8)
        x, z = math.cos(math.radians(ang)) * 20, math.sin(math.radians(ang)) * 20
        hgt = random.uniform(3, 9)
        a.geo('stone', x, z).box((x - 1, -0.5, z - 1), (x + 1, hgt, z + 1), uvs=0.3)
    a.entity('Embers', t3((0, 2, 0)), particles(rate=10, max=60, lifetime=3, speed=1, spread=90, area=(36, 36), gravity=-0.3,
                                              size_start=0.12, size_end=0, color_start='#ff8040ff', color_end='#ff200000', blend='add'))
    a.spawn_point('start', 0, 0.1, 15, 0)
    a.entity('Gorgemold', t3((0, 0, -4), (0, 0, 0), 3.2), mesh('model', '#506040ff', file='models/mildew.glb', shadow=True),
             ('Animator', [('clip', q('idle')), ('speed', 1), ('loop', True), ('playing', True), ('blend', 0.2)]),
             collider('capsule', (1, 2.0, 1), 0.5, offset=(0, 1.0, 0)), ('RigidBody3D', [('type', 'kinematic')]),
             tags('enemy', 'focusable', 'boss'), script('scripts/gorgemold.bs'))
    a.entity('Saffron', t3((-10, height(-10, 10), 10), (0, -130, 0), 1.3), mesh('model', file='models/saffron.glb'),
             ('Animator', [('clip', q('idle')), ('speed', 1), ('loop', True), ('playing', True), ('blend', 0.2)]))
    a.area_map()          # (the MAP page: the ground from above, the ways out named)
    a.save()
