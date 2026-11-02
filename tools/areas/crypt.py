"""The Compost Crypt: the seventh dungeon, under Peppermill's graveyard (the Risen era).

Nothing here is what it seems (the Onion Lens). North is -z:
  A  the stair down; a false wall west
  B  the hall of the unseen bridge: a pit crossed by a floor only the lens shows
  C  the guillotine walk: blades drop across the way; the small key at the end
  D  east, behind the locked door: the Stalebies' tomb; the Meringue Boots
  E  north: a gap too wide to jump; walk on air; the Boss Key
  F  the Maw of Rot
"""
import math

from areakit import Area, ring_floor, ring_wall, ceiling_disc, tunnel, box_wall
from kit import t3, mesh, collider, tags, script, particles, q

H = 7.0


def room(a, cx, cz, r, holes, ceil=H, floor=True):
    for k in range(3):
        ang = 120 * k + 60
        ring_wall(a.geo('rock', cx + math.cos(math.radians(ang)) * r * 0.6, cz + math.sin(math.radians(ang)) * r * 0.6), cx, cz, r, -6, ceil,
                  24, [(h[0], h[1], 0, 3.0) for h in holes])
    ceiling_disc(a.geo('rock', cx, cz), cx, cz, r, ceil, 0, 18)
    if floor:
        ring_floor(a.geo('rot', cx, cz), cx, cz, 0, r, 0, segs=20, thick=0.5)


def hall(a, x0, z0, x1, z1):
    tunnel(a.geo('rot', (x0 + x1) / 2, (z0 + z1) / 2), a.geo('rock', (x0 + x1) / 2, (z0 + z1) / 2), x0, z0, x1, z1, 0)


def build():
    a = Area('crypt', 'Compost Crypt', music='music/gulp.wav', dungeon='crypt', kill_y=-20, sky='#0a0608ff', fog=(16, 48),
             fog_color='#140a10ff', ambient=('#a08898ff', 0.55), sun=('#c0a0c0ff', 0.3), sun_rot=(-80, 0, 0), shadows=False, chunk=16)
    # ---- A ----
    room(a, 0, 0, 7, [(90, 1.4), (270, 1.4), (180, 1.4)])
    hall(a, 0, 6.6, 0, 11)
    a.loadzone(0, 0, 10.6, 2.6, 3, 0.8, to='peppermill', at='crypt')
    a.spawn_point('start', 0, 0.1, 4.5, 0)
    a.sign(2.4, 0, 4.2, 0, 'lens_hint')
    # west: a false wall hides the map
    hall(a, -6.6, 0, -11, 0)
    a.entity('False Wall', t3((-7.2, 1.5, 0), (0, 90, 0), (2.6, 3.0, 0.4)), mesh('cube', '#7a6a6aff', 'art/stone.png'), script('scripts/secret.bs', kind='fake'))
    room(a, -14, 0, 3.4, [(0, 1.4)])
    a.chest(-15.6, 0, 0, -90, 'map_crypt', 'cc_map')
    a.point_light(0, 4, 0, '#c0a0c0ff', 1.1, 10)
    # ---- B: the unseen bridge ----
    bz = -20.0
    hall(a, 0, -6.6, 0, bz + 8.6)
    room(a, 0, bz, 9, [(90, 1.4), (270, 1.4), (330, 1.4)], floor=False)
    a.geo('rot', 0, bz + 6).box((-9, -0.5, bz + 4), (9, 0, bz + 9), uvs=0.35)
    a.geo('rot', 0, bz - 6).box((-9, -0.5, bz - 9), (9, 0, bz - 4), uvs=0.35)
    a.geo('rock', 0, bz).box((-9, -6.5, bz - 4), (9, -6, bz + 4), uvs=0.35)
    a.entity('Pit', t3((0, -5.5, bz)), collider('box', (18, 0.6, 8), trigger=True), tags('pit'))
    a.entity('Unseen Bridge', t3((-2.5, -0.26, bz), (0, 0, 0), (1.6, 0.5, 8.2)), mesh('cube', '#d0b0ffa0', 'art/stone.png', cast=False),
             collider('box'), script('scripts/secret.bs', kind='invisible'))
    a.entity('Seen Bridge', t3((3, -0.25, bz + 2.5), (0, 0, 0), (1.6, 0.5, 3.0)), mesh('cube', '#ffffffff', 'art/stone.png'), collider('box'))
    a.point_light(0, 4, bz, '#c0a0c0ff', 1.2, 12)
    # ---- C: the guillotine walk (east of B) ----
    cz = bz - 4.5
    hall(a, 8.4, cz, 26, cz)
    for k, x in enumerate([12, 15.5, 19, 22.5]):
        a.entity('Guillotine', t3((x, 0, cz), (0, 0, 0), (0.25, 2.6, 2.4)), mesh('cube', '#c0c0c8ff', cast=False), script('scripts/blade.bs', offset=k * 0.6))
    room(a, 30, cz, 4.5, [(180, 1.4)])
    a.chest(32, 0, cz, 90, 'key', 'cc_key')
    a.entity('Lock Door', t3((0, 1.4, bz - 9.4), (0, 0, 0), (2.4, 2.8, 0.3)), mesh('cube', '#ffffffff', 'art/planks.png'),
             collider('box'), tags('interact'), script('scripts/lockdoor.bs', id='cc_key'))
    # ---- D: the Stalebies' tomb (north of B, behind the locked door) ----
    dz = -38.0
    hall(a, 0, bz - 9, 0, dz + 8.6)
    room(a, 0, dz, 9, [(90, 1.4), (270, 1.4)])
    for x, z in [(-4, dz + 2), (4, dz + 2), (-3, dz - 3), (3, dz - 3)]:
        a.enemy('stalebie', x, 0, z, hp=4, damage=4, always=True, group='cc_tomb')
    a.chest(0, 0, dz - 5, 180, 'hover', 'cc_hover', appear='clear:cc_tomb', big=True)
    a.chest(-6, 0, dz, -90 + 180, 'compass_crypt', 'cc_compass')
    a.point_light(0, 4, dz, '#c0a0c0ff', 1.2, 12)
    # ---- E: the gap (north) ----
    ez = -58.0
    hall(a, 0, dz - 9, 0, ez + 8)
    room(a, 0, ez, 8, [(90, 1.4), (270, 1.4)], floor=False)
    a.geo('rot', 0, ez + 5.5).box((-8, -0.5, ez + 3), (8, 0, ez + 8), uvs=0.35)
    a.geo('rot', 0, ez - 5.5).box((-8, -0.5, ez - 8), (8, 0, ez - 0.5), uvs=0.35)
    a.geo('rock', 0, ez).box((-8, -6.5, ez - 0.5), (8, -6, ez + 3), uvs=0.35)
    a.entity('Pit', t3((0, -5.5, ez + 1.25)), collider('box', (16, 0.6, 3.5), trigger=True), tags('pit'))
    a.chest(-5, 0, ez - 4, 180, 'bosskey_crypt', 'cc_bosskey', big=True)
    a.point_light(0, 4, ez, '#c0a0c0ff', 1.2, 12)
    hall(a, 0, ez - 8, 0, ez - 13)
    a.entity('Boss Door', t3((0, 1.5, ez - 10.5), (0, 0, 0), (2.6, 3.0, 0.4)), mesh('cube', '#4a2a3aff', 'art/planks.png'),
             collider('box'), tags('interact'), script('scripts/lockdoor.bs', id='cc_boss_door', boss=True))
    # ---- F: the Maw of Rot ----
    fz = -82.0
    room(a, 0, fz, 12, [(90, 1.4)], ceil=10)
    a.entity('Maw of Rot', t3((0, 3.5, fz - 3), (0, 0, 0), (3.0, 3.0, 3.0)), mesh('sphere', '#a04060ff', 'art/rot.png'),
             collider('sphere', radius=0.5, trigger=True), tags('enemy', 'boss', 'shootable'), script('scripts/maw.bs'))
    a.entity('Heart Pie', t3((0, 0.8, fz + 4), (0, 0, 0), 2.0), mesh('model', '#ff3048ff', file='models/heart.obj', lit=False),
             script('scripts/pickup.bs', kind='heartpie', id='cc_pie', when='cc_boss'))
    a.entity('Blue Light', t3((0, 1.5, fz + 6), (0, 0, 0), (1.6, 3.0, 1.6)), mesh('cylinder', '#80c0ff60', lit=False, cull=False, cast=False),
             particles(rate=20, max=40, lifetime=1.5, speed=1.2, spread=10, area=(1.6, 1.6), size_start=0.15, size_end=0,
                       color_start='#c0e0ffff', color_end='#4080ff00', blend='add'),
             script('scripts/warp.bs', to='chamber', at='start', sets='crypt_done', when='cc_boss'))
    a.point_light(0, 6, fz, '#c0a0c0ff', 1.5, 18)
    a.spawn_point('t_b', 0, 0.1, bz + 7, 0)
    a.spawn_point('t_e', 0, 0.1, ez + 7, 0)
    a.spawn_point('t_boss', 0, 0.1, ez - 12.5, 0)
    a.save()
