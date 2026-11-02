"""The Haunted Flats: a sandstorm over endless dunes between the Raider Fort and the Salt Idol.

A path of posts winds west; stray from it and the sand turns you round (lost.bs). Ghostly
lanterns along the way show only through the Onion Lens.
"""
import math
import random

from areakit import Area
from kit import drawn, t3, mesh, collider, tags, script, particles

PATH = [(36, 0), (20, 10), (4, -6), (-12, 8), (-26, -6), (-40, 4)]


def height(x, z):
    return 1.2 * math.sin(x * 0.11) * math.cos(z * 0.13) + 0.6 * math.sin(x * 0.27 + z * 0.19)


def build():
    global height
    random.seed(73)
    a = Area('flats', 'Haunted Flats', music='music/castle.wav', kill_y=-20, sky='#d8b888ff', fog=(12, 40), fog_color='#d8b888ff',
             ambient=('#c0a080ff', 0.65), sun=('#ffe8c0ff', 0.7), chunk=22)
    for cz in range(-33, 33, 11):
        for cx in range(-55, 55, 11):
            a.geo('sand', cx + 5.5, cz + 5.5).ground(cx, cz, cx + 11, cz + 11, 4, 4, height, uvs=0.25)
    height = drawn(height)        # (from here on, things are set on the ground as drawn: none float or sink)
    a.entity('Sandstorm', t3((0, 3, 0)), particles(rate=60, max=200, lifetime=2.5, speed=8, spread=10, angle=0, area=(90, 50), gravity=0,
                                                 size_start=0.12, size_end=0.08, color_start='#f0d8a0a0', color_end='#f0d8a000'))
    a.spawn_point('start', 36, height(36, 0) + 0.1, 0, 90)
    a.loadzone(40, height(40, 0), 0, 1.5, 4, 8, to='fort', at='flats')
    a.sign(34, height(34, 2.5), 2.5, 90, 'sign_flats')
    pts = []
    for (x0, z0), (x1, z1) in zip(PATH, PATH[1:]):
        n = max(1, int(math.hypot(x1 - x0, z1 - z0) / 7))
        for i in range(n):
            x, z = x0 + (x1 - x0) * i / n, z0 + (z1 - z0) * i / n
            a.geo('bark', x, z).cylinder((x + 1.8, height(x + 1.8, z) - 0.2, z), 0.12, 2.2, 6)
            a.entity('Post Flag', t3((x + 1.8, height(x + 1.8, z) + 2.0, z + 0.3), (0, 0, 0), (0.05, 0.4, 0.6)), mesh('cube', '#c03030ff'))
            a.entity('Ghost Lantern', t3((x, height(x, z) + 1.4, z), (0, 0, 0), 0.3), mesh('sphere', '#c080ffff', lit=False, cast=False),
                     script('scripts/secret.bs', kind='invisible'))
    a.entity('Lost', t3((0, 0, 0)), script('scripts/lost.bs', path=[(x, 0, z) for x, z in PATH], width=7))
    a.loadzone(-44, height(-44, 4), 4, 1.5, 4, 8, to='idol', at='start')
    a.save()
