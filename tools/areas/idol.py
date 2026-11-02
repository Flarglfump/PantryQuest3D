"""The Salt Idol's sands: the great statue of the twin witches, at the edge of the desert.

Built for both eras (the Requiem of Sugar brings Sprig here either way). The way back east
crosses the Haunted Flats; the temple door is at the statue's feet; Cinder waits nearby.
"""
import math

from areakit import Area
from kit import drawn, t3, mesh, collider, tags, script, particles


def height(x, z):
    h = 0.4 * math.sin(x * 0.2) * math.cos(z * 0.17)
    r = math.hypot(x, z)
    return h + 10 * max(0.0, min(1.0, (r - 30) / 4))


def build():
    global height
    a = Area('idol', 'Salt Idol', music='music/castle.wav', kill_y=-20, sky='#f0c890ff', fog=(60, 130), fog_color='#e8c090ff',
             ambient=('#c0a080ff', 0.6), sun=('#fff0d0ff', 1.0), chunk=22)
    for cz in range(-36, 36, 12):
        for cx in range(-36, 36, 12):
            a.geo('sand', cx + 6, cz + 6).ground(cx, cz, cx + 12, cz + 12, 4, 4, height, uvs=0.25)
    height = drawn(height)        # (from here on, things are set on the ground as drawn: none float or sink)
    # the Idol: a seated giantess of rock salt
    a.geo('stone', 0, -22).box((-6, -0.5, -28), (6, 8, -20), uvs=0.2)
    a.geo('stone', 0, -24).box((-5, 8, -27), (5, 20, -21), uvs=0.2)
    a.geo('stone', 0, -24).cylinder((0, 20, -24), 3.6, 5.5, 10, uvs=0.3)
    a.geo('stone', 0, -24).cone((0, 25.5, -24), 4.2, 4.0, 10)
    for sx in (-1, 1):
        a.geo('stone', sx * 7.5, -20).box((sx * 7.5 - 1.5, -0.5, -22), (sx * 7.5 + 1.5, 9, -14), uvs=0.25)
    a.entity('Idol Door', t3((0, 1.8, -19.95), (0, 0, 0), (3.0, 3.6, 0.1)), mesh('cube', '#100804ff', lit=False))
    a.loadzone(0, 0, -19.6, 3, 3, 0.6, to='idoltemple', at='start')
    a.spawn_point('temple', 0, 0.1, -16.5, 180)
    a.spawn_point('requiem', 0, 0.1, -8, 180)
    a.sign(3.5, height(3.5, -15), -15, 180, 'sign_idol')
    a.npc('cinder', -4, height(-4, -12), -12, 120, reach=2.4, needs='risen_once')
    # the way back east, across the Flats
    a.loadzone(34, height(30, 0), 0, 1.5, 4, 8, to='flats', at='start')
    a.spawn_point('start', 26, height(26, 0) + 0.1, 0, 90)
    for k in range(6):
        x, z = math.cos(k) * 18, math.sin(k * 1.3) * 16
        a.entity('Rock', t3((x, height(x, z) + 0.4, z), (0, k * 50, 0), (2.0, 1.4, 2.0)), mesh('sphere', '#e8c8a0ff', 'art/stone.png'),
                 collider('sphere', radius=0.5))
    a.area_map()          # (the MAP page: the ground from above, the ways out named)
    a.save()
