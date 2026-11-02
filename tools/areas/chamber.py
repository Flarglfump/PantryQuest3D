"""The Chamber of Keepers: where a Keeper of Flavour wakes, after a temple's master falls.

A round hall of light with six pedestals. Fennel, Keeper of Bitter, waits on hers.
"""
import math

from areakit import Area, ring_floor, ring_wall, ceiling_disc
from kit import t3, mesh, collider, tags, script, particles


def build():
    a = Area('chamber', 'Chamber of Keepers', music='music/title.wav', kill_y=-20, sky='#f0f0e0ff', fog=(30, 70), fog_color='#f0e8d0ff',
             ambient=('#fff0d0ff', 0.8), sun=('#ffffffff', 0.5), sun_rot=(-80, 0, 0), chunk=16)
    ring_wall(a.geo('stone', 0, 0), 0, 0, 10, -0.5, 8, 28)
    ring_floor(a.geo('stone', 0, 0), 0, 0, 0, 10, 0, segs=24, thick=0.5)
    colors = ['#f0c040ff', '#60c050ff', '#ff6040ff', '#4090ffff', '#a060c0ff', '#ffa0c0ff']
    for k in range(6):
        ang = -90 + k * 60
        x, z = math.cos(math.radians(ang)) * 6.5, math.sin(math.radians(ang)) * 6.5
        a.geo('stone', x, z).cylinder((x, 0, z), 1.0, 0.6, 10, uvs=0.5)
        a.entity('Glow', t3((x, 0.7, z)), particles(rate=6, max=20, lifetime=1.5, speed=0.5, spread=10, area=(1.4, 1.4), gravity=-0.3,
                                                    size_start=0.15, size_end=0, color_start=colors[k], color_end='#ffffff00', blend='add'))
    a.npc('fennel_keeper', 0, 0.6, -6.5, 0, model='fennel', reach=3.0, needs='thymetemple_done', until='left_bitter')
    a.npc('biscotti_keeper', 0, 0.6, -6.5, 0, model='biscotti', reach=3.4, needs='forge_done', until='left_spice')
    a.npc('fizzy_keeper', 0, 0.6, -6.5, 0, model='fizzy', reach=3.0, needs='brinetemple_done', until='left_salt')
    a.npc('kimchi_keeper', 0, 0.6, -6.5, 0, model='kimchi', reach=3.0, needs='crypt_done', until='left_sour')
    a.npc('caramel_keeper', 0, 0.6, -6.5, 0, model='caramel', reach=3.0, needs='idol_done', until='left_sweet')
    a.spawn_point('start', 0, 0.1, 2, 0)
    for to, at, keeper in [('thicket', 'glade', 'bitter'), ('fondue', 'forge', 'spice'), ('lake', 'island', 'salt'), ('peppermill', 'graveyard', 'sour'), ('temple', 'start', 'sweet')]:
        a.entity('Blue Light', t3((0, 1.5, 5.5), (0, 0, 0), (1.6, 3.0, 1.6)), mesh('cylinder', '#80c0ff60', lit=False, cull=False, cast=False),
                 particles(rate=20, max=40, lifetime=1.5, speed=1.2, spread=10, area=(1.6, 1.6), size_start=0.15, size_end=0,
                           color_start='#c0e0ffff', color_end='#4080ff00', blend='add'),
                 script('scripts/warp.bs', to=to, at=at, when='keeper_' + keeper, until='left_' + keeper, sets='left_' + keeper))
    a.save()
