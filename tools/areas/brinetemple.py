"""The Fizzwater Temple: the sixth dungeon, under Lake Brine (the Risen era).

The whole temple is flooded; a royal crest in the middle of the great hall drains it (or
fills it again) to Saffron's Lullaby. North is -z:
  A  the way in, from the lake bed
  B  the great hall: the crest; a high ledge east (float up to it while the water's high)
     with the small key
  C  west, behind a water gate that opens when the water's low: Shadow Sprig, and the Long
     Licorice
  D  east, behind the locked door: a chasm only the Long Licorice crosses; the Boss Key
  F  north, through the boss door: the Living Brine's pool
"""
import math

from areakit import Area, ring_floor, ring_wall, ceiling_disc, tunnel, box_wall
from kit import t3, mesh, collider, tags, script, particles, q

H = 9.0


def polar(r, a):
    return math.cos(math.radians(a)) * r, math.sin(math.radians(a)) * r


def room(a, cx, cz, r, holes, ceil=H, floor=True):
    for k in range(3):
        ang = 120 * k + 60
        ring_wall(a.geo('fizzrock', cx + math.cos(math.radians(ang)) * r * 0.6, cz + math.sin(math.radians(ang)) * r * 0.6), cx, cz, r, -4, ceil,
                  24, [(h[0], h[1], 0, 3.0) for h in holes])
    ceiling_disc(a.geo('fizzrock', cx, cz), cx, cz, r, ceil, 0, 18)
    if floor:
        ring_floor(a.geo('stone', cx, cz), cx, cz, 0, r, 0, segs=20, thick=0.5)


def hall(a, x0, z0, x1, z1):
    tunnel(a.geo('stone', (x0 + x1) / 2, (z0 + z1) / 2), a.geo('fizzrock', (x0 + x1) / 2, (z0 + z1) / 2), x0, z0, x1, z1, 0, h=3.2)


def build():
    a = Area('brinetemple', 'Fizzwater Temple', music='music/gulp.wav', dungeon='brinetemple', kill_y=-20, sky='#081828ff',
             fog=(12, 36), fog_color='#103048ff', ambient=('#90c0e0ff', 0.65), sun=('#c0e8ffff', 0.35), sun_rot=(-80, 0, 0),
             shadows=False, chunk=16)
    # the temple's water (tide.bs)
    a.entity('Temple Water', t3((-10.5, 0, -10)), collider('box', (51, 14, 46), trigger=True), tags('water'), script('scripts/tide.bs'))
    a.entity('Tide Surface', t3((-10.5, 5.2, -10), (0, 0, 0), (51, 0.02, 46)), mesh('cube', '#80c0f0a0', 'art/water.png', uv=(20, 10), cast=False, lit=False))
    # ---- A: the way in ----
    for x0, z0, x1, z1 in [(-3, 12, -3, -10), (3, 12, 3, -10)]:
        box_wall(a, 'fizzrock', x0, z0, x1, z1, -4, H, thick=0.8, uvs=0.3)
    a.geo('fizzrock', 0, 0).box((-3, H, -10), (3, H + 0.4, 12), uvs=0.3, sides=('ny',))
    a.geo('stone', 0, 1).box((-3, -0.5, -10), (3, 0, 12), uvs=0.35)
    a.loadzone(0, 0, 11.6, 6, 6, 0.8, to='lake', at='brinetemple')
    a.spawn_point('start', 0, 0.1, 9, 0)
    a.sign(2.2, 0, 6, 0, 'bt_plate')
    hall(a, 0, -10, 0, -11.6)
    a.point_light(0, 4, 0, '#a0d8ffff', 1.2, 14)

    # ---- B: the great hall ----
    bz = -22.0
    room(a, 0, bz, 10, [(90, 1.6), (180, 1.6), (0, 1.6), (270, 1.6)])
    a.geo('stone', 0, bz).cylinder((0, -0.45, bz), 1.6, 0.47, 16, uvs=0.5)
    a.entity('Royal Crest', t3((0, 0.03, bz), (0, 0, 0), (2.4, 0.02, 2.4)), mesh('cylinder', '#e0c050ff', lit=False), tags('interact', 'focusable'),
             script('scripts/crest.bs'))
    # the high ledge (east), with the small key
    a.geo('stone', 6, bz - 6).box((4.2, -0.5, bz - 8.6), (8.6, 5.0, bz - 4.2), uvs=0.35)
    a.chest(6.4, 5.0, bz - 6.4, 135, 'key', 'bt_key')
    a.chest(-7, 0, bz + 4, -120, 'map_brinetemple', 'bt_map')
    for x, z in [(-4, bz - 5), (4, bz + 5)]:
        a.enemy('jelly', x, 0.1, z, hp=2, damage=2)
    a.point_light(0, 6, bz, '#a0d8ffff', 1.4, 16)

    # ---- C: the water gate and Shadow Sprig (west) ----
    cx = -24.0
    hall(a, -9.6, bz, cx + 7.6, bz)
    a.switchdoor(-11.0, 0, bz, (0.5, 3.2, 3.2), 'bt_low', material='stone', color='#6080a0ff')
    room(a, cx, bz, 8, [(0, 1.6)])
    a.entity('Shadow Sprig', t3((cx - 3, 0.1, bz), (0, -90, 0), 1.3), mesh('model', '#303848ff', file='models/sprig.glb', shadow=True),
             ('Animator', [('clip', q('idle')), ('speed', 1), ('loop', True), ('playing', True), ('blend', 0.1)]),
             collider('capsule', (1, 1.1, 1), 0.3, offset=(0, 0.55, 0)), ('RigidBody3D', [('type', 'kinematic')]),
             tags('enemy', 'focusable'), script('scripts/shadow.bs'))
    a.chest(cx - 5.2, 0, bz, -90, 'longlash', 'bt_longlash', appear='clear:bt_shadow', big=True)
    a.point_light(cx, 4, bz, '#a0d8ffff', 1.2, 12)

    # ---- D: the chasm (east, locked) ----
    hall(a, 9.6, bz, 16, bz)
    a.entity('Locked Door', t3((12.5, 1.5, bz), (0, 90, 0), (2.6, 3.0, 0.3)), mesh('cube', '#ffffffff', 'art/planks.png'),
             collider('box'), tags('interact'), script('scripts/lockdoor.bs', id='bt_east'))
    for z0 in (bz - 5, bz + 5):
        box_wall(a, 'fizzrock', 16, z0, 44, z0, -8, 7, thick=0.8, uvs=0.3)
    box_wall(a, 'fizzrock', 44, bz - 5, 44, bz + 5, -8, 7, thick=0.8, uvs=0.3)
    a.geo('fizzrock', 30, bz).box((16, 7, bz - 5), (44, 7.4, bz + 5), uvs=0.3, sides=('ny',))
    a.geo('stone', 18, bz).box((16, -0.5, bz - 5), (20, 0, bz + 5), uvs=0.35)
    a.geo('stone', 39, bz).box((34, -0.5, bz - 5), (44, 0, bz + 5), uvs=0.35)
    a.geo('stone', 27, bz).box((20, -8.5, bz - 5), (34, -8, bz + 5), uvs=0.35)
    a.entity('Chasm', t3((27, -7.5, bz)), collider('box', (14, 0.6, 10), trigger=True), tags('pit'))
    a.target(40.0, 1.9, bz, 90)
    a.geo('fizzrock', 40.4, bz).box((40.2, 0, bz - 0.5), (41.0, 3.2, bz + 0.5), uvs=0.4)
    a.chest(42, 0, bz + 3, 90, 'bosskey_brinetemple', 'bt_bosskey', big=True)
    a.chest(42, 0, bz - 3, 90, 'compass_brinetemple', 'bt_compass')

    # ---- F: the Living Brine (north) ----
    fz = -52.0
    hall(a, 0, bz - 9.6, 0, fz + 11.6)
    a.entity('Boss Door', t3((0, 1.5, bz - 12), (0, 0, 0), (2.6, 3.0, 0.4)), mesh('cube', '#2a4a6aff', 'art/planks.png'),
             collider('box'), tags('interact'), script('scripts/lockdoor.bs', id='bt_boss_door', boss=True))
    room(a, 0, fz, 12, [(90, 1.6)], floor=False)
    ring_floor(a.geo('stone', 0, fz), 0, fz, 8, 12, 0, segs=24, thick=0.5)
    a.geo('fizzrock', 0, fz).cylinder((0, -4.5, fz), 8.2, 0.5, 20, top=True, uvs=0.3)
    a.geo('fizzrock', 0, fz).cylinder((0, -4.0, fz), 8.0, 4.0, 20, top=False, inside=True, uvs=0.3)
    a.water(-8, fz - 8, 8, fz + 8, -0.2, depth=4.4, round_=True)
    a.entity('Brine Column', t3((0, -2, fz), (0, 0, 0), (1.6, 0.2, 1.6)), mesh('cylinder', '#60b0ffa0', lit=False, cast=False, cull=False))
    a.entity('Living Brine', t3((0, -2.2, fz), (0, 0, 0), 0.6), mesh('sphere', '#ff3040ff', lit=False), collider('sphere', radius=0.6),
             tags('enemy', 'focusable', 'boss'), script('scripts/brine.bs'))
    a.entity('Heart Pie', t3((0, 0.8, fz + 10), (0, 0, 0), 2.0), mesh('model', '#ff3048ff', file='models/heart.obj', lit=False),
             script('scripts/pickup.bs', kind='heartpie', id='bt_pie', when='bt_boss'))
    a.entity('Blue Light', t3((0, 1.5, fz + 9.6), (0, 0, 0), (1.6, 3.0, 1.6)), mesh('cylinder', '#80c0ff60', lit=False, cull=False, cast=False),
             particles(rate=20, max=40, lifetime=1.5, speed=1.2, spread=10, area=(1.6, 1.6), size_start=0.15, size_end=0,
                       color_start='#c0e0ffff', color_end='#4080ff00', blend='add'),
             script('scripts/warp.bs', to='chamber', at='start', sets='brinetemple_done', when='bt_boss'))
    a.point_light(0, 6, fz, '#a0d8ffff', 1.5, 18)
    a.spawn_point('t_b', 0, 0.1, bz + 8, 0)
    a.spawn_point('t_d', 17.5, 0.1, bz, -90)
    a.spawn_point('t_boss', 0, 0.1, fz + 10, 0)
    a.save()
