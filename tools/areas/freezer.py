"""The Freezer Caves: an ice cave behind the frozen Fizzwater Fountain (the Risen era).

North is -z. The way in is at the south. A blue fire burns in the first cave (catch it in
a jar); red ice seals the way north (blue fire melts it); in the last cave, the Cast-Iron
Boots. Cinder waits there afterwards.
"""
import math

from areakit import Area, ring_floor, ring_wall, ceiling_disc, tunnel
from kit import t3, mesh, collider, tags, script, particles


def room(a, cx, cz, r, holes, ceil=7.0):
    for k in range(3):
        ang = 120 * k + 60
        ring_wall(a.geo('ice', cx + math.cos(math.radians(ang)) * r * 0.6, cz + math.sin(math.radians(ang)) * r * 0.6), cx, cz, r, -1, ceil,
                  24, [(h[0], h[1], 0, 3.0) for h in holes])
    ceiling_disc(a.geo('ice', cx, cz), cx, cz, r, ceil, 0, 18)
    ring_floor(a.geo('ice', cx, cz), cx, cz, 0, r, 0, segs=20, thick=0.5)


def build():
    a = Area('freezer', 'Freezer Caves', music='music/caverns.wav', kill_y=-20, sky='#c0e0f0ff', fog=(12, 34), fog_color='#a0c8e0ff',
             ambient=('#c0e0ffff', 0.75), sun=('#e0f4ffff', 0.4), sun_rot=(-80, 0, 0), chunk=16)
    room(a, 0, 0, 9, [(90, 1.4), (270, 1.4)])
    tunnel(a.geo('ice', 0, 11), a.geo('ice', 0, 11), 0, 8.6, 0, 13, 0)
    a.loadzone(0, 0, 12.6, 2.6, 3, 0.8, to='fountain', at='freezer')
    a.spawn_point('start', 0, 0.1, 6.5, 0)
    a.bluefire(-4.5, 0, -2)
    a.sign(2, 0, 4, 0, 'freezer_sign')
    for x, z in [(4, -3), (-3, 4)]:
        a.enemy('fuzzball', x, 0.1, z, hp=3, damage=4)
    for k in range(10):
        ang = k * 36
        x, z = math.cos(math.radians(ang)) * 7, math.sin(math.radians(ang)) * 7
        a.entity('Icicle', t3((x, 6.2, z), (180, 0, 0), (0.5, 1.6, 0.5)), mesh('cone', '#e0f4ffff', cast=False))
    a.point_light(0, 4, 0, '#c0e0ffff', 1.2, 12)
    # north: the red ice
    tunnel(a.geo('ice', 0, -12), a.geo('ice', 0, -12), 0, -8.6, 0, -15.4, 0)
    a.redice(0, 0, -11.5, (2.6, 3.0, 1.0), 'ice_cave')
    # the last cave: the Cast-Iron Boots
    room(a, 0, -23, 8, [(90, 1.4)])
    a.chest(0, 0, -27, 180, 'boots', 'frz_boots', big=True)
    for x, z in [(-4, -21), (4, -22)]:
        a.enemy('crustling', x, 0.1, z, hp=4, damage=4)
    a.npc('cinder', -3.5, 0, -24.5, 160, needs='chest:frz_boots', reach=2.4)
    a.point_light(0, 4, -23, '#c0e0ffff', 1.2, 12)
    a.save()
