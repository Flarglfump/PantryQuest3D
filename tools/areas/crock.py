"""The Great Crock: the first dungeon, inside Mother Starter.

Built round three things Sprig learns here, one after another:
  - crust blocks: grab one (Action) and push or pull it a step; it holds a floor switch down
  - warm dough: a dough column rises while he stands on it, and sinks when he steps off
  - the Pea Shooter (found here): eyes over doors, and a pea shot through a flame catches
    fire - it burns mould webs and lights fire-bowls, and a lit bowl's warmth raises the
    cold dough columns round it for good

The Kneading Hall is the middle: the way in from the south, the Crate Room east (a block on
a switch: a small key; the DUNGEON MAP for clearing the fuzzballs), the Proofing Room west
(locked: warm columns up to a ledge, a scrub spitting nuts, the Pea Shooter). A pea in the
eye under the hall's balcony opens the Furnace Room (north): two fire-bowls across a chasm
raise its columns into a bridge, and a web burnt by a fire pea guards the second key (and
the COMPASS is over there). A warm column, behind a web, rises to the balcony: the Boss Key
room behind the locked door north (two blocks on two switches), and the big door west, to
the shaft down to Queen Mildewmite's lair.

North is -z. 1F is y 0, the balcony and the rooms off it y 4; the lair is far below.
"""
import math

from areakit import Area, ring_floor, ring_wall, ceiling_disc
from kit import t3, mesh, collider, tags, script, particles, light, q

F1, F2, LAIR = 0.0, 4.0, -12.0
WALL = 0.5          # wall thickness (walls stand just outside a room's floor)


# ---- building blocks ----

def box_room(a, floor, wall, x0, z0, x1, z1, y, h, doors=(), sides='nsew', ceiling='ceiling', holes=()):
    """A box room: floor (top at y) over x0..x1, z0..z1, walls of `wall` outside it on the
    `sides` listed, a ceiling at y + h. doors: (side, centre, width, bottom, top) cut out of
    walls (side n: z0, s: z1, w: x0, e: x1; centre along the wall; heights absolute).
    holes: (x0, z0, x1, z1) left out of the floor."""
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    if floor:
        for (fx0, fz0, fx1, fz1) in split_rect((x0, z0, x1, z1), holes):
            a.geo(floor, (fx0 + fx1) / 2, (fz0 + fz1) / 2).box((fx0, y - 0.5, fz0), (fx1, y, fz1), uvs=0.35)
    top = y + h
    if ceiling:              # (over the walls too, but not past an open end: that's the next room's wall)
        ex0, ex1 = x0 - (WALL if 'w' in sides else 0), x1 + (WALL if 'e' in sides else 0)
        ez0, ez1 = z0 - (WALL if 'n' in sides else 0), z1 + (WALL if 's' in sides else 0)
        a.geo(ceiling, cx, cz).box((ex0, top, ez0), (ex1, top + 0.4, ez1), uvs=0.3)
    for side in sides:
        cut = [(c - w / 2, c + w / 2, b, t) for (s, c, w, b, t) in doors if s == side]
        if side in 'ns':
            zz = z0 - WALL if side == 'n' else z1
            span = (x0 - WALL, x1 + WALL)
            def put(u0, u1, b, t, zz=zz):
                a.geo(wall, (u0 + u1) / 2, zz).box((u0, b, zz), (u1, t, zz + WALL), uvs=0.3)
        else:
            xx = x0 - WALL if side == 'w' else x1
            span = (z0, z1)
            def put(u0, u1, b, t, xx=xx):
                a.geo(wall, xx, (u0 + u1) / 2).box((xx, b, u0), (xx + WALL, t, u1), uvs=0.3)
        wall_with_doors(put, span, y - 0.5, top, cut)


def split_rect(r, holes):
    """The rectangle r less the holes, as rectangles."""
    out = [r]
    for (hx0, hz0, hx1, hz1) in holes:
        nxt = []
        for (x0, z0, x1, z1) in out:
            if hx1 <= x0 or hx0 >= x1 or hz1 <= z0 or hz0 >= z1:
                nxt.append((x0, z0, x1, z1))
                continue
            ix0, ix1, iz0, iz1 = max(x0, hx0), min(x1, hx1), max(z0, hz0), min(z1, hz1)
            if z0 < iz0: nxt.append((x0, z0, x1, iz0))
            if iz1 < z1: nxt.append((x0, iz1, x1, z1))
            if x0 < ix0: nxt.append((x0, iz0, ix0, iz1))
            if ix1 < x1: nxt.append((ix1, iz0, x1, iz1))
        out = nxt
    return out


def wall_with_doors(put, span, bottom, top, cuts):
    """A wall from span[0] to span[1], bottom to top, less the doorways (u0, u1, b, t)."""
    edges = sorted({span[0], span[1]} | {c for (u0, u1, b, t) in cuts for c in (u0, u1) if span[0] < c < span[1]})
    for u0, u1 in zip(edges, edges[1:]):
        mid = (u0 + u1) / 2
        gaps = sorted((b, t) for (c0, c1, b, t) in cuts if c0 <= mid <= c1)
        y = bottom
        for (b, t) in gaps:
            if b > y:
                put(u0, u1, y, b)
            y = max(y, t)
        if y < top:
            put(u0, u1, y, top)


def torch(a, x, y, z, lamp=True):
    """A torch on a stone stand: its flame (y + 0.6) lights a pea shot through it."""
    a.entity('Torch', t3((x, y + 0.2, z), (0, 0, 0), (0.4, 0.4, 0.4)), mesh('cylinder', '#ffffffff', 'art/stone.png'),
             collider('box', (1, 1, 1)), tags('torch'), script('scripts/torch.bs', flame_h=0.4))
    a.entity('Flame', t3((x, y + 0.6, z)), particles(rate=30, max=40, lifetime=0.5, lifetime_random=0.3, speed=0.8, spread=25,
                                                   area=(0.25, 0.25), gravity=-1.5, size_start=0.22, size_end=0.02,
                                                   color_start='#ffe080ff', color_end='#ff300000', blend='add'))
    if lamp:
        a.point_light(x, y + 1.0, z, '#ffb060ff', 1.3, 9)


def firebowl(a, x, y, z, id):
    """A bowl of oil on a stand (its rim at y + 0.75): a burning pea lights it, for good."""
    a.entity('Bowl Stand', t3((x, y + 0.3, z), (0, 0, 0), (0.35, 0.6, 0.35)), mesh('cylinder', '#ffffffff', 'art/stone.png'),
             collider('box', (1, 1, 1)))
    a.entity('Fire Bowl', t3((x, y + 0.75, z), (0, 0, 0), (0.8, 0.3, 0.8)), mesh('cylinder', '#806040ff', 'art/stone.png'),
             particles(rate=40, max=60, lifetime=0.6, lifetime_random=0.3, speed=1.2, spread=20, area=(0.5, 0.5), gravity=-2.0,
                       size_start=0.35, size_end=0.02, color_start='#ffd070ff', color_end='#ff200000', blend='add'),
             tags('torch', 'shootable', 'focusable'), script('scripts/firebowl.bs', id=id, flame_h=0.2))


def column(a, x, z, low, high, mode='stand', when='', half=1.0, tall=10.0, name='Dough Column'):
    """A square column of dough: its top a platform between low and high (proof.bs)."""
    kw = {'mode': mode, 'low': low, 'high': high, 'tall': tall, 'half': half}
    if when:
        kw['when'] = when
    mat = '#f4e2bcff' if mode == 'stand' else '#c8b08cff'
    a.entity(name, t3((x, low - tall / 2, z), (0, 0, 0), (half * 2, tall, half * 2)), mesh('cube', mat, 'art/dough.png', uv=(1, 4)),
             collider('box', (1, 1, 1)), ('RigidBody3D', [('type', 'kinematic')]), tags('platform'), script('scripts/proof.bs', **kw))


def crate(a, x, y, z):
    """A crust block, 1.6 a side, sitting on y (pushblock.bs: grab it with Action, then push or pull)."""
    a.entity('Crust Block', t3((x, y + 0.8, z), (0, 0, 0), (1.6, 1.6, 1.6)), mesh('cube', '#ffffffff', 'art/crust.png'),
             collider('box', (1, 1, 1)), ('RigidBody3D', [('type', 'kinematic')]), tags('weight', 'interact'), script('scripts/pushblock.bs'))


def curtain(a, x, y, z, w, h, yaw, id):
    """A web of mould across a doorway: only fire burns it."""
    a.entity('Web', t3((x, y + h / 2, z), (0, yaw, 0), (w, h, 0.08)), mesh('cube', '#ffffffff', 'art/web.png', uv=(w / 2, h / 2), cull=False, cast=False),
             collider('box', (1, 1, 1)), tags('focusable', 'shootable'), script('scripts/web.bs', id=id, breaks='fire', radius=max(w, h) * 0.6))


def pool(a, x0, z0, x1, z1, surface=-0.8, bottom=-4.0, sides='nsew'):
    """A pit of runny starter: a fall into it puts Sprig back where he last stood."""
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    a.geo('dough', cx, cz).box((x0 + 0.02, bottom - 0.5, z0 + 0.02), (x1 - 0.02, bottom, z1 - 0.02), uvs=0.35)   # (in from the sides: columns pass it)
    a.geo('starter_pool', cx, cz).quad((x0, surface, z1), (x1, surface, z1), (x1, surface, z0), (x0, surface, z0),
                                       (x0 * 0.3, z1 * 0.3), (x1 * 0.3, z1 * 0.3), (x1 * 0.3, z0 * 0.3), (x0 * 0.3, z0 * 0.3))
    a.entity('Starter Pit', t3((cx, surface - 0.6, cz)), collider('box', (x1 - x0, 1.0, z1 - z0), trigger=True), tags('pit'))
    # its sides, under the floors and walls round it (which stop at -0.5)
    for side, (bx0, bz0, bx1, bz1) in zip('nswe', [(x0 - WALL, z0 - WALL, x1 + WALL, z0), (x0 - WALL, z1, x1 + WALL, z1 + WALL),
                                                    (x0 - WALL, z0, x0, z1), (x1, z0, x1 + WALL, z1)]):
        if side not in sides:
            continue
        a.geo('dough_wall', (bx0 + bx1) / 2, (bz0 + bz1) / 2).box((bx0, bottom - 0.5, bz0), (bx1, -0.5, bz1), uvs=0.3)


def build():
    a = Area('crock', 'The Great Crock', music='music/crock.wav', dungeon='crock', kill_y=-30, sky='#2a1c10ff',
             fog=(14, 40), fog_color='#2a1c10ff', ambient=('#a08868ff', 0.6), sun=('#ffe0b0ff', 0.35), sun_rot=(-70, 20, 0),
             shadows=False, chunk=16)
    a.floors = [('B1', -40, -6), ('1F', -6, 2.5), ('2F', 2.5, 40)]       # (the lair; the halls and pools; the balcony's rooms)

    # ================= the way in =================
    box_room(a, 'dough', 'dough_wall', -1.5, 16.5, 1.5, 24, F1, 3.0, sides='ew')
    a.geo('dough_wall', 0, 24.5).box((-2.0, -0.5, 24.0), (2.0, 3.4, 24.5), uvs=0.3)      # (the far end: dark beyond the zone)
    a.loadzone(0, F1, 23.4, 3.0, 2.6, 0.8, to='sprouthollow', at='crock')
    a.spawn_point('start', 0, F1 + 0.1, 20.5, 0)

    # ================= the Kneading Hall =================
    pad_hole = (6.5, -6.0, 8.5, -4.0)                       # where the warm column comes up through the floor
    box_room(a, 'dough', 'dough_wall', -10, -12, 10, 16, F1, 9.0, holes=[pad_hole],
             doors=[('s', 0, 3.0, F1, F1 + 3.0), ('e', 0, 3.0, F1, F1 + 3.0), ('w', 0, 3.0, F1, F1 + 3.0),
                    ('n', 0, 3.0, F1, F1 + 3.0), ('n', 0, 2.6, F2, F2 + 3.0), ('w', -10, 2.6, F2, F2 + 3.0)])
    # the balcony along the north side (2F), with a rail open where the column comes up
    a.geo('crust', 0, -9).box((-10, F2 - 0.5, -12), (10, F2, -6), uvs=0.4)
    for (rx0, rx1) in [(-10, 6.4), (8.6, 10)]:
        a.geo('crust', (rx0 + rx1) / 2, -6).box((rx0, F2, -6.3), (rx1, F2 + 0.9, -6.0), uvs=0.5)
    # the warm column to the balcony, in a pen with a web across its front
    column(a, 7.5, -5.0, F1 - 0.02, F2, mode='stand', name='Hall Column')
    for (px0, px1) in [(6.0, 6.5), (8.5, 9.0)]:
        a.geo('crust', px0, -5).box((px0, F1, -6.0), (px1, F1 + 1.5, -3.5), uvs=0.5)
    a.geo('crust', 7.5, -6.2).box((6.0, F1, -6.5), (9.0, F2 - 0.5, -6.0), uvs=0.5)     # (behind it, up to the balcony)
    curtain(a, 7.5, F1, -3.6, 2.0, 1.6, 0, 'crock_web_hall')
    torch(a, 7.5, F1, -0.5)
    # the eye in the north wall over the Furnace Room door (under the balcony), and the bars it watches
    eye_y = F1 + 3.24
    a.geo('crust', 0, -12).box((-0.75, eye_y - 0.32, -12.0), (0.75, eye_y + 0.26, -11.9), uvs=0.5)     # (its socket on the wall)
    a.entity('Eye Switch', t3((0, eye_y, -11.82), (0, 0, 0), (0.9, 0.5, 0.3)), mesh('sphere', '#f4ecd8ff', lit=False),
             tags('focusable', 'shootable'), script('scripts/eyeswitch.bs', id='crock_eye'))
    a.entity('Eye Pupil', t3((0, eye_y, -11.66), (0, 0, 0), (0.28, 0.28, 0.1)), mesh('sphere', '#c02020ff', lit=False),
             script('scripts/blocker.bs', until='crock_eye'))
    a.blocker(0, F1, -12.25, (2.98, 2.98, 0.3), 'crock_eye')        # (doors fill their doorways)
    # the locked door to the Boss Key room (2F, north) and the big door west (2F)
    a.entity('Locked Door', t3((0, F2 + 1.49, -12.25), (0, 0, 0), (2.58, 2.98, 0.3)), mesh('cube', '#ffffffff', 'art/planks.png'),
             collider('box'), tags('interact'), script('scripts/lockdoor.bs', id='crock_bk'))
    a.entity('Lock', t3((0, F2 + 1.3, -12.05), (0, 0, 0), (0.5, 0.6, 0.2)), mesh('cube', '#c8a040ff'), tags('lock'))
    a.entity('Boss Door', t3((-10.25, F2 + 1.49, -10), (0, 90, 0), (2.58, 2.98, 0.4)), mesh('cube', '#8a3a2aff', 'art/planks.png'),
             collider('box'), tags('interact'), script('scripts/lockdoor.bs', id='crock_boss_door', boss=True))
    a.entity('Boss Lock', t3((-10.0, F2 + 1.4, -10), (0, 90, 0), (0.8, 0.9, 0.2)), mesh('cube', '#c84040ff'), tags('lock'))
    # things about the hall
    for (x, z) in [(-3.0, 13.5), (3.0, 13.5)]:
        torch(a, x, F1, z)
    for (x, z) in [(-9.0, 14.8), (-9.0, 13.6), (9.0, 14.8), (-9.0, -4.5), (9.2, 4.0)]:
        a.pot(x, F1, z)
    for (x, z) in [(-5.0, 4.0), (4.0, 7.0)]:
        a.enemy('fuzzball', x, F1 + 0.1, z, hp=2)
    a.sign(-1.8, F1, 14.6, 0, 'crock_enter')
    a.point_light(0, 6.5, 2, '#ffd090ff', 1.1, 18)
    a.point_light(0, 6.5, -9, '#ffd090ff', 0.9, 12)

    # ================= the Crate Room (east) =================
    box_room(a, 'dough', 'dough_wall', 10.5, -1.5, 12.5, 1.5, F1, 3.0, sides='ns')
    box_room(a, 'dough', 'dough_wall', 13, -7, 27, 7, F1, 6.0,
             doors=[('w', 0, 3.0, F1, F1 + 3.0), ('e', 3.0, 2.0, F1, F1 + 2.6)])
    box_room(a, 'dough', 'dough_wall', 27.5, 2, 29, 4, F1, 2.6, sides='nse')         # the key's alcove
    crate(a, 18.6, F1, -0.8)
    a.floorswitch(18.6, F1, -5.6, 'crock_sw_crate')
    a.switchdoor(27.2, F1, 3.0, (0.3, 2.58, 1.98), 'crock_sw_crate', material='planks', color='#a08060ff')     # (open only while weighed down)
    a.chest(28.3, F1, 3.0, 90, 'key', 'crock_key1')
    for (x, z) in [(22.0, 3.0), (16.0, 4.5)]:
        a.enemy('fuzzball', x, F1 + 0.1, z, hp=2, group='crate')
    a.chest(24.0, F1, -4.5, 180, 'map_crock', 'crock_map', appear='clear:crate')
    a.sign(14.6, F1, 2.4, 270, 'crock_crates')
    for (x, z) in [(26.0, -6.0), (14.0, -6.0)]:
        a.pot(x, F1, z)
    a.point_light(20, 4.5, 0, '#ffd090ff', 1.1, 12)

    # ================= the Proofing Room (west, locked) =================
    box_room(a, 'dough', 'dough_wall', -12.5, -1.5, -10.5, 1.5, F1, 3.0, sides='ns')
    a.entity('Locked Door', t3((-11.5, F1 + 1.49, 0), (0, 90, 0), (2.98, 2.98, 0.3)), mesh('cube', '#ffffffff', 'art/planks.png'),
             collider('box'), tags('interact'), script('scripts/lockdoor.bs', id='crock_proof'))
    a.entity('Lock', t3((-11.3, F1 + 1.3, 0), (0, 90, 0), (0.5, 0.6, 0.2)), mesh('cube', '#c8a040ff'), tags('lock'))
    box_room(a, None, 'dough_wall', -29, -6, -13, 10, F1, 9.0, doors=[('e', 0, 3.0, F1, F1 + 3.0)])
    a.geo('dough', -15, 2).box((-17.0, F1 - 0.5, -6), (-13, F1, 10), uvs=0.35)              # the floor by the door
    pool(a, -23.0, -6, -17.0, 10, sides='nse')                                              # (the ledge is its west side)
    a.geo('crust', -26, 2).box((-29, -4.5, -6), (-23.0, F2, 10), uvs=0.4)                  # the high ledge
    column(a, -18.0, 2.0, F1 - 0.02, 1.5, half=0.95)
    column(a, -20.0, 2.0, 1.5, 3.0, half=0.95)
    column(a, -22.0, 2.0, 3.0, F2, half=0.95)
    a.chest(-26.0, F2, 2.0, -90, 'shooter', 'crock_shooter', big=True)
    a.enemy('scrub', -27.0, F2, 7.5, yaw=-90, hp=1)
    for (x, z) in [(-15.0, 6.0), (-15.5, -3.5)]:
        a.enemy('fuzzball', x, F1 + 0.1, z, hp=2)
    a.sign(-14.6, F1, -2.4, 90, 'crock_proof')
    for (x, z) in [(-14.0, 9.0), (-28.0, -5.0)]:
        a.pot(x, F1 if x > -20 else F2, z)
    torch(a, -14.0, F1, -5.2)
    a.point_light(-21, 6.5, 2, '#ffd090ff', 1.2, 14)

    # ================= the Furnace Room (north, 1F, behind the eye's bars) =================
    box_room(a, 'dough', 'dough_wall', -1.5, -14.5, 1.5, -12.5, F1, 3.0, sides='ew')
    box_room(a, None, 'dough_wall', -8, -31, 8, -15, F1, 3.4, doors=[('s', 0, 3.0, F1, F1 + 3.0), ('e', -29.5, 2.0, F1, F1 + 2.4)])
    a.geo('dough', 0, -17).box((-8, F1 - 0.5, -19), (8, F1, -15), uvs=0.35)                 # the near floor
    a.geo('dough', 0, -28).box((-8, F1 - 0.5, -31), (8, F1, -25), uvs=0.35)                 # the far floor
    pool(a, -8, -25, 8, -19)
    for z in (-20.0, -22.0):
        column(a, 0, z, -3.98, F1 - 0.02, mode='flag', when='crock_bowl_w')
    column(a, 0, -24.0, -3.98, F1 - 0.02, mode='flag', when='crock_bowl_e')
    for (x, id) in [(-5.5, 'crock_bowl_w'), (5.5, 'crock_bowl_e')]:
        torch(a, x, F1, -17.0, lamp=False)
        firebowl(a, x, F1, -27.0, id)
    a.point_light(0, 2.6, -17, '#ffb060ff', 1.2, 12)
    a.point_light(0, 2.6, -28, '#ff9050ff', 1.0, 11)
    box_room(a, 'dough', 'dough_wall', 8.5, -30.5, 10, -28.5, F1, 2.4, sides='nse')       # the second key's alcove
    curtain(a, 8.05, F1, -29.5, 2.0, 2.4, 90, 'crock_web_key')
    torch(a, 4.0, F1, -29.5, lamp=False)
    a.chest(9.2, F1, -29.5, 90, 'key', 'crock_key2')
    a.chest(-6.5, F1, -29.8, 180, 'compass_crock', 'crock_compass')
    a.enemy('fuzzball', 2.5, F1 + 0.1, -17.5, hp=2)
    a.sign(-2.0, F1, -15.3, 0, 'crock_furnace')

    # ================= the Boss Key room (2F, north, over the furnace) =================
    box_room(a, 'dough', 'dough_wall', -6, -24, 6, -12.5, F2, 4.0, sides='new', doors=[('n', 0, 3.0, F2, F2 + 3.0)])
    box_room(a, 'dough', 'dough_wall', -1.5, -26.5, 1.5, -24.5, F2, 3.0, sides='new')
    crate(a, -2.4, F2, -16.4)
    crate(a, 0.8, F2, -19.6)
    a.floorswitch(-2.4, F2, -21.2, 'crock_sw_a')
    a.floorswitch(4.0, F2, -19.6, 'crock_sw_b')
    a.entity('Two Switches', t3((0, F2, -18)), script('scripts/allflags.bs', a='crock_sw_a', b='crock_sw_b', out='crock_bk_gate'))
    a.switchdoor(0, F2, -24.2, (2.98, 2.98, 0.3), 'crock_bk_gate', material='planks', color='#a08060ff')
    a.chest(0, F2, -25.4, 180, 'bosskey_crock', 'crock_bosskey', big=True)
    a.point_light(0, F2 + 3.0, -18, '#ffd090ff', 1.1, 11)
    a.sign(4.6, F2, -13.2, 0, 'crock_bkroom')

    # ================= past the big door: the shaft down =================
    box_room(a, 'crust', 'dough_wall', -15.5, -11.3, -10.5, -8.7, F2, 3.0, sides='ns')
    shaft = (-20.0, -11.0, -18.0, -9.0)
    box_room(a, 'crust', 'dough_wall', -22, -13, -16, -7, F2, 4.0, holes=[shaft], doors=[('e', -10, 2.6, F2, F2 + 3.0)])
    for (sx0, sz0, sx1, sz1) in [(-20.5, -11.5, -18.0, -11.0), (-18.0, -11.5, -17.5, -9.0), (-20.0, -9.0, -17.5, -8.5), (-20.5, -11.0, -20.0, -8.5)]:
        a.geo('mould', (sx0 + sx1) / 2, (sz0 + sz1) / 2).box((sx0, -5.0, sz0), (sx1, F2 - 0.5, sz1), uvs=0.4)
    a.entity('Shaft Glow', t3((-19, F2 + 0.4, -10)), particles(rate=8, max=20, lifetime=2.0, speed=0.4, spread=30, area=(1.6, 1.6), gravity=-0.3,
                                                             size_start=0.2, size_end=0.0, color_start='#c0ff90a0', color_end='#40802000'))
    a.point_light(-19, F2 + 2.5, -10, '#c0ff90ff', 0.9, 8)

    # ================= Queen Mildewmite's lair =================
    lx, lz = -19.0, -10.0
    ring_wall(a.geo('mould', lx, lz), lx, lz, 10, LAIR - 0.5, -5.0, 28)
    ceiling_disc(a.geo('ceiling', lx, lz), lx, lz, 10, -5.0, 1.45, 24)
    ring_floor(a.geo('mould', lx, lz), lx, lz, 0, 10, LAIR, segs=24, thick=0.5)
    a.entity('Queen', t3((lx, -6.0, lz - 4)), mesh('model', file='models/queen.glb', shadow=False),
             ('Animator', [('clip', q('idle')), ('speed', 1), ('loop', True), ('playing', True), ('blend', 0.15)]),
             collider('capsule', (1, 2.2, 1), 1.3, offset=(0, 1.1, 0)), ('RigidBody3D', [('type', 'kinematic')]),
             tags('enemy', 'focusable', 'boss'), script('scripts/queen.bs', ceiling=-6.0, floor_y=LAIR))
    a.entity('Queen Eye', t3((lx, -5.4, lz - 5)), mesh('sphere', '#f0f0d0ff', lit=False, cast=False))
    a.entity('Heart Pie', t3((lx, LAIR + 0.8, lz + 4), (0, 0, 0), 2.0), mesh('model', '#ff3048ff', file='models/heart.obj', lit=False),
             script('scripts/pickup.bs', kind='heartpie', id='crock_pie', when='crock_boss'))
    a.entity('Blue Light', t3((lx, LAIR + 1.5, lz), (0, 0, 0), (1.6, 3.0, 1.6)), mesh('cylinder', '#80c0ff60', lit=False, cull=False, cast=False),
             particles(rate=20, max=40, lifetime=1.5, speed=1.2, spread=10, area=(1.6, 1.6), size_start=0.15, size_end=0,
                       color_start='#c0e0ffff', color_end='#4080ff00', blend='add'),
             script('scripts/warp.bs', to='sprouthollow', at='grove', sets='crock_done', when='crock_boss'))
    a.point_light(lx, LAIR + 5, lz, '#c0ff90ff', 1.3, 16)

    # (for trying parts on their own)
    a.spawn_point('t_hall2f', 0, F2 + 0.1, -9, 0)
    a.spawn_point('t_crate', 15, F1 + 0.1, 0, 270)
    a.spawn_point('t_proof', -15, F1 + 0.1, 2, 90)
    a.spawn_point('t_furnace', 0, F1 + 0.1, -16.5, 0)
    a.spawn_point('t_bk', 0, F2 + 0.1, -14, 0)
    a.spawn_point('t_shaft', -14, F2 + 0.1, -10, 90)
    a.spawn_point('t_lair', lx, LAIR + 0.1, lz + 6, 0)
    a.save()
