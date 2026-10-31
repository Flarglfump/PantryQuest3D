"""The Great Crock: the first dungeon, inside Mother Starter.

The heart of it is the Central Rise, a tall round chamber: the ground floor (1F, y 0) is a
ring round a mould web over the basement; a ledge runs round at 2F (y 4) and another along
the north side at 3F (y 8), with vines between them and a plank jutting out over the middle.
Off it: the Lift room (east, 2F: riding crusts over the starter to the map and a key), the
Shooter room (west, 2F, locked: fuzzballs, then the Pea Shooter), the Compass room (north,
3F, behind an eye switch). Diving from the plank tears the web and drops Sprig into the
basement (B1, y -6), where the Scrub brothers guard the way to the last web, which only
fire burns: below it lies the Queen.
"""
import math

from areakit import Area, ring_floor, ring_wall, ceiling_disc, tunnel
from kit import t3, mesh, collider, tags, script, particles, light, q

B1, F1, F2, F3, TOP = -6.0, 0.0, 4.0, 8.0, 13.0
R = 12.0


def polar(r, a):
    return math.cos(math.radians(a)) * r, math.sin(math.radians(a)) * r


def vine_yaw(a):
    """The yaw of something facing the middle from angle a on a round wall."""
    return 90.0 - a


def torch(a, x, y, z, lamp=True, flame_h=0.6):
    a.entity('Torch', t3((x, y + 0.2, z), (0, 0, 0), (0.4, 0.4, 0.4)), mesh('cylinder', '#ffffffff', 'art/stone.png'),
             collider('box', (1, 1, 1)), tags('torch'), script('scripts/torch.bs', flame_h=flame_h - 0.2))
    a.entity('Flame', t3((x, y + flame_h, z)), particles(rate=30, max=40, lifetime=0.5, lifetime_random=0.3, speed=0.8, spread=25,
                                                       area=(0.25, 0.25), gravity=-1.5, size_start=0.22, size_end=0.02,
                                                       color_start='#ffe080ff', color_end='#ff300000', blend='add'))
    if lamp:
        a.point_light(x, y + 1.0, z, '#ffb060ff', 1.4, 10)


def build():
    a = Area('crock', 'The Great Crock', music='music/crock.wav', dungeon='crock', kill_y=-30, sky='#2a1c10ff',
             fog=(12, 34), fog_color='#2a1c10ff', ambient=('#a08868ff', 0.55), sun=('#ffe0b0ff', 0.35), sun_rot=(-70, 20, 0),
             shadows=False, chunk=16)

    # ================= the Central Rise =================
    g = lambda m: a.geo(m, 0, 0)
    holes = [(90, 1.3, F1, F1 + 2.8), (0, 1.3, F2, F2 + 2.8), (180, 1.3, F2, F2 + 2.8), (270, 1.3, F3, F3 + 2.8), (270, 1.3, B1, B1 + 2.8)]
    for k in range(4):            # (the wall, in four parts so the renderer can skip some)
        o = a.geo('dough_wall', *polar(8, 45 + 90 * k))
        ring_wall(o, 0, 0, R, B1 - 0.5, TOP, 32, holes)
    ceiling_disc(g('ceiling'), 0, 0, R, TOP, 0, 24)
    ring_floor(g('dough'), 0, 0, 0, R, B1, segs=28, thick=0.5)                         # the basement floor
    ring_floor(g('dough'), 0, 0, 4, 9.5, F1, segs=28, thick=0.6)                       # 1F: the inner ring
    ring_floor(g('dough'), 0, 0, 9.5, R, F1, 14, 346, segs=32, thick=0.6)              # ... and the outer, with a gap east
    ring_floor(g('crust'), 0, 0, 9.0, 9.5, F1 - 0.01, -14, 14, segs=4, thick=6.0)      # a crust wall up from B1 there (vines; just under the floor's level)
    ring_floor(g('crust'), 0, 0, 9.0, R, F2, 0, 360, segs=36, thick=0.6)               # 2F ledge
    ring_floor(g('crust'), 0, 0, 8.6, R, F2, 262, 278, segs=3, thick=4.0)              # a pillar under it (vines 1F->2F)
    ring_floor(g('crust'), 0, 0, 9.5, R, F3, 200, 340, segs=16, thick=0.6)             # 3F ledge (north)
    ring_floor(g('crust'), 0, 0, 9.0, 9.5, F3, 220, 236, segs=2, thick=4.0)            # a pillar under it (vines 2F->3F)
    # the plank over the middle, from 3F
    g('planks').box((-0.7, F3 - 0.25, -9.6), (0.7, F3, -3.0), uvs=0.6)
    a.entity('Plank Tip', t3((0, F3 + 0.3, -3.1), (0, 0, 0), (1.2, 0.1, 0.1)), mesh('cube', '#a07040ff'))
    # vines: 1F -> 2F (north, on the pillar), 2F -> 3F (north-west), B1 -> 1F (east, in the gap)
    x, z = polar(8.6, 270)
    a.vine(x, F1, z, 1.4, F2 - F1, vine_yaw(270), top=F2)
    x, z = polar(9.0, 228)
    a.vine(x, F2, z, 1.4, F3 - F2, vine_yaw(228), top=F3)
    x, z = polar(9.5, 0)
    a.vine(x, B1, z, 1.4, F1 - B1, vine_yaw(180), top=F1)    # (faces out, into the gap)
    # the web over the middle: falling on it from 3F tears it
    a.entity('Web', t3((0, F1 + 0.02, 0), (0, 0, 0), (8.0, 0.08, 8.0)), mesh('cylinder', '#ffffffff', 'art/web.png', uv=(3, 3), cull=False, cast=False),
             collider('box', (1, 1, 1)), script('scripts/web.bs', id='crock_web1', breaks='fall', radius=3.6))
    # the starter pond in the basement (just to look at: it's shallow)
    ring_floor(a.geo('starter', 0, 0), 0, 0, 0, 7.5, B1 + 0.15, segs=20, thick=0, edges=False)
    # torches and things on 1F
    for ang in (60, 120):
        x, z = polar(10.8, ang)
        torch(a, x, F1, z)
    for ang in (200, 215, 330):
        x, z = polar(10.6, ang)
        a.pot(x, F1, z)
    for ang in (150, 30):
        x, z = polar(7, ang)
        a.enemy('fuzzball', x, F1 + 0.1, z, hp=2)
    for ang in (100, 160, 300):
        x, z = polar(10.5, ang)
        a.pot(x, F2, z)
    x, z = polar(10.6, 300)
    a.chest(x, F3, z, vine_yaw(300), 'bean20', 'crock_3f')

    # ================= the entrance =================
    tunnel(a.geo('dough', 0, 15), a.geo('dough_wall', 0, 15), 0, R - 0.5, 0, 19, F1)
    a.loadzone(0, F1, 18.8, 2.4, 2.6, 0.6, to='sprouthollow', at='crock')
    a.spawn_point('start', 0, F1 + 0.1, 16.5, 0)
    # (for trying parts on their own)
    a.spawn_point('t_2f', 10.5, F2 + 0.1, 0, 90)
    a.spawn_point('t_3f', 0, F3 + 0.1, -10.5, 0)
    a.spawn_point('t_b1', 0, B1 + 0.1, 0, 0)
    a.spawn_point('t_lair', 0, -6 + 0.1, -16.5, 0)
    a.sign(1.6, F1, 13.8, 0, 'crock_enter')

    # ================= the Lift room (east, 2F) =================
    cx = 25.0
    tunnel(a.geo('crust', 14, 0), a.geo('dough_wall', 14, 0), R - 0.5, 0, cx - 7.6, 0, F2)
    ring_wall(a.geo('dough_wall', cx, 0), cx, 0, 8, -1, 10, 24, [(180, 1.3, F2, F2 + 2.8)])
    ceiling_disc(a.geo('ceiling', cx, 0), cx, 0, 8, 10, 0, 16)
    ring_floor(a.geo('rot', cx, 0), cx, 0, 0, 8, 0, segs=20, thick=0.5)
    ring_floor(a.geo('starter', cx, 0), cx, 0, 0, 8, 0.6, segs=20, thick=0, edges=False)
    a.geo('crust', cx - 6, 0).box((cx - 8.2, 0, -2.0), (cx - 5.5, F2, 2.0), uvs=0.5)       # the ledge in
    a.geo('crust', cx + 6, 0).box((cx + 5.5, 0, -3.2), (cx + 8.2, F2, 3.2), uvs=0.5)       # the far ledge
    a.entity('Starter Pit', t3((cx, 0.6, 0)), collider('box', (15, 1.2, 15), trigger=True), tags('pit'))
    a.entity('Crust Lift', t3((cx - 4.5, F2 - 0.25, 0), (0, 0, 0), (2.0, 0.5, 2.0)), mesh('cube', '#ffffffff', 'art/crust.png'), collider('box', (1, 1, 1)),
             ('RigidBody3D', [('type', 'kinematic')]), tags('platform'),
             script('scripts/platform.bs', a=(cx - 4.5, F2 - 0.25, 0), b=(cx + 4.5, F2 - 0.25, 0), speed=1.8, wait=1.4))
    a.chest(cx + 7.0, F2, -1.8, 90, 'map_crock', 'crock_map')
    a.chest(cx + 7.0, F2, 1.8, 90, 'key', 'crock_key1')
    torch(a, cx + 7.3, F2, 0, flame_h=0.7)

    # ================= the Shooter room (west, 2F, locked) =================
    cx = -24.0
    tunnel(a.geo('crust', -14, 0), a.geo('dough_wall', -14, 0), -R + 0.5, 0, cx + 6.6, 0, F2)
    a.entity('Locked Door', t3((-14.6, F2 + 1.4, 0), (0, 90, 0), (2.4, 2.8, 0.3)), mesh('cube', '#ffffffff', 'art/planks.png'),
             collider('box'), tags('interact'), script('scripts/lockdoor.bs', id='crock_shooter'))
    a.entity('Lock', t3((-14.4, F2 + 1.3, 0), (0, 90, 0), (0.5, 0.6, 0.2)), mesh('cube', '#c8a040ff'))
    ring_wall(a.geo('dough_wall', cx, 0), cx, 0, 7, F2 - 0.5, 11, 24, [(0, 1.3, F2, F2 + 2.8)])
    ceiling_disc(a.geo('ceiling', cx, 0), cx, 0, 7, 11, 0, 16)
    ring_floor(a.geo('dough', cx, 0), cx, 0, 0, 7, F2, segs=20, thick=0.5)
    for dx, dz in [(-2, -3), (-3, 2.5), (1, 3)]:
        a.enemy('fuzzball', cx + dx, F2 + 0.1, dz, hp=2, group='shooter')
    a.chest(cx - 4.5, F2, 0, -90, 'shooter', 'crock_shooter', appear='clear:shooter', big=True)
    for dx, dz in [(3, -5), (4, 4.6)]:
        a.pot(cx + dx, F2, dz)
    torch(a, cx - 5.6, F2, -3)

    # ================= the Compass room (north, 3F, behind the eye) =================
    cz = -23.0
    tunnel(a.geo('crust', 0, -14), a.geo('dough_wall', 0, -14), 0, -R + 0.5, 0, cz + 5.6, F3)
    a.blocker(0, F3, -12.4, (2.6, 2.8, 0.3), 'crock_eye')
    a.entity('Eye Switch', t3((0, F3 + 3.3, -11.75), (0, 0, 0), (0.9, 0.5, 0.3)), mesh('sphere', '#f4ecd8ff', lit=False),
             tags('focusable', 'shootable'), script('scripts/eyeswitch.bs', id='crock_eye'))
    a.entity('Eye Pupil', t3((0, F3 + 3.3, -11.58), (0, 0, 0), (0.28, 0.28, 0.1)), mesh('sphere', '#c02020ff', lit=False),
             script('scripts/blocker.bs', until='crock_eye'))
    ring_wall(a.geo('dough_wall', 0, cz), 0, cz, 6, F3 - 0.5, 13, 24, [(90, 1.3, F3, F3 + 2.8)])
    ceiling_disc(a.geo('ceiling', 0, cz), 0, cz, 6, 13, 0, 16)
    ring_floor(a.geo('dough', 0, cz), 0, cz, 0, 6, F3, segs=20, thick=0.5)
    a.chest(0, F3, cz - 3.6, 180, 'compass_crock', 'crock_compass')
    a.enemy('scrub', 3.2, F3, cz - 1.5, hp=1)
    for dx, dz in [(-4, 1), (-3.5, -3)]:
        a.pot(dx, F3, cz + dz)
    a.point_light(0, F3 + 3, cz, '#ffc080ff', 1.2, 9)

    # ================= the basement: the Scrub brothers, the bars, the fire web =================
    for i, dx in enumerate((-6.0, 0, 6.0)):
        a.enemy('scrub', dx, B1, -8.0 - (1.0 if i == 1 else 0), hp=1, trio=True, order=i)
    a.entity('ScrubTrio', t3((0, B1, 0)), script('scripts/scrubtrio.bs'))
    a.sign(-5.5, B1, -5.0, 200, 'crock_scrubs')
    a.blocker(0, B1, -12.3, (2.6, 2.8, 0.3), 'crock_scrubs')
    for x, z in [(6, 6), (-7, 4), (8, 3.5)]:
        a.pot(x, B1, z)
    cz = -21.0
    tunnel(a.geo('dough', 0, -14), a.geo('dough_wall', 0, -14), 0, -R + 0.5, 0, cz + 4.3, B1)
    ring_wall(a.geo('dough_wall', 0, cz), 0, cz, 4.6, B1 - 0.5, B1 + 4, 20, [(90, 1.3, B1, B1 + 2.8)])
    ceiling_disc(a.geo('ceiling', 0, cz), 0, cz, 4.6, B1 + 4, 0, 16)
    ring_floor(a.geo('dough', 0, cz), 0, cz, 2.0, 4.6, B1, segs=20, thick=0.5)
    ring_wall(a.geo('dough_wall', 0, cz), 0, cz, 2.0, -8.6, B1 - 0.5, 12)            # the shaft down
    a.entity('Fire Web', t3((0, B1 + 0.03, cz), (0, 0, 0), (4.2, 0.08, 4.2)), mesh('cylinder', '#ffffffff', 'art/web.png', uv=(2, 2), cull=False, cast=False),
             collider('box', (1, 1, 1)), tags('focusable'), script('scripts/web.bs', id='crock_web2', breaks='fire', radius=2.2))
    torch(a, 0.7, B1, -17.9, lamp=False, flame_h=0.6)
    a.entity('Torch Glow', t3((0, B1 + 1.2, -17.9)), light('point', '#ffb060ff', 1.0, range=6))

    # ================= the Queen's lair =================
    LY = -16.0
    ring_wall(a.geo('mould', 0, cz), 0, cz, 10, LY - 0.5, -8.6, 28)
    ceiling_disc(a.geo('ceiling', 0, cz), 0, cz, 10, -8.6, 2.0, 24)
    ring_floor(a.geo('mould', 0, cz), 0, cz, 0, 10, LY, segs=24, thick=0.5)
    a.entity('Queen', t3((0, -9.6, cz - 4)), mesh('model', file='models/queen.glb', shadow=False),
             ('Animator', [('clip', q('idle')), ('speed', 1), ('loop', True), ('playing', True), ('blend', 0.15)]),
             collider('capsule', (1, 2.2, 1), 1.3, offset=(0, 1.1, 0)), ('RigidBody3D', [('type', 'kinematic')]),
             tags('enemy', 'focusable', 'boss'), script('scripts/queen.bs', ceiling=-9.6, floor_y=LY))
    a.entity('Queen Eye', t3((0, -9, cz - 5)), mesh('sphere', '#f0f0d0ff', lit=False, cast=False))
    a.entity('Heart Pie', t3((0, LY + 0.8, cz + 3), (0, 0, 0), 2.0), mesh('model', '#ff3048ff', file='models/heart.obj', lit=False),
             script('scripts/pickup.bs', kind='heartpie', id='crock_pie', when='crock_boss'))
    a.entity('Blue Light', t3((0, LY + 1.5, cz), (0, 0, 0), (1.6, 3.0, 1.6)), mesh('cylinder', '#80c0ff60', lit=False, cull=False, cast=False),
             particles(rate=20, max=40, lifetime=1.5, speed=1.2, spread=10, area=(1.6, 1.6), size_start=0.15, size_end=0,
                       color_start='#c0e0ffff', color_end='#4080ff00', blend='add'),
             script('scripts/warp.bs', to='sprouthollow', at='grove', sets='crock_done', when='crock_boss'))
    a.point_light(0, LY + 5, cz, '#c0ff90ff', 1.3, 16)
    a.save()
