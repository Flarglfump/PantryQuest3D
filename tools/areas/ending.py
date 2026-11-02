"""The ending: the castle garden, seven years before, in the morning light."""
import math

from areakit import Area
from kit import t3, mesh, collider, tags, script, particles, q


def build():
    a = Area('ending', 'Castle Garden', music='music/title.wav', kill_y=-20, sky='#b0dcf0ff', fog=(50, 110), ambient=('#a0b0c8ff', 0.65), chunk=20)
    a.geo('grass', 0, 0).ground(-20, -20, 20, 20, 8, 8, lambda x, z: 0.0, uvs=0.3)
    for k in range(12):
        ang = k * 30
        x, z = math.cos(math.radians(ang)) * 14, math.sin(math.radians(ang)) * 14
        a.tree(x, 0, z, 1.2)
    a.spawn_point('start', 0, 0.1, 4, 0)
    a.entity('Saffron', t3((0, 0, -2), (0, 180, 0)), mesh('model', file='models/saffron.glb'),
             ('Animator', [('clip', q('idle')), ('speed', 1), ('loop', True), ('playing', True), ('blend', 0.2)]))
    a.entity('Ending', t3((0, 0, 0)), script('scripts/ending.bs'))
    a.save()
