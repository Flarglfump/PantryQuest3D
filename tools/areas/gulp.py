"""Inside Lord Gulp: the third dungeon, in the belly of the Fizzlings' guardian sturgeon.

Fleshy round chambers joined by gullets (north is -z):
  A  the mouth: a floor switch opens the way on (it sticks)
  B  the round gut: Princess Fizzy sulks here. West to C (its door needs its switch held
     down: set Fizzy on it), east to D, north (locked) to E
  C  the jelly chamber: beat the shock jellies for the Spatula Boomerang; the map
  D  the pit: a tendril holds the bridge up (cut it with the boomerang); key and compass
  E  the north chamber: a switch for the boss key's alcove (Fizzy again); three tendrils
     hold a curtain over the way to the boss door
  F  the Gristle Knot's chamber
"""
import math

from areakit import Area, ring_floor, ring_wall, ceiling_disc, tunnel
from kit import t3, mesh, collider, tags, script, particles

H = 6.0


def polar(r, a):
    return math.cos(math.radians(a)) * r, math.sin(math.radians(a)) * r


def room(a, cx, cz, r, holes, ceil=H, floor=True):
    for k in range(3):
        ang = 120 * k + 60
        ring_wall(a.geo('flesh', cx + math.cos(math.radians(ang)) * r * 0.6, cz + math.sin(math.radians(ang)) * r * 0.6), cx, cz, r, -3.5, ceil,
                  24, [(h[0], h[1], 0, 3.0) for h in holes])
    ceiling_disc(a.geo('flesh', cx, cz), cx, cz, r, ceil, 0, 18)
    if floor:
        ring_floor(a.geo('flesh', cx, cz), cx, cz, 0, r, 0, segs=20, thick=0.5)


def gullet(a, x0, z0, x1, z1):
    tunnel(a.geo('flesh', (x0 + x1) / 2, (z0 + z1) / 2), a.geo('flesh', (x0 + x1) / 2, (z0 + z1) / 2), x0, z0, x1, z1, 0)


def glow(a, x, z, r=10):
    a.point_light(x, 4, z, '#ffa0b0ff', 1.3, r)


def build():
    a = Area('gulp', 'Inside Lord Gulp', music='music/gulp.wav', dungeon='gulp', kill_y=-20, sky='#200810ff',
             fog=(12, 34), fog_color='#3a1018ff', ambient=('#d090a0ff', 0.6), sun=('#ffc0c8ff', 0.3), sun_rot=(-80, 0, 0),
             shadows=False, chunk=16)
    # ---- A: the mouth ----
    room(a, 0, 0, 8, [(90, 1.4), (270, 1.4)])
    gullet(a, 0, 8.6, 0, 13)
    a.loadzone(0, 0, 12.6, 2.6, 3, 0.8, to='fountain', at='gulp')
    a.spawn_point('start', 0, 0.1, 6, 0)
    a.floorswitch(4.5, 0, 0, 'ga_sw')
    gullet(a, 0, -8.6, 0, -13)
    a.switchdoor(0, 0, -9.0, (2.8, 3.0, 0.5), 'ga_sw', stay=True)
    a.enemy('jelly', -3, 0.1, -2, hp=2, damage=2)
    a.entity('Drip', t3((0, H - 0.3, 0)), particles(rate=4, max=12, lifetime=1.2, speed=0.2, spread=10, area=(10, 10), gravity=8,
                                                  size_start=0.12, size_end=0.08, color_start='#ffd0d0c0', color_end='#ff808000'))
    glow(a, 0, 0)

    # ---- B: the round gut ----
    bz = -22.0
    room(a, 0, bz, 9, [(90, 1.4), (180, 1.4), (0, 1.4), (270, 1.4)])
    a.entity('Princess Fizzy', t3((-2.5, 0, bz - 3), (0, 30, 0)), mesh('model', file='models/fizzy.glb', shadow=True),
             ('Animator', [('clip', '"idle"'), ('speed', 1), ('loop', True), ('playing', True), ('blend', 0.2)]),
             collider('capsule', (1, 1.1, 1), 0.3, offset=(0, 0.55, 0), trigger=True), tags('interact', 'focusable', 'weight'),
             script('scripts/fizzy.bs'))
    a.enemy('jelly', 4, 0.1, bz + 2, hp=2, damage=2)
    glow(a, 0, bz, 12)
    # west: the jelly chamber's door, held by a switch beside it
    cx = -22.0
    gullet(a, -9.6, bz, cx + 6.6, bz)
    a.switchdoor(-10.0, 0, bz, (0.5, 3.0, 2.8), 'gb_sw')
    a.floorswitch(-6.0, 0, bz + 3.2, 'gb_sw')
    a.sign(-6.8, 0, bz - 2.6, 90, 'gulp_sw_tip')
    room(a, cx, bz, 7, [(0, 1.4)])
    for dx, dz in [(-2, -3), (-3, 2.5), (1.5, 2)]:
        a.enemy('jelly', cx + dx, 0.1, bz + dz, hp=2, damage=2, group='gc_jelly')
    a.chest(cx - 4.2, 0, bz, -90, 'boomerang', 'gc_boomerang', appear='clear:gc_jelly', big=True)
    a.chest(cx + 1, 0, bz - 5, 180, 'map_gulp', 'gc_map')
    glow(a, cx, bz)

    # ---- D: the pit (east) ----
    dx0 = 22.0
    gullet(a, 9.6, bz, dx0 - 6.6, bz)
    room(a, dx0, bz, 7, [(180, 1.4)], floor=False)
    a.geo('flesh', dx0 - 5, bz).box((dx0 - 7.2, -0.5, bz - 7), (dx0 - 2.6, 0, bz + 7), uvs=0.35)
    a.geo('flesh', dx0 + 5, bz).box((dx0 + 2.4, -0.5, bz - 7), (dx0 + 7.2, 0, bz + 7), uvs=0.35)
    a.geo('flesh', dx0, bz).box((dx0 - 2.6, -3.6, bz - 7), (dx0 + 2.4, -3.0, bz + 7), uvs=0.35)
    a.entity('Acid', t3((dx0, -2.6, bz)), collider('box', (5.0, 0.8, 14), trigger=True), tags('pit'))
    a.geo('lava', dx0, bz).quad((dx0 - 2.6, -2.9, bz + 7), (dx0 + 2.4, -2.9, bz + 7), (dx0 + 2.4, -2.9, bz - 7), (dx0 - 2.6, -2.9, bz - 7),
                                (0, 0), (2, 0), (2, 5), (0, 5))
    a.switchdoor(dx0 - 0.1, -3.36, bz, (4.96, 0.3, 2.4), 'gd_bridge', stay=True, material='planks', color='#e8d8c0ff')
    a.tendril(dx0 + 4.5, H - 0.4, bz, 'gd_bridge', count=1)
    a.sign(dx0 - 4.5, 0, bz - 2.6, -90, 'gulp_tendril')
    a.chest(dx0 + 5.2, 0, bz - 2.2, 90, 'key', 'gd_key')
    a.chest(dx0 + 5.2, 0, bz + 2.2, 90, 'compass_gulp', 'gd_compass')
    a.enemy('jelly', dx0 - 4.5, 0.1, bz + 3.5, hp=2, damage=2)
    glow(a, dx0, bz)

    # ---- E: the north chamber, behind the locked door ----
    ez = -48.0
    gullet(a, 0, bz - 9.6, 0, ez + 8.6)
    a.entity('Locked Door', t3((0, 1.4, bz - 11), (0, 0, 0), (2.4, 2.8, 0.3)), mesh('cube', '#c86070ff', 'art/flesh.png'),
             collider('box'), tags('interact'), script('scripts/lockdoor.bs', id='gulp_north'))
    a.entity('Lock', t3((0, 1.3, bz - 11.2), (0, 0, 0), (0.5, 0.6, 0.2)), mesh('cube', '#c8a040ff'))
    room(a, 0, ez, 9, [(90, 1.4), (270, 1.4), (180, 1.4)])
    a.floorswitch(4.5, 0, ez + 2, 'ge_sw')
    # the boss key's alcove (west), behind a door the switch holds open
    gullet(a, -8.6, ez, -14, ez)
    a.switchdoor(-9.6, 0, ez, (0.5, 3.0, 2.8), 'ge_sw')
    room(a, -18, ez, 4.5, [(0, 1.4)])
    a.chest(-20, 0, ez, -90, 'bosskey_gulp', 'ge_bosskey', big=True)
    # three tendrils hold the curtain over the way north
    for k, ang in enumerate((-150, -90, -30)):
        x, z = polar(7.8, ang)
        a.tendril(x, H - 0.3, ez + z, 'ge_knot%d' % k, set_='ge_knot', count=3)
    a.enemy('jelly', -3, 0.1, ez + 3, hp=2, damage=2)
    a.enemy('jelly', 3, 0.1, ez - 3, hp=2, damage=2)
    glow(a, 0, ez, 12)
    gullet(a, 0, ez - 8.6, 0, ez - 14)
    a.switchdoor(0, 0, ez - 9.2, (2.8, 3.0, 0.5), 'ge_knot', stay=True)
    a.entity('Boss Door', t3((0, 1.5, ez - 12), (0, 0, 0), (2.6, 3.0, 0.4)), mesh('cube', '#7a2a3aff', 'art/flesh.png'),
             collider('box'), tags('interact'), script('scripts/lockdoor.bs', id='gulp_boss_door', boss=True))

    # ---- F: the Gristle Knot ----
    fz = -72.0
    room(a, 0, fz, 12, [(90, 1.4)], ceil=9)
    a.entity('Gristle Knot', t3((0, 4.5, fz - 3)), mesh('model', '#e8d0b0ff', file='models/knot.obj', shadow=True),
             collider('sphere', radius=1.4), ('RigidBody3D', [('type', 'kinematic')]), tags('enemy', 'boss'), script('scripts/gristle.bs'))
    a.entity('Heart Pie', t3((0, 0.8, fz + 4), (0, 0, 0), 2.0), mesh('model', '#ff3048ff', file='models/heart.obj', lit=False),
             script('scripts/pickup.bs', kind='heartpie', id='gulp_pie', when='gulp_boss'))
    a.entity('Blue Light', t3((0, 1.5, fz), (0, 0, 0), (1.6, 3.0, 1.6)), mesh('cylinder', '#80c0ff60', lit=False, cull=False, cast=False),
             particles(rate=20, max=40, lifetime=1.5, speed=1.2, spread=10, area=(1.6, 1.6), size_start=0.15, size_end=0,
                       color_start='#c0e0ffff', color_end='#4080ff00', blend='add'),
             script('scripts/warp.bs', to='fountain', at='gulp', sets='gulp_done', when='gulp_boss'))
    glow(a, 0, fz, 18)
    # (for trying parts on their own)
    a.spawn_point('t_b', 0, 0.1, bz + 7, 0)
    a.spawn_point('t_d', 12, 0.1, bz, -90)
    a.spawn_point('t_e', 0, 0.1, ez + 6, 0)
    a.spawn_point('t_boss', 0, 0.1, ez - 13, 0)
    a.save()
