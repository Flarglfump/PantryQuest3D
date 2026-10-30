"""The Salt Idol: the eighth dungeon, inside the witches' statue - played as both child and adult.

North is -z:
  A  the way in
  B  the great hall: west to C, east (a block of rock salt only the Silver Platter moves)
     to D, north the boss door
  C  west: Caramel, in the Fresh era; a hole only a child fits through, to C2 and the
     Silver Platter
  D  east (the Risen era): the witches' guards; the Boss Key; the compass
  F  the twin witches, Saccharine and Sodium
"""
import math

from areakit import Area, ring_floor, ring_wall, ceiling_disc, tunnel, box_wall
from kit import t3, mesh, collider, tags, script, particles, q

H = 8.0


def room(a, cx, cz, r, holes, ceil=H):
    for k in range(3):
        ang = 120 * k + 60
        ring_wall(a.geo('stone', cx + math.cos(math.radians(ang)) * r * 0.6, cz + math.sin(math.radians(ang)) * r * 0.6), cx, cz, r, -1, ceil,
                  24, [(h[0], h[1], 0, 3.0) for h in holes])
    ceiling_disc(a.geo('stone', cx, cz), cx, cz, r, ceil, 0, 18)
    ring_floor(a.geo('sand', cx, cz), cx, cz, 0, r, 0, segs=20, thick=0.5)


def hall(a, x0, z0, x1, z1, h=2.8):
    tunnel(a.geo('sand', (x0 + x1) / 2, (z0 + z1) / 2), a.geo('stone', (x0 + x1) / 2, (z0 + z1) / 2), x0, z0, x1, z1, 0, h=h)


def build():
    a = Area('idoltemple', 'Salt Idol', music='music/castle.wav', dungeon='idoltemple', kill_y=-20, sky='#201408ff', fog=(12, 34),
             fog_color='#302010ff', ambient=('#e0c090ff', 0.6), sun=('#fff0c0ff', 0.4), sun_rot=(-80, 0, 0), shadows=False, chunk=16)
    # ---- A ----
    hall(a, 0, 10, 0, -11.6, h=3.2)
    a.loadzone(0, 0, 9.6, 2.6, 3, 0.8, to='idol', at='temple')
    a.spawn_point('start', 0, 0.1, 7, 0)
    a.point_light(0, 2.5, 2, '#ffd090ff', 1.1, 10)
    # ---- B ----
    bz = -22.0
    room(a, 0, bz, 10, [(90, 1.4), (180, 1.4), (0, 1.4), (270, 1.4)])
    a.chest(-6, 0, bz - 5, 45 + 180, 'map_idoltemple', 'si_map')
    a.point_light(0, 5, bz, '#ffd090ff', 1.4, 14)
    # ---- C: the child's way (west) ----
    cx = -24.0
    hall(a, -9.6, bz, cx + 6.6, bz)
    room(a, cx, bz, 7, [(0, 1.4), (270, 1.0)])
    a.npc('caramel', cx - 2, 0, bz + 2, 60, reach=2.6, until='caramel_taken')
    a.entity('Crawl Hole', t3((cx, 0.6, bz - 6.9), (0, 0, 0), (1.6, 1.2, 0.2)), mesh('cube', '#100804ff', lit=False))
    tunnel(a.geo('sand', cx, bz - 10), a.geo('stone', cx, bz - 10), cx, bz - 6.6, cx, bz - 13.4, 0, w=1.6, h=1.3)
    a.entity('Too Small', t3((cx, 0.65, bz - 7.6), (0, 0, 0), (1.6, 1.3, 0.4)), collider('box'), script('scripts/crawlhole.bs'))
    a.sign(cx + 1.6, 0, bz - 5.2, 0, 'crawl_hint')
    room(a, cx, bz - 18, 4.5, [(90, 1.0)], ceil=4)
    a.chest(cx, 0, bz - 20.5, 180, 'platter', 'si_platter', big=True, then='platter_after')
    a.point_light(cx, 4, bz, '#ffd090ff', 1.1, 11)
    # ---- D: the guards (east, past the rock salt) ----
    dx0 = 24.0
    hall(a, 9.6, bz, dx0 - 6.6, bz)
    a.entity('Rock Salt', t3((13, 1.3, bz), (0, 0, 0), (1.8, 2.6, 2.4)), mesh('cube', '#f0f0f8ff', 'art/ice.png', uv=(2, 2)),
             collider('box'), tags('interact', 'focusable'), script('scripts/heavy.bs', id='si_salt'))
    room(a, dx0, bz, 7.5, [(180, 1.4)])
    for x, z in [(dx0 - 2, bz - 3), (dx0 - 2, bz + 3), (dx0 + 2, bz)]:
        a.enemy('stalebie', x, 0, z, hp=6, damage=4, always=True, group='si_d')
    a.chest(dx0 + 5, 0, bz - 2, 90, 'bosskey_idoltemple', 'si_bosskey', appear='clear:si_d', big=True)
    a.chest(dx0 + 5, 0, bz + 2.5, 90, 'compass_idoltemple', 'si_compass')
    a.point_light(dx0, 4, bz, '#ffd090ff', 1.1, 12)
    # ---- F: the twin witches (north) ----
    fz = -50.0
    hall(a, 0, bz - 9.6, 0, fz + 12.6)
    a.entity('Boss Door', t3((0, 1.5, bz - 11.5), (0, 0, 0), (2.6, 3.0, 0.4)), mesh('cube', '#8a6a3aff', 'art/planks.png'),
             collider('box'), tags('interact'), script('scripts/lockdoor.bs', id='si_boss_door', boss=True))
    room(a, 0, fz, 13, [(90, 1.4)], ceil=12)
    for kind, x in [('sugar', -4), ('salt', 4)]:
        a.entity('Witch', t3((0, 3.5, fz)), mesh('model', '#ff80b0ff' if kind == 'sugar' else '#c0e0ffff', file='models/witch.glb', shadow=True),
                 ('Animator', [('clip', q('idle')), ('speed', 1), ('loop', True), ('playing', True), ('blend', 0.2)]),
                 collider('capsule', (1, 1.2, 1), 0.4, offset=(0, 0.6, 0), trigger=True), tags('enemy', 'focusable', 'boss'),
                 script('scripts/witch.bs', kind=kind))
    a.entity('Heart Pie', t3((0, 0.8, fz + 6), (0, 0, 0), 2.0), mesh('model', '#ff3048ff', file='models/heart.obj', lit=False),
             script('scripts/pickup.bs', kind='heartpie', id='si_pie', when='si_boss'))
    a.entity('Blue Light', t3((0, 1.5, fz), (0, 0, 0), (1.6, 3.0, 1.6)), mesh('cylinder', '#80c0ff60', lit=False, cull=False, cast=False),
             particles(rate=20, max=40, lifetime=1.5, speed=1.2, spread=10, area=(1.6, 1.6), size_start=0.15, size_end=0,
                       color_start='#c0e0ffff', color_end='#4080ff00', blend='add'),
             script('scripts/warp.bs', to='chamber', at='start', sets='idol_done', when='si_boss'))
    a.point_light(0, 7, fz, '#ffd090ff', 1.5, 20)
    a.spawn_point('t_b', 0, 0.1, bz + 8, 0)
    a.spawn_point('t_boss', 0, 0.1, fz + 11, 0)
    a.save()
