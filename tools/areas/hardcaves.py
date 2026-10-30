"""Hardtack Caverns: the second dungeon, the Hardtack Clan's food caves inside Mount Fondue.

Round caves joined by tunnels (north is -z):
  A  the entrance hall: rolling Hardtack, bomb flowers, a cracked wall north
  B  the cheese hall: a pool of molten cheese crossed by stepping stones and a crust raft;
     the map on the far side; west to C, east (past a boulder) to D, north (locked) to E
  C  the crustlings' den: beat them and the Popcorn Bombs appear
  D  the store room: the compass and the small key
  E  the north cave: the boss key behind a cracked wall; the boss door
  F  King Crustodon's lair
"""
import math

from areakit import Area, ring_floor, ring_wall, ceiling_disc, tunnel
from kit import t3, mesh, collider, tags, script, particles, light, q

H = 7.0


def polar(r, a):
    return math.cos(math.radians(a)) * r, math.sin(math.radians(a)) * r


def room(a, cx, cz, r, holes, floor='rock', ceil=H, y=0.0):
    for k in range(3):
        ang = 120 * k + 60
        ring_wall(a.geo('rock', cx + math.cos(math.radians(ang)) * r * 0.6, cz + math.sin(math.radians(ang)) * r * 0.6), cx, cz, r, y - 0.5, y + ceil,
                  24, [(h[0], h[1], y, y + 3.0) for h in holes])
    ceiling_disc(a.geo('rock', cx, cz), cx, cz, r, y + ceil, 0, 18)
    if floor:
        ring_floor(a.geo(floor, cx, cz), cx, cz, 0, r, y, segs=20, thick=0.5)


def lamp(a, x, y, z):
    a.entity('Lamp', t3((x, y + 0.3, z), (0, 0, 0), (0.5, 0.6, 0.5)), mesh('cylinder', '#ffffffff', 'art/stone.png'), collider('box'))
    a.entity('Flame', t3((x, y + 0.8, z)), particles(rate=24, max=30, lifetime=0.5, speed=0.8, spread=25, area=(0.3, 0.3), gravity=-1.5,
                                                   size_start=0.25, size_end=0.02, color_start='#ffe080ff', color_end='#ff300000', blend='add'))


def build():
    a = Area('hardcaves', 'Hardtack Caverns', music='music/caverns.wav', dungeon='hardcaves', kill_y=-20, sky='#1c0c04ff',
             fog=(12, 34), fog_color='#2a1206ff', ambient=('#c08060ff', 0.55), sun=('#ffa060ff', 0.35), sun_rot=(-80, 0, 0),
             shadows=False, chunk=16)
    # ---- A: the entrance hall ----
    room(a, 0, 0, 9, [(90, 1.4), (270, 1.4)])
    tunnel(a.geo('rock', 0, 11), a.geo('rock', 0, 11), 0, 8.6, 0, 13, 0)
    a.loadzone(0, 0, 12.6, 2.6, 3, 0.8, to='fondue', at='caves')
    a.spawn_point('start', 0, 0.1, 6.5, 0)
    a.sign(1.8, 0, 9.6, 0, 'hc_enter')
    for ang in (200, 340):
        x, z = polar(7, ang)
        a.bombflower(x, 0, z)
    a.enemy('roller', -4, 0.1, 2, hp=2, damage=4)
    a.enemy('roller', 4, 0.1, -2, hp=2, damage=4)
    tunnel(a.geo('rock', 0, -11), a.geo('rock', 0, -11), 0, -8.6, 0, -13.5, 0)
    a.cracked(0, 0, -9.6, 2.8, 3.0, 0.8, 'hc_wall1')
    a.point_light(0, 4, 0, '#ffa050ff', 1.3, 14)

    # ---- B: the cheese hall ----
    bz = -24.0
    room(a, 0, bz, 11, [(90, 1.4), (180, 1.4), (0, 1.4), (270, 1.4)], floor=None)
    ring_floor(a.geo('rock', 0, bz), 0, bz, 7.5, 11, 0, 0, 180, segs=14, thick=3.0)   # the south half of the floor round the pool
    ring_floor(a.geo('rock', 0, bz), 0, bz, 7.5, 11, 0, 242, 298, segs=5, thick=3.0)  # and a ledge on the north side
    a.geo('lava', 0, bz).cylinder((0, -1.6, bz), 7.6, 0.01, 18, top=True)
    a.entity('Cheese', t3((0, -1.2, bz)), collider('box', (15, 1.2, 15), trigger=True), tags('lava'))
    a.entity('Pool Floor', t3((0, -2.2, bz)), collider('box', (16, 0.4, 16)))
    for x, z in [(-2.5, bz + 4.5), (0.5, bz + 1.5), (3, bz - 1.5)]:              # stepping stones (south -> centre)
        a.geo('rock', x, z).cylinder((x, -2, z), 1.0, 2.0, 8)
    a.entity('Crust Raft', t3((3, -0.25, bz - 3), (0, 0, 0), (2.0, 0.5, 2.0)), mesh('cube', '#ffffffff', 'art/crust.png'), collider('box'),
             ('RigidBody3D', [('type', 'kinematic')]), tags('platform'),
             script('scripts/platform.bs', a=(3, -0.25, bz - 3), b=(0, -0.25, bz - 6.8), speed=1.4, wait=1.5))
    x, z = polar(9.4, 250)
    a.chest(x, 0, bz + z, -160, 'map_hardcaves', 'hc_map')
    for ang in (120, 60):
        x, z = polar(9.2, ang)
        lamp(a, x, 0, bz + z)
    a.point_light(0, 5, bz, '#ffb050ff', 1.4, 16)
    # north (locked) to E
    tunnel(a.geo('rock', 0, bz - 13), a.geo('rock', 0, bz - 13), 0, bz - 10.6, 0, bz - 15.5, 0)
    a.entity('Locked Door', t3((0, 1.4, bz - 12.2), (0, 0, 0), (2.4, 2.8, 0.3)), mesh('cube', '#ffffffff', 'art/planks.png'),
             collider('box'), tags('interact'), script('scripts/lockdoor.bs', id='hc_north'))
    a.entity('Lock', t3((0, 1.3, bz - 12.0), (0, 0, 0), (0.5, 0.6, 0.2)), mesh('cube', '#c8a040ff'))

    # ---- C: the crustlings' den (west) ----
    cx = -24.0
    tunnel(a.geo('rock', -13, bz), a.geo('rock', -13, bz), -10.6, bz, cx + 7.6, bz, 0)
    room(a, cx, bz, 8, [(0, 1.4)])
    for dx, dz in [(-2, -3), (-3, 2.5), (2, 2)]:
        a.enemy('crustling', cx + dx, 0.1, bz + dz, hp=3, damage=4, group='hc_crust')
    a.chest(cx - 4.8, 0, bz, -90, 'bombs', 'hc_bombs', appear='clear:hc_crust', big=True)
    lamp(a, cx - 5.5, 0, bz - 3.5)
    a.point_light(cx, 4, bz, '#ffa050ff', 1.2, 11)

    # ---- D: the store room (east, past the boulder) ----
    dx0 = 24.0
    tunnel(a.geo('rock', 13, bz), a.geo('rock', 13, bz), 10.6, bz, dx0 - 7.6, bz, 0)
    a.cracked(14.5, 0, bz, 2.4, 2.4, 2.2, 'hc_boulder', boulder=True)
    room(a, dx0, bz, 8, [(180, 1.4)])
    a.chest(dx0 + 4.8, 0, bz - 2, 90, 'compass_hardcaves', 'hc_compass')
    a.chest(dx0 + 4.8, 0, bz + 2, 90, 'key', 'hc_key')
    a.enemy('roller', dx0, 0.1, bz + 3, hp=2, damage=4)
    for x, z in [(dx0 - 3, bz - 5.5), (dx0 - 1.5, bz - 6.2), (dx0 + 2, bz + 5.8)]:
        a.pot(x, 0, z)
    a.point_light(dx0, 4, bz, '#ffa050ff', 1.2, 11)

    # ---- E: the north cave ----
    ez = -48.0
    room(a, 0, ez, 9, [(90, 1.4), (270, 1.4), (180, 1.4)])
    for ang in (30, 150):
        x, z = polar(7, ang)
        a.bombflower(x, 0, ez + z)
    a.enemy('crustling', 3, 0.1, ez, hp=3, damage=4)
    a.enemy('roller', -3, 0.1, ez - 3, hp=2, damage=4)
    # the boss key: behind the cracked wall to the west
    tunnel(a.geo('rock', -11, ez), a.geo('rock', -11, ez), -8.6, ez, -14, ez, 0)
    a.cracked(-9.5, 0, ez, 0.8, 3.0, 2.8, 'hc_wall2')
    room(a, -18, ez, 4.5, [(0, 1.4)])
    a.chest(-20, 0, ez, -90, 'bosskey_hardcaves', 'hc_bosskey', big=True)
    a.point_light(0, 4, ez, '#ffa050ff', 1.2, 12)
    # the boss door
    tunnel(a.geo('rock', 0, ez - 11), a.geo('rock', 0, ez - 11), 0, ez - 8.6, 0, ez - 14, 0)
    a.entity('Boss Door', t3((0, 1.5, ez - 10), (0, 0, 0), (2.6, 3.0, 0.4)), mesh('cube', '#8a3a2aff', 'art/planks.png'),
             collider('box'), tags('interact'), script('scripts/lockdoor.bs', id='hc_boss', boss=True))

    # ---- F: King Crustodon's lair ----
    fz = -74.0
    room(a, 0, fz, 14, [(90, 1.4)], ceil=10)
    for ang in (30, 150, 210, 330):
        x, z = polar(11.5, ang)
        a.bombflower(x, 0, fz + z)
    for ang in (0, 90, 180, 270):
        x, z = polar(12.8, ang + 45)
        lamp(a, x, 0, fz + z)
    a.entity('Crustodon', t3((0, 0, fz - 4), (0, 0, 0)), mesh('model', file='models/crustodon.glb', shadow=True),
             ('Animator', [('clip', q('idle')), ('speed', 1), ('loop', True), ('playing', True), ('blend', 0.2)]),
             collider('capsule', (1, 3.0, 1), 1.6, offset=(0, 1.5, 0)), ('RigidBody3D', [('type', 'kinematic')]),
             tags('enemy', 'focusable', 'boss'), script('scripts/crustodon.bs'))
    a.entity('Heart Pie', t3((0, 0.8, fz + 4), (0, 0, 0), 2.0), mesh('model', '#ff3048ff', file='models/heart.obj', lit=False),
             script('scripts/pickup.bs', kind='heartpie', id='hc_pie', when='hardcaves_boss'))
    a.entity('Blue Light', t3((0, 1.5, fz), (0, 0, 0), (1.6, 3.0, 1.6)), mesh('cylinder', '#80c0ff60', lit=False, cull=False, cast=False),
             particles(rate=20, max=40, lifetime=1.5, speed=1.2, spread=10, area=(1.6, 1.6), size_start=0.15, size_end=0,
                       color_start='#c0e0ffff', color_end='#4080ff00', blend='add'),
             script('scripts/warp.bs', to='fondue', at='caves', sets='hardcaves_done', when='hardcaves_boss'))
    a.point_light(0, 7, fz, '#ffa050ff', 1.5, 20)
    # (for trying parts on their own)
    a.spawn_point('t_b', 0, 0.1, bz + 9, 0)
    a.spawn_point('t_e', 0, 0.1, ez + 6, 0)
    a.spawn_point('t_boss', 0, 0.1, ez - 13, 0)
    a.save()
