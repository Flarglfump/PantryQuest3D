"""The Thyme Temple: the fourth dungeon, an overgrown manor of stone deep in the Thicket.

North is -z. Rooms:
  A  the entry: a broken bridge over a pit; a lash target on the far pillar
  B  the hall of braziers: three cold braziers (the Lantern Sisters stole their flames)
     round the lift in the middle, which goes down to the gallery when all three burn
  C  west: the purple sister; the map
  D  east: Stalebies guard the Skewer Bow; the small key on a high ledge (lash target)
  E  north (locked): the red sister floats out of reach of a blade; the Boss Key; then a
     pit (lash target) east to F
  F  the green sister
  G  the gallery, down the lift: the Hollow Duke
"""
import math

from areakit import Area, ring_floor, ring_wall, ceiling_disc, tunnel, box_wall
from kit import t3, mesh, collider, tags, script, particles, q

H = 7.0


def polar(r, a):
    return math.cos(math.radians(a)) * r, math.sin(math.radians(a)) * r


def room(a, cx, cz, r, holes, ceil=H, floor=True):
    for k in range(3):
        ang = 120 * k + 60
        ring_wall(a.geo('stone', cx + math.cos(math.radians(ang)) * r * 0.6, cz + math.sin(math.radians(ang)) * r * 0.6), cx, cz, r, -3.5, ceil,
                  24, [(h[0], h[1], 0, 3.0) for h in holes])
    ceiling_disc(a.geo('planks', cx, cz), cx, cz, r, ceil, 0, 18)
    if floor:
        ring_floor(a.geo('cobble', cx, cz), cx, cz, 0, r, 0, segs=20, thick=0.5)


def hall(a, x0, z0, x1, z1):
    tunnel(a.geo('cobble', (x0 + x1) / 2, (z0 + z1) / 2), a.geo('stone', (x0 + x1) / 2, (z0 + z1) / 2), x0, z0, x1, z1, 0)


def sister(a, x, y, z, flame, hp=6, arrow_only=False, float_h=0.3, speed=1.6):
    kw = {'flame': flame, 'hp': hp, 'float_h': float_h, 'speed': speed}
    if arrow_only:
        kw['arrow_only'] = True
    a.entity('Lantern Sister', t3((x, y, z)), mesh('model', '#d090ffc0', file='models/sister.glb', cast=False),
             ('Animator', [('clip', q('idle')), ('speed', 1), ('loop', True), ('playing', True), ('blend', 0.2)]),
             collider('capsule', (1, 1.2, 1), 0.4, offset=(0, 0.6, 0), trigger=True), tags('enemy', 'shootable'), script('scripts/sister.bs', **kw))


def build():
    a = Area('thymetemple', 'Thyme Temple', music='music/castle.wav', dungeon='thymetemple', kill_y=-20, sky='#101810ff',
             fog=(12, 34), fog_color='#182418ff', ambient=('#a0c098ff', 0.6), sun=('#d0f0c0ff', 0.35), sun_rot=(-80, 0, 0),
             shadows=False, chunk=16)
    # ---- A: the entry and its broken bridge ----
    for x0, z0, x1, z1 in [(-3, 10, -3, -10), (3, 10, 3, -10)]:
        box_wall(a, 'stone', x0, z0, x1, z1, -6, H, thick=0.8, uvs=0.3)
    a.geo('planks', 0, 0).box((-3, H, -10), (3, H + 0.3, 10), uvs=0.3, sides=('ny',))
    a.geo('cobble', 0, 6).box((-3, -0.5, 1), (3, 0, 10), uvs=0.35)
    a.geo('cobble', 0, -7).box((-3, -0.5, -10), (3, 0, -5), uvs=0.35)
    a.geo('stone', 0, -2).box((-3, -6.5, -5), (3, -6, 1), uvs=0.35)
    a.entity('Pit', t3((0, -5.5, -2)), collider('box', (6, 0.6, 6), trigger=True), tags('pit'))
    a.geo('stone', 0, -7.6).box((-0.6, 0, -8.2), (0.6, 3.4, -7.4), uvs=0.4)
    a.target(0, 2.4, -7.25, 180)
    a.loadzone(0, 0, 9.6, 6, 3, 0.8, to='thicket', at='temple')
    a.spawn_point('start', 0, 0.1, 7.5, 0)
    a.sign(-2.2, 0, 3, 90, 'tt_enter')
    a.point_light(0, 4, 0, '#c0e0a0ff', 1.2, 12)
    hall(a, 0, -10, 0, -14)

    # ---- B: the hall of braziers ----
    bz = -24.0
    room(a, 0, bz, 10, [(90, 1.4), (180, 1.4), (0, 1.4), (270, 1.4)])
    for k, (flame, color) in enumerate([('tt_flame1', '#c070ffff'), ('tt_flame2', '#ff5050ff'), ('tt_flame3', '#50ff70ff')]):
        x, z = polar(6.5, 210 + k * 60)
        a.geo('stone', x, bz + z).cylinder((x, 0, bz + z), 0.6, 1.4, 8, uvs=0.5)
        a.entity('Brazier Flame', t3((x, 1.6, bz + z)), particles(rate=20, max=30, lifetime=0.7, speed=0.8, spread=20, area=(0.5, 0.5), gravity=-1.2,
                                                               size_start=0.45, size_end=0, color_start=color, color_end='#ffffff00', blend='add', emitting=False),
                 script('scripts/brazier.bs', when=flame))
    a.geo('stone', 0, bz).cylinder((0, -0.3, bz), 2.2, 0.4, 16, uvs=0.5)
    a.entity('Lift Glow', t3((0, 0.2, bz)), particles(rate=8, max=20, lifetime=1.2, speed=0.6, spread=10, area=(3, 3), size_start=0.2, size_end=0,
                                                    color_start='#c0ffc0ff', color_end='#40804000', blend='add'))
    a.loadzone(0, 0.1, bz, 2.6, 2, 2.6, to='thymetemple', at='gallery', needs='tt_flames')
    a.sign(2.8, 0, bz + 3.2, 0, 'tt_lift')
    a.point_light(0, 5, bz, '#c0e0a0ff', 1.3, 14)

    # ---- C: the purple sister (west) ----
    cx = -22.0
    hall(a, -9.6, bz, cx + 6.6, bz)
    room(a, cx, bz, 7, [(0, 1.4)])
    sister(a, cx, 0, bz, 'tt_flame1', hp=6)
    a.chest(cx - 4.4, 0, bz - 2, -90, 'map_thymetemple', 'tt_map')
    for p in [(cx - 6, 3.2, bz), (cx, 3.2, bz - 6.5), (cx, 3.2, bz + 6.5)]:
        a.entity('Old Painting', t3(p, (0, 90 if p[0] < cx - 1 else (0 if p[2] < bz else 180), 0), (2.0, 1.4, 0.1)), mesh('cube', '#ffffffff', 'art/painting.png'))
    a.point_light(cx, 4, bz, '#d0b0ffff', 1.1, 11)

    # ---- D: the Stalebies and the Skewer Bow (east) ----
    dx0 = 22.0
    hall(a, 9.6, bz, dx0 - 6.6, bz)
    room(a, dx0, bz, 7, [(180, 1.4)])
    for dx, dz in [(2, -2.5), (2.5, 2.5)]:
        a.enemy('stalebie', dx0 + dx, 0, bz + dz, hp=4, damage=4, group='tt_d', always=True)
    a.chest(dx0 + 4.6, 0, bz, 90, 'bow', 'tt_bow', appear='clear:tt_d', big=True)
    a.chest(dx0 - 1, 0, bz + 5, 180, 'compass_thymetemple', 'tt_compass')
    a.geo('stone', dx0, bz - 5.5).box((dx0 - 2, 0, bz - 7), (dx0 + 2, 3.2, bz - 4.6), uvs=0.4)
    a.chest(dx0, 3.2, bz - 5.6, 180, 'key', 'tt_key')
    a.target(dx0 + 1.6, 4.4, bz - 6.0, 180)
    a.point_light(dx0, 4, bz, '#c0e0a0ff', 1.1, 11)

    # ---- E: the red sister (north, locked) ----
    ez = -48.0
    hall(a, 0, bz - 10, 0, ez + 8.6)
    a.entity('Locked Door', t3((0, 1.4, bz - 11), (0, 0, 0), (2.4, 2.8, 0.3)), mesh('cube', '#ffffffff', 'art/planks.png'),
             collider('box'), tags('interact'), script('scripts/lockdoor.bs', id='tt_north'))
    a.entity('Lock', t3((0, 1.3, bz - 11.2), (0, 0, 0), (0.5, 0.6, 0.2)), mesh('cube', '#c8a040ff'))
    room(a, 0, ez, 9, [(90, 1.4), (0, 1.4)], ceil=8)
    sister(a, 0, 0, ez, 'tt_flame2', hp=6, arrow_only=True, float_h=3.6, speed=1.0)
    a.chest(-5, 0, ez - 4, -45, 'slice', 'tt_slice', appear='tt_flame2')
    a.point_light(0, 5, ez, '#ffb0b0ff', 1.2, 12)
    # east to F, over a pit
    fx = 22.0
    a.geo('cobble', 11, ez).box((8.6, -0.5, ez - 1.6), (11, 0, ez + 1.6), uvs=0.35)
    for z0, z1 in [(ez - 1.6, ez - 1.6), (ez + 1.6, ez + 1.6)]:
        box_wall(a, 'stone', 8.6, z0, fx - 6.6, z1, -6, 3.0, thick=0.5, uvs=0.3)
    a.geo('stone', 11, ez).box((8.6, 3.0, ez - 1.8), (fx - 6.6, 3.4, ez + 1.8), uvs=0.3)
    a.geo('stone', 14, ez).box((11, -6.5, ez - 1.6), (fx - 6.6, -6, ez + 1.6), uvs=0.35)
    a.entity('Pit', t3((14, -5.5, ez)), collider('box', (8, 0.6, 3.2), trigger=True), tags('pit'))
    room(a, fx, ez, 7, [(180, 1.4)])
    a.geo('stone', fx - 4.4, ez + 1.4).box((fx - 4.4, 0, ez + 1.0), (fx - 3.6, 3.4, ez + 1.8), uvs=0.4)
    a.target(fx - 4.55, 1.8, ez + 1.4, 90)

    # ---- F: the green sister ----
    sister(a, fx + 1, 0, ez, 'tt_flame3', hp=8, speed=2.4)
    a.point_light(fx, 4, ez, '#b0ffc0ff', 1.1, 11)

    # ---- G: the gallery and the Hollow Duke (far below) ----
    gz = -90.0
    room(a, 0, gz, 11, [], ceil=9)
    for k in range(4):
        ang = 45 + 90 * k
        x, z = polar(10.6, ang)
        a.entity('Painting', t3((x, 3.0, gz + z), (0, 90 - ang, 0), (3.0, 2.2, 0.15)), mesh('cube', '#ffffffff', 'art/painting.png'),
                 collider('box'), tags('focusable'), script('scripts/painting.bs', slot=k))
    a.entity('Hollow Duke', t3((0, 0, gz)), mesh('model', '#a0c8a0ff', file='models/mildew.glb', shadow=True),
             ('Animator', [('clip', q('idle')), ('speed', 1), ('loop', True), ('playing', True), ('blend', 0.2)]),
             collider('capsule', (1, 2.0, 1), 0.6, offset=(0, 1.0, 0), trigger=True), tags('enemy', 'boss'), script('scripts/hollowduke.bs'))
    a.spawn_point('gallery', 0, 0.1, gz + 8, 0)
    a.entity('Heart Pie', t3((0, 0.8, gz - 3), (0, 0, 0), 2.0), mesh('model', '#ff3048ff', file='models/heart.obj', lit=False),
             script('scripts/pickup.bs', kind='heartpie', id='tt_pie', when='tt_boss'))
    a.entity('Blue Light', t3((0, 1.5, gz), (0, 0, 0), (1.6, 3.0, 1.6)), mesh('cylinder', '#80c0ff60', lit=False, cull=False, cast=False),
             particles(rate=20, max=40, lifetime=1.5, speed=1.2, spread=10, area=(1.6, 1.6), size_start=0.15, size_end=0,
                       color_start='#c0e0ffff', color_end='#4080ff00', blend='add'),
             script('scripts/warp.bs', to='chamber', at='start', sets='thymetemple_done', when='tt_boss'))
    a.point_light(0, 6, gz, '#c0e0a0ff', 1.4, 18)
    # (for trying parts on their own)
    a.spawn_point('t_b', 0, 0.1, bz + 8, 0)
    a.spawn_point('t_d', 12, 0.1, bz, -90)
    a.spawn_point('t_e', 0, 0.1, ez + 7, 0)
    a.save()
