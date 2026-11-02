"""The Proofing Vault: the warm stone room where Sprig slept seven years, rising.

A round, dim, warm room. Sprig wakes in the middle; Old Mozz, Keeper of Umami, waits by
the hearth. Once he has spoken, a blue light takes Sprig back to the temple.
"""
from areakit import Area, ring_floor, ring_wall, ceiling_disc
from kit import t3, mesh, collider, tags, script, particles


def build():
    a = Area('vault', 'The Proofing Vault', music='music/title.wav', kill_y=-20, sky='#140a04ff', fog=(16, 48), fog_color='#2a1608ff',
             ambient=('#e0b080ff', 0.6), sun=('#ffd0a0ff', 0.4), sun_rot=(-80, 0, 0), chunk=16)
    ring_wall(a.geo('crust', 0, 0), 0, 0, 9, -0.5, 7, 28)
    ceiling_disc(a.geo('crust', 0, 0), 0, 0, 9, 7, 0, 20)
    ring_floor(a.geo('dough', 0, 0), 0, 0, 0, 9, 0, segs=24, thick=0.5)
    a.geo('stone', 0, 0).cylinder((0, 0, 0), 2.0, 0.4, 16, uvs=0.5)
    a.spawn_point('start', 0, 0.5, 0, 0)
    a.npc('mozz', 0, 0, -4.5, 0, reach=2.6)
    a.entity('Hearth', t3((0, 0.3, -7.5)), particles(rate=24, max=40, lifetime=0.8, speed=0.8, spread=20, area=(1.4, 0.4), gravity=-1.4,
                                                    size_start=0.35, size_end=0.02, color_start='#ffd070ff', color_end='#ff300000', blend='add'))
    a.point_light(0, 2, -7, '#ffb060ff', 1.6, 12)
    a.entity('Blue Light', t3((0, 1.5, 4.5), (0, 0, 0), (1.6, 3.0, 1.6)), mesh('cylinder', '#80c0ff60', lit=False, cull=False, cast=False),
             particles(rate=20, max=40, lifetime=1.5, speed=1.2, spread=10, area=(1.6, 1.6), size_start=0.15, size_end=0,
                       color_start='#c0e0ffff', color_end='#4080ff00', blend='add'),
             script('scripts/warp.bs', to='temple', at='block', when='met_mozz'))
    a.save()
