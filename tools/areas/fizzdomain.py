"""The Fizzling Domain: the Fizzlings' cave behind Fizzwater Falls.

A tall round cave of water-worn blue stone round a deep pool (the diving game). The way
in from the falls is at the south; King Carbonarius sits on his dais at the north end,
filling the passage to Fizzwater Fountain behind him.
"""
import math

from areakit import Area, ring_floor, ring_wall, ceiling_disc, tunnel
from kit import t3, mesh, collider, tags, script, particles

R = 18.0
POOL = 8.0
SURF = -0.4
BED = -4.4


def polar(r, a):
    return math.cos(math.radians(a)) * r, math.sin(math.radians(a)) * r


def build():
    a = Area('fizzdomain', 'Fizzling Domain', music='music/fizz.wav', kill_y=-20, sky='#0c2030ff', fog=(18, 46), fog_color='#183040ff',
             ambient=('#a0c8e8ff', 0.7), sun=('#d0f0ffff', 0.45), sun_rot=(-80, 0, 0), chunk=18)
    holes = [(90, 1.6, 0, 3.2), (270, 1.6, 2.0, 5.2)]
    for k in range(4):
        ring_wall(a.geo('fizzrock', *polar(12, 45 + 90 * k)), 0, 0, R, BED, 14, 32, holes)
    ceiling_disc(a.geo('fizzrock', 0, 0), 0, 0, R, 14, 4, 24)
    a.entity('Skylight', t3((0, 13, 0)), particles(rate=6, max=30, lifetime=5, speed=0.6, spread=10, area=(6, 6), gravity=0.4,
                                                 size_start=0.2, size_end=0.0, color_start='#e0f8ffc0', color_end='#80c0ff00', blend='add'))
    ring_floor(a.geo('fizzrock', 0, 9), 0, 0, POOL, R, 0, segs=28, thick=0.6)
    a.geo('fizzrock', 0, 0).cylinder((0, BED - 0.5, 0), POOL + 0.2, 0.5, 20, top=True, uvs=0.3)
    a.geo('fizzrock', 0, 0).cylinder((0, BED, 0), POOL, -BED, 20, top=False, inside=True, uvs=0.3)
    a.water(-POOL, -POOL, POOL, POOL, SURF, depth=5, round_=True)
    a.entity('Bubbles', t3((0, BED + 0.2, 0)), particles(rate=14, max=60, lifetime=2.5, speed=1.6, spread=8, area=(6, 6), gravity=-0.6,
                                                       size_start=0.12, size_end=0.18, color_start='#ffffffc0', color_end='#ffffff00'))
    a.point_light(0, 6, 0, '#a0e0ffff', 1.6, 24)
    # the way in from the falls (south)
    tunnel(a.geo('fizzrock', 0, R + 2), a.geo('fizzrock', 0, R + 2), 0, R - 0.5, 0, R + 4, 0)
    a.loadzone(0, 0, R + 3.6, 3, 3, 0.8, to='gorge', at='falls')
    a.spawn_point('start', 0, 0.1, R - 2.5, 0)
    a.spawn_point('fountain', 0, 2.1, -R + 6, 180)
    # the diving game
    a.npc('diver', 7.0, 0, 6.0, 135, model='fizzling', reach=2.4)
    a.entity('Dive Game', t3((0, BED + 0.05, 0)), script('scripts/divegame.bs'))
    # King Carbonarius on his dais (north), in front of the way to the fountain
    a.geo('fizzrock', 0, -R + 4).box((-6, 0, -R + 0.5), (6, 2.0, -R + 7.5), uvs=0.3)
    z0, z1 = -R + 7.5, -R + 12.0             # a ramp up to the dais
    o = a.geo('fizzrock', 0, z0)
    o.quad((-2, 2.0, z0), (-2, 0.0, z1), (2, 0.0, z1), (2, 2.0, z0), (0, 0), (0, 1.5), (1.3, 1.5), (1.3, 0))
    o.tri((-2, 2.0, z0), (-2, 0.0, z0), (-2, 0.0, z1), (0, 0), (0, 1), (1, 1))
    o.tri((2, 2.0, z0), (2, 0.0, z1), (2, 0.0, z0), (0, 0), (1, 1), (0, 1))
    tunnel(a.geo('fizzrock', 0, -R - 2), a.geo('fizzrock', 0, -R - 2), 0, -R + 0.5, 0, -R - 4, 2.0)
    a.loadzone(0, 2.0, -R - 3.6, 3, 3, 0.8, to='fountain', at='start')
    a.blocker(0, 2.0, -R + 1.2, (3.4, 3.2, 0.4), 'carb_moved', material='planks', color='#2a4050ff')
    a.npc('carbonarius', 0, 2.0, -R + 2.6, 0, until='carb_moved', reach=4.2)
    a.npc('carbonarius', -3.8, 2.0, -R + 3.4, 30, needs='carb_moved', reach=4.2)
    # Fizzlings about the domain
    a.npc('fizzling', -9, 0, 8, -150)
    a.npc('fizzling', 11, 0, -6, 60, reach=2.0)
    a.npc('fizzling2', -12, 0, -4, -100, model='fizzling')
    for ang in (200, 220, 330):
        x, z = polar(16, ang)
        a.pot(x, 0, z)
    a.save()
