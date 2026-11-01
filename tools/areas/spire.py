"""The Moldering Spire: Duke Mildew's tower of mould, grown from the ruins of Castle Larder.

Four floors (each its own round room, joined by stairs that are load zones):
  F1  the Keepers' gate: rot-things guard the stair
  F2  a pit of rot: lash across
  F3  a hall of lies: an unseen bridge (the Onion Lens)
  top Duke Mildew; Saffron in her crystal. When he falls the tower comes down: run (escape.bs)
"""
import math

from areakit import Area, ring_floor, ring_wall, ceiling_disc, tunnel, box_wall
from kit import t3, mesh, collider, tags, script, particles, q

H = 8.0


def room(a, cx, cz, r, holes, ceil=H, floor=True):
    for k in range(3):
        ang = 120 * k + 60
        ring_wall(a.geo('mould', cx + math.cos(math.radians(ang)) * r * 0.6, cz + math.sin(math.radians(ang)) * r * 0.6), cx, cz, r, -7, ceil,
                  24, [(h[0], h[1], 0, 3.0) for h in holes])
    ceiling_disc(a.geo('rot', cx, cz), cx, cz, r, ceil, 0, 18)
    if floor:
        ring_floor(a.geo('rot', cx, cz), cx, cz, 0, r, 0, segs=20, thick=0.5)


def stairs(a, x, z, to_spawn, needs=''):
    a.geo('stone', x, z).box((x - 1.4, -0.5, z - 1.4), (x + 1.4, 0.02, z + 1.4), uvs=0.5)
    a.entity('Stair Glow', t3((x, 0.3, z)), particles(rate=10, max=20, lifetime=1.2, speed=1.0, spread=10, area=(2, 2), size_start=0.15, size_end=0,
                                                    color_start='#e0ffa0ff', color_end='#60a02000', blend='add'))
    a.loadzone(x, 0, z, 2.4, 2, 2.4, to='spire', at=to_spawn, needs=needs)


def build():
    a = Area('spire', 'Moldering Spire', music='music/castle.wav', kill_y=-20, sky='#101408ff', fog=(12, 34), fog_color='#182010ff',
             ambient=('#90a080ff', 0.55), sun=('#c0d0a0ff', 0.3), sun_rot=(-80, 0, 0), shadows=False, chunk=16)
    a.entity('Escape', t3((0, 0, 0)), script('scripts/escape.bs'))
    # ---- F1 ----
    room(a, 0, 0, 10, [(90, 1.4)])
    tunnel(a.geo('rot', 0, 12), a.geo('mould', 0, 12), 0, 9.6, 0, 14, 0)
    a.loadzone(0, 0, 13.6, 2.6, 3, 0.8, to='town', at='spire', until='escaping')
    a.loadzone(0, 0, 13.6, 2.6, 3, 0.8, to='ruins', at='start', needs='escaping')
    a.spawn_point('start', 0, 0.1, 7, 0)
    a.spawn_point('bottom', 0, 0.1, 4, 180)
    for x, z in [(-4, -2), (4, -2), (0, -5), (-5, 3)]:
        a.enemy('stalebie', x, 0, z, hp=6, damage=4, always=True, group='sp1')
    a.switchdoor(0, 0, -7.52, (3.2, 3.0, 0.6), 'clear:sp1', stay=True, material='stone', color='#506040ff')
    stairs(a, 0, -8.6, 'f2')
    a.point_light(0, 4, 0, '#c0e0a0ff', 1.2, 14)
    # ---- F2: the pit of rot ----
    z2 = -40.0
    room(a, 0, z2, 10, [], floor=False)
    a.geo('rot', 0, z2 + 6.5).box((-10, -0.5, z2 + 3.5), (10, 0, z2 + 10), uvs=0.35)
    a.geo('rot', 0, z2 - 7).box((-10, -0.5, z2 - 10), (10, 0, z2 - 4.5), uvs=0.35)
    a.geo('rot', 0, z2).box((-10, -7.5, z2 - 4.5), (10, -7, z2 + 3.5), uvs=0.35)
    a.entity('Pit', t3((0, -6.5, z2 - 0.5)), collider('box', (20, 0.6, 8), trigger=True), tags('pit'))
    a.geo('stone', 0, z2 - 6.6).box((-0.5, 0, z2 - 7.0), (0.5, 3.4, z2 - 6.2), uvs=0.4)
    a.target(0, 2.0, z2 - 5.95, 180)
    a.spawn_point('f2', 0, 0.1, z2 + 7.5, 0)
    stairs(a, 5, z2 - 7.5, 'f3')
    a.point_light(0, 4, z2, '#c0e0a0ff', 1.2, 14)
    # ---- F3: the hall of lies ----
    z3 = -80.0
    room(a, 0, z3, 10, [], floor=False)
    a.geo('rot', 0, z3 + 6.5).box((-10, -0.5, z3 + 3.5), (10, 0, z3 + 10), uvs=0.35)
    a.geo('rot', 0, z3 - 7).box((-10, -0.5, z3 - 10), (10, 0, z3 - 4.5), uvs=0.35)
    a.geo('rot', 0, z3).box((-10, -7.5, z3 - 4.5), (10, -7, z3 + 3.5), uvs=0.35)
    a.entity('Pit', t3((0, -6.5, z3 - 0.5)), collider('box', (20, 0.6, 8), trigger=True), tags('pit'))
    a.entity('Unseen Bridge', t3((3, -0.26, z3 - 0.5), (0, 0, 0), (1.6, 0.5, 8.2)), mesh('cube', '#d0b0ffa0', 'art/stone.png', cast=False),
             collider('box'), script('scripts/secret.bs', kind='invisible'))
    a.entity('False Bridge', t3((-3, -0.26, z3 - 0.5), (0, 0, 0), (1.6, 0.5, 8.2)), mesh('cube', '#ffffffff', 'art/stone.png'),
             script('scripts/secret.bs', kind='fake'))
    a.spawn_point('f3', 0, 0.1, z3 + 7.5, 0)
    stairs(a, 0, z3 - 7.5, 'top')
    a.point_light(0, 4, z3, '#c0e0a0ff', 1.2, 14)
    # ---- the top: Duke Mildew ----
    zt = -122.0
    room(a, 0, zt, 13, [], ceil=13)
    a.entity('Duke Mildew', t3((0, 0, zt - 3), (0, 0, 0), 1.2), mesh('model', file='models/mildew.glb', shadow=True),
             ('Animator', [('clip', q('idle')), ('speed', 1), ('loop', True), ('playing', True), ('blend', 0.2)]),
             collider('capsule', (1, 2.0, 1), 0.6, offset=(0, 1.0, 0), trigger=True), tags('enemy', 'boss'), script('scripts/mildew.bs'))
    a.entity('Crystal', t3((0, 1.6, zt - 10), (0, 0, 0), (1.8, 3.2, 1.8)), mesh('cube', '#a0ff80a0', lit=False, cast=False),
             script('scripts/blocker.bs', until='mildew_beaten'))
    a.entity('Saffron', t3((0, 0.2, zt - 10), (0, 0, 0), 1.3), mesh('model', file='models/saffron.glb'),
             ('Animator', [('clip', q('idle')), ('speed', 1), ('loop', True), ('playing', True), ('blend', 0.2)]))
    a.spawn_point('top', 0, 0.1, zt + 9, 0)
    stairs(a, 9, zt + 6, 'bottom', needs='escaping')
    a.point_light(0, 7, zt, '#c0e0a0ff', 1.6, 20)
    a.save()
