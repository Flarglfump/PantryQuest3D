"""The bottom of the well: a dark, damp cave under Peppermill (the Risen era).

A ladder of light back up; a round cave; a wall that isn't there (an illusion) to a
second cave where Stalebies guard the Onion Lens.
"""
import math

from areakit import Area, ring_floor, ring_wall, ceiling_disc, tunnel
from kit import t3, mesh, collider, tags, script, particles


def build():
    a = Area('well', 'Bottom of the Well', music='music/caverns.wav', kill_y=-20, sky='#100c08ff', fog=(13, 42), fog_color='#181208ff',
             ambient=('#a09080ff', 0.55), sun=('#c0b090ff', 0.3), sun_rot=(-80, 0, 0), chunk=16)
    ring_wall(a.geo('rock', 0, 0), 0, 0, 7, -1, 5, 24, [(270, 1.4, 0, 3.0)])
    ceiling_disc(a.geo('rock', 0, 0), 0, 0, 7, 5, 0, 18)
    ring_floor(a.geo('dirt', 0, 0), 0, 0, 0, 7, 0, segs=20, thick=0.5)
    a.entity('Light Shaft', t3((0, 3, 5.2), (0, 0, 0), (2.2, 6, 2.2)), mesh('cylinder', '#fff0c018', lit=False, cull=False, cast=False))
    a.entity('Up', t3((0, 0.5, 5.5)), collider('box', (1.6, 1.0, 1.6), trigger=True), tags('loadzone'), script('scripts/loadzone.bs', to='peppermill', at='well'))
    a.spawn_point('start', 0, 0.1, 3.2, 0)
    a.sign(2.5, 0, 2.5, 0, 'lens_hint')
    tunnel(a.geo('dirt', 0, -9), a.geo('rock', 0, -9), 0, -6.6, 0, -11.6, 0)
    a.entity('False Wall', t3((0, 1.5, -7.6), (0, 0, 0), (2.6, 3.0, 0.4)), mesh('cube', '#8a7a6aff', 'art/stone.png'), script('scripts/secret.bs', kind='fake'))
    ring_wall(a.geo('rock', 0, -18), 0, -18, 7, -1, 5, 24, [(90, 1.4, 0, 3.0)])
    ceiling_disc(a.geo('rock', 0, -18), 0, -18, 7, 5, 0, 18)
    ring_floor(a.geo('dirt', 0, -18), 0, -18, 0, 7, 0, segs=20, thick=0.5)
    for x, z in [(-3, -16), (3, -17), (0, -21)]:
        a.enemy('stalebie', x, 0, z, hp=4, damage=4, always=True, group='well_s')
    a.chest(0, 0, -23, 0 + 180, 'lens', 'well_lens', appear='clear:well_s', big=True)
    a.point_light(0, 3, 0, '#ffe0a0ff', 1.2, 10)
    a.point_light(0, 3, -18, '#c0a0ffff', 1.0, 10)
    a.save()
