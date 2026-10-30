"""The Fondue Forge: the fifth dungeon, in the crater of Mount Fondue (the Risen era).

Hot: without the Oven Apron the heat hurts. North is -z. Rooms:
  A  the entry bridge over molten cheese; a Hardtack locked in a cell
  B  the great forge hall: a pit of molten cheese in the middle
  C  west: the Crust Golems guard the Meat Tenderizer; the map
  D  east: a rusted switch (only the Tenderizer moves it) opens the small key's alcove;
     a cracked pillar hides the compass
  E  north (locked): another rusted switch raises a bridge to the Boss Key; a prisoner
  F  Gratinox's lair: a ring of holes into the molten cheese
"""
import math

from areakit import Area, ring_floor, ring_wall, ceiling_disc, tunnel, box_wall
from kit import t3, mesh, collider, tags, script, particles, q

H = 8.0


def polar(r, a):
    return math.cos(math.radians(a)) * r, math.sin(math.radians(a)) * r


def room(a, cx, cz, r, holes, ceil=H, floor=True, r0=0.0):
    for k in range(3):
        ang = 120 * k + 60
        ring_wall(a.geo('rock', cx + math.cos(math.radians(ang)) * r * 0.6, cz + math.sin(math.radians(ang)) * r * 0.6), cx, cz, r, -4, ceil,
                  24, [(h[0], h[1], 0, 3.0) for h in holes])
    ceiling_disc(a.geo('rock', cx, cz), cx, cz, r, ceil, 0, 18)
    if floor:
        ring_floor(a.geo('stone', cx, cz), cx, cz, r0, r, 0, segs=20, thick=0.5)


def lava_pool(a, x, z, r, y=-1.2):
    a.geo('lava', x, z).cylinder((x, y, z), r, 0.01, 16, top=True, uvs=0.4)
    a.entity('Molten Cheese', t3((x, y + 0.3, z)), collider('box', (r * 1.6, 0.8, r * 1.6), trigger=True), tags('lava'))


def hall(a, x0, z0, x1, z1):
    tunnel(a.geo('stone', (x0 + x1) / 2, (z0 + z1) / 2), a.geo('rock', (x0 + x1) / 2, (z0 + z1) / 2), x0, z0, x1, z1, 0)


def cell(a, x, z, yaw, who):
    """A barred cell with a prisoner in it."""
    a.npc(who, x, 0, z, yaw, model='hardtack', reach=3.0)
    fx, fz = -math.sin(math.radians(yaw)) * 1.4, -math.cos(math.radians(yaw)) * 1.4
    for k in range(5):
        sx, sz = math.cos(math.radians(yaw)) * (k - 2) * 0.5, -math.sin(math.radians(yaw)) * (k - 2) * 0.5
        a.geo('stone', x + fx + sx, z + fz + sz).cylinder((x + fx + sx, 0, z + fz + sz), 0.08, 3.0, 6)
    a.entity('Cell Bars', t3((x + fx, 1.5, z + fz), (0, yaw, 0), (2.6, 3.0, 0.3)), collider('box'))


def build():
    a = Area('forge', 'Fondue Forge', music='music/caverns.wav', dungeon='forge', kill_y=-20, sky='#200800ff',
             fog=(12, 36), fog_color='#3a1004ff', ambient=('#e09060ff', 0.6), sun=('#ffa060ff', 0.4), sun_rot=(-80, 0, 0),
             shadows=False, chunk=16, hot=True)
    # ---- A: the entry bridge ----
    for x0, x1 in [(-7, -7), (7, 7)]:
        box_wall(a, 'rock', x0, 10, x1, -10, -4, H, thick=0.8, uvs=0.3)
    box_wall(a, 'rock', -7, 10, -1.5, 10, -4, H, thick=0.8, uvs=0.3)
    box_wall(a, 'rock', 1.5, 10, 7, 10, -4, H, thick=0.8, uvs=0.3)
    box_wall(a, 'rock', -7, -10, -1.2, -10, -4, H, thick=0.8, uvs=0.3)
    box_wall(a, 'rock', 1.2, -10, 7, -10, -4, H, thick=0.8, uvs=0.3)
    a.geo('rock', 0, 0).box((-7, H, -10), (7, H + 0.4, 10), uvs=0.3, sides=('ny',))
    a.geo('stone', 0, 0).box((-1.6, -0.5, -10), (1.6, 0, 10), uvs=0.35)
    a.geo('stone', -4.5, 6).box((-7, -0.5, 4), (-1.6, 0, 9.6), uvs=0.35)
    for sx in (-1, 1):
        lava_pool(a, sx * 4.3, -2, 3.2)
    cell(a, -4.5, 7.6, 90, 'prisoner')
    a.loadzone(0, 0, 9.6, 3, 3, 0.8, to='fondue', at='forge')
    a.spawn_point('start', 0, 0.1, 7.5, 0)
    a.sign(1.4, 0, 5, 0, 'forge_enter')
    a.point_light(0, 4, 0, '#ff9050ff', 1.3, 14)
    hall(a, 0, -10, 0, -12.5)

    # ---- B: the great forge hall ----
    bz = -23.0
    room(a, 0, bz, 11, [(90, 1.4), (180, 1.4), (0, 1.4), (270, 1.4)], r0=5.0)
    lava_pool(a, 0, bz, 5.2)
    a.entity('Heat Shimmer', t3((0, -0.8, bz)), particles(rate=10, max=40, lifetime=1.6, speed=1.0, spread=20, area=(8, 8), gravity=-0.6,
                                                         size_start=0.3, size_end=0, color_start='#ffd070ff', color_end='#ff400000', blend='add'))
    for ang in (45, 135, 225, 315):
        x, z = polar(8.5, ang)
        a.enemy('roller', x, 0.1, bz + z, hp=3, damage=4)
    a.point_light(0, 5, bz, '#ff9050ff', 1.5, 16)

    # ---- C: the Crust Golems and the Meat Tenderizer (west) ----
    cx = -24.0
    hall(a, -10.6, bz, cx + 6.6, bz)
    room(a, cx, bz, 7, [(0, 1.4)])
    for dx, dz in [(-2, -2.5), (-2, 2.5)]:
        a.enemy('crustling', cx + dx, 0.1, bz + dz, hp=6, damage=4, group='fg_mini')
    a.chest(cx - 4.4, 0, bz, -90, 'hammer', 'fg_hammer', appear='clear:fg_mini', big=True)
    a.chest(cx + 1, 0, bz - 5, 180, 'map_forge', 'fg_map')
    a.point_light(cx, 4, bz, '#ff9050ff', 1.2, 11)

    # ---- D: the rusted switch (east) ----
    dx0 = 24.0
    hall(a, 10.6, bz, dx0 - 6.6, bz)
    room(a, dx0, bz, 7, [(180, 1.4), (270, 1.4)])
    a.hammerswitch(dx0 + 1, 0, bz + 2, 'fg_rust')
    hall(a, dx0, bz - 6.6, dx0, bz - 10)
    a.switchdoor(dx0, 0, bz - 7.2, (2.8, 3.0, 0.5), 'fg_rust', stay=True, material='stone', color='#a08070ff')
    room(a, dx0, bz - 13, 3.5, [(90, 1.4)])
    a.chest(dx0, 0, bz - 14.5, 180, 'key', 'fg_key')
    a.cracked(dx0 + 4.5, 0, bz - 3, 1.4, 3.0, 1.4, 'fg_pillar')
    a.chest(dx0 + 5.3, 0, bz - 4.6, 90, 'compass_forge', 'fg_compass')
    a.point_light(dx0, 4, bz, '#ff9050ff', 1.2, 11)

    # ---- E: north, behind the locked door ----
    ez = -50.0
    hall(a, 0, bz - 11, 0, ez + 9.6)
    a.entity('Locked Door', t3((0, 1.4, bz - 12), (0, 0, 0), (2.4, 2.8, 0.3)), mesh('cube', '#ffffffff', 'art/planks.png'),
             collider('box'), tags('interact'), script('scripts/lockdoor.bs', id='fg_north'))
    a.entity('Lock', t3((0, 1.3, bz - 12.2), (0, 0, 0), (0.5, 0.6, 0.2)), mesh('cube', '#c8a040ff'))
    room(a, 0, ez, 10, [(90, 1.4), (270, 1.4)], floor=False)
    a.geo('stone', 0, ez + 6).box((-10, -0.5, ez + 3), (10, 0, ez + 10), uvs=0.35)       # south half
    a.geo('stone', 0, ez - 7).box((-10, -0.5, ez - 10), (10, 0, ez - 4.5), uvs=0.35)     # north half
    a.geo('stone', 0, ez).box((-10, -3.6, ez - 4.6), (10, -3.0, ez + 3.1), uvs=0.35)
    a.geo('lava', 0, ez).quad((-10, -1.2, ez + 3), (10, -1.2, ez + 3), (10, -1.2, ez - 4.5), (-10, -1.2, ez - 4.5), (0, 0), (5, 0), (5, 2), (0, 2))
    a.entity('Molten Cheese', t3((0, -0.9, ez - 0.8)), collider('box', (20, 0.8, 7.6), trigger=True), tags('lava'))
    a.hammerswitch(-5, 0, ez + 5, 'fg_rust2')
    a.switchdoor(0, -3.3, ez - 0.8, (2.6, 0.3, 7.8), 'fg_rust2', stay=True, material='stone', color='#a08070ff')
    a.chest(-6, 0, ez - 7, 180, 'bosskey_forge', 'fg_bosskey', big=True)
    cell(a, 6, ez - 7.5, 0, 'prisoner2')
    a.point_light(0, 5, ez, '#ff9050ff', 1.3, 14)
    hall(a, 0, ez - 9.6, 0, ez - 14)
    a.entity('Boss Door', t3((0, 1.5, ez - 12), (0, 0, 0), (2.6, 3.0, 0.4)), mesh('cube', '#8a3a2aff', 'art/planks.png'),
             collider('box'), tags('interact'), script('scripts/lockdoor.bs', id='fg_boss_door', boss=True))

    # ---- F: Gratinox's lair ----
    fz = -78.0
    room(a, 0, fz, 12, [(90, 1.4)], ceil=11)
    for k in range(6):
        x, z = polar(7, k * 60 + 30)
        a.geo('lava', x, fz + z).cylinder((x, 0.03, fz + z), 1.3, 0.0, 12, top=True, uvs=0.4)
        a.entity('Hole', t3((x, 0.3, fz + z)), collider('box', (1.6, 0.6, 1.6), trigger=True), tags('lava'))
    a.entity('Gratinox', t3((0, 0, fz)), mesh('model', '#ff9050ff', 'art/crust.png', file='models/gratinox.obj'),
             collider('sphere', radius=1.0, trigger=True), tags('enemy', 'boss'), script('scripts/gratinox.bs'))
    a.entity('Heart Pie', t3((0, 0.8, fz + 4), (0, 0, 0), 2.0), mesh('model', '#ff3048ff', file='models/heart.obj', lit=False),
             script('scripts/pickup.bs', kind='heartpie', id='fg_pie', when='forge_boss'))
    a.entity('Blue Light', t3((0, 1.5, fz), (0, 0, 0), (1.6, 3.0, 1.6)), mesh('cylinder', '#80c0ff60', lit=False, cull=False, cast=False),
             particles(rate=20, max=40, lifetime=1.5, speed=1.2, spread=10, area=(1.6, 1.6), size_start=0.15, size_end=0,
                       color_start='#c0e0ffff', color_end='#4080ff00', blend='add'),
             script('scripts/warp.bs', to='chamber', at='start', sets='forge_done', when='forge_boss'))
    a.point_light(0, 7, fz, '#ff9050ff', 1.6, 20)
    a.spawn_point('t_b', 0, 0.1, bz + 8, 0)
    a.spawn_point('t_d', 13, 0.1, bz, -90)
    a.spawn_point('t_e', 0, 0.1, ez + 8, 0)
    a.spawn_point('t_boss', 0, 0.1, ez - 13, 0)
    a.save()
