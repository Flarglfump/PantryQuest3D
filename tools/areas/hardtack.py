"""Hardtack City: the round hall of the Hardtack Clan, inside Mount Fondue.

A great round cave lit by lava-cheese lamps. A ramp winds up the wall from the door (south)
to a ledge on the north side, where Big Biscotti's door (it answers only a royal song) leads
to his room.
"""
import math

from areakit import Area, ring_floor, ring_wall, ceiling_disc, tunnel
from kit import t3, mesh, collider, tags, script, particles, q

R = 14.0
UP = 4.5


def polar(r, a):
    return math.cos(math.radians(a)) * r, math.sin(math.radians(a)) * r


def ramp(o, a0, a1, y0, y1, r0, r1, segs=16):
    """A ramp winding along the wall from angle a0 to a1, rising from y0 to y1."""
    for i in range(segs):
        aa, ab = a0 + (a1 - a0) * i / segs, a0 + (a1 - a0) * (i + 1) / segs
        ya, yb = y0 + (y1 - y0) * i / segs, y0 + (y1 - y0) * (i + 1) / segs
        P = lambda r, a, y: (math.cos(math.radians(a)) * r, y, math.sin(math.radians(a)) * r)
        top = [P(r0, aa, ya), P(r0, ab, yb), P(r1, ab, yb), P(r1, aa, ya)]
        if ab > aa:
            o.quad(*top)
        else:
            o.quad(*reversed(top))
        inner = [P(r0, aa, -0.3), P(r0, aa, ya), P(r0, ab, yb), P(r0, ab, -0.3)]
        if ab > aa:
            o.quad(inner[3], inner[2], inner[1], inner[0])
        else:
            o.quad(*inner)


def build(era='fresh'):
    risen = era == 'risen'
    a = Area('hardtack', 'Hardtack City', music='music/fondue.wav', kill_y=-20, sky='#2a1408ff', fog=(22, 64), fog_color='#2a1408ff',
             ambient=('#c09070ff', 0.55), sun=('#ffc080ff', 0.4), sun_rot=(-80, 0, 0), chunk=16, variant=era if risen else '')
    holes = [(90, 1.4, 0, 3.0), (270, 1.4, UP, UP + 3.0)]
    for k in range(4):
        ring_wall(a.geo('rock', *polar(9, 45 + 90 * k)), 0, 0, R, -0.5, 12, 32, holes)
    ceiling_disc(a.geo('rock', 0, 0), 0, 0, R, 12, 0, 24)
    ring_floor(a.geo('rock', 0, 0), 0, 0, 0, R, 0, segs=28, thick=0.5)
    # a lava-cheese lamp in the middle
    a.geo('stone', 0, 0).cylinder((0, -0.3, 0), 2.2, 1.0, 12, top=False, uvs=0.5)
    a.geo('lava', 0, 0).cylinder((0, 0.6, 0), 2.0, 0.01, 12, top=True)
    a.entity('Lamp Rim', t3((0, 0.5, 0)), collider('capsule', (1, 1, 1), 2.2), tags('seethrough'))
    a.entity('Lamp Glow', t3((0, 0.8, 0)), particles(rate=10, max=30, lifetime=1.4, speed=0.6, spread=30, area=(3, 3), gravity=-0.5,
                                                     size_start=0.25, size_end=0, color_start='#ffd070ff', color_end='#ff400000', blend='add'))
    a.point_light(0, 3, 0, '#ffb060ff', 1.6, 18)
    # the ramp: from beside the door (south-east) round the east wall to the north ledge
    ramp(a.geo('rock', 9, 0), 60, -60, 0, UP, R - 3.6, R, 24)
    ring_floor(a.geo('rock', 0, -9), 0, 0, R - 3.6, R, UP, 180, 300, segs=12, thick=UP + 0.3)
    # the door out
    tunnel(a.geo('rock', 0, 16), a.geo('rock', 0, 16), 0, R - 0.5, 0, R + 3, 0)
    a.loadzone(0, 0, R + 2.6, 2.6, 3, 0.8, to='fondue', at='city')
    a.spawn_point('start', 0, 0.1, R - 2, 0)
    # Big Biscotti's door (north ledge) and his room
    tunnel(a.geo('rock', 0, -16), a.geo('rock', 0, -16), 0, -R + 0.5, 0, -R - 3.5, UP)
    a.entity('Biscotti Door', t3((0, UP + 1.5, -R - 0.6), (0, 0, 0), (2.6, 3.0, 0.3)), mesh('cube', '#8a6a3aff', 'art/planks.png'),
             collider('box'), tags('interact', 'focusable'), script('scripts/songdoor.bs', song='lullaby', id='door:biscotti', say='biscotti_door'))
    a.entity('Crest', t3((0, UP + 2.2, -R - 0.42), (0, 0, 0), (0.7, 0.7, 0.05)), mesh('cylinder', '#e0b040ff'))
    bz = -R - 9
    ring_wall(a.geo('rock', 0, bz), 0, bz, 6, UP - 0.5, UP + 6, 20, [(90, 1.4, UP, UP + 3.0)])
    ceiling_disc(a.geo('rock', 0, bz), 0, bz, 6, UP + 6, 0, 16)
    ring_floor(a.geo('rock', 0, bz), 0, bz, 0, 6, UP, segs=16, thick=0.5)
    if not risen:
        a.npc('biscotti', 0, UP, bz - 2, 0, until='hardcaves_done', reach=3.2)
    a.point_light(0, UP + 3, bz, '#ffb060ff', 1.2, 10)
    # the Hardtack about town
    if risen:          # the Duke took them all to the forge: only Biscotti's boy is left, hiding
        a.npc('little_biscotti', 5, 0, -6, 210, model='hardtack_kid', reach=2.4)
    else:
        a.npc('hardtack', -6, 0, 4, 120)
        a.npc('hardtack', 5, 0, -6, 210, model='hardtack_kid')
    for ang in (150, 200, 230):
        x, z = polar(11, ang)
        a.bombflower(x, 0, z)
    for ang in (110, 125):
        x, z = polar(12, ang)
        a.pot(x, 0, z)
    a.area_map()          # (the MAP page: the ground from above, the ways out named)
    a.save()


def build_risen():
    build('risen')
