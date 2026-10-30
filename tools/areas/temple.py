"""The Temple of the First Hearth: the old stone hall on the east side of Larder Town.

The door from town is at the south. The Altar of Embers stands in the middle of the hall,
with a pedestal for each Ember; the Door of Seasons fills the north wall (it opens to the
Song of Rising, with all three Embers); behind it, in the Pantry of Ages, the Cleaver of
Dawn waits in its butcher's block. The same hall serves both eras (cleaver.bs).
"""
from areakit import Area, box_wall
from kit import t3, mesh, collider, tags, script, particles


def build():
    a = Area('temple', 'Temple of the First Hearth', music='', kill_y=-20, sky='#100c08ff', fog=(16, 40), fog_color='#1a140cff',
             ambient=('#c0a880ff', 0.6), sun=('#ffe0a0ff', 0.5), sun_rot=(-75, 20, 0), chunk=16)
    W, N, S, H = 7.0, -16.0, 14.0, 9.0
    a.geo('stone', 0, 0).box((-W, -0.5, N), (W, 0.0, S), uvs=0.3)
    for x0, z0, x1, z1 in [(-W, N, -W, S), (W, N, W, S), (-W, N, W, N), (-W, S, -1.6, S), (1.6, S, W, S)]:
        box_wall(a, 'stone', x0, z0, x1, z1, -0.5, H, thick=0.8, uvs=0.25)
    a.geo('stone', 0, S).box((-1.6, 3.2, S - 0.4), (1.6, H, S + 0.4), uvs=0.25)
    a.geo('planks', 0, 0).box((-W, H, N), (W, H + 0.4, S), uvs=0.25, sides=('ny',))
    for z in (-4, 2, 8):
        for xx in (-5.2, 5.2):
            a.geo('stone', xx, z).cylinder((xx, 0, z), 0.5, H, 8, uvs=0.4)
    # light from high windows
    for z in (-4, 4):
        a.entity('Light Beam', t3((0, H / 2, z), (25, 0, 0), (2.4, H, 0.6)), mesh('cube', '#ffe8a018', lit=False, cull=False, cast=False))
    a.entity('Motes', t3((0, 3, 0)), particles(rate=4, max=30, lifetime=5, speed=0.2, spread=180, area=(10, 20), gravity=-0.05,
                                             size_start=0.06, size_end=0, color_start='#fff0c0c0', color_end='#ffe08000', blend='add'))
    # the way out (south)
    a.loadzone(0, 0, S + 0.6, 3, 3, 0.8, to='town', at='temple')
    a.spawn_point('start', 0, 0.1, S - 2.5, 0)
    # the Altar of Embers
    a.geo('stone', 0, 0).box((-3, 0, -1.2), (3, 0.6, 1.2), uvs=0.4)
    a.entity('Altar', t3((0, 0.6, 1.25)), tags('interact', 'focusable'), script('scripts/sign.bs', say='altar', prompt='Read', reach=2.4))
    for k, (item, color) in enumerate([('ember_courage', '#60ff80ff'), ('ember_power', '#ff6040ff'), ('ember_wisdom', '#60a0ffff')]):
        x = -2 + k * 2
        a.geo('stone', x, 0).cylinder((x, 0.6, 0), 0.35, 0.6, 8, uvs=0.5)
        a.entity('Ember Flame', t3((x, 1.3, 0)), particles(rate=16, max=30, lifetime=0.7, speed=0.6, spread=20, area=(0.2, 0.2), gravity=-1,
                                                          size_start=0.25, size_end=0, color_start=color, color_end='#ffffff00', blend='add'),
                 script('scripts/pedestal.bs', item=item))
    a.point_light(0, 4, 0, '#ffd090ff', 1.2, 14)
    # the Door of Seasons
    a.geo('stone', 0, N + 6).box((-W, 0, N + 5.6), (-2.4, H, N + 6.4), uvs=0.25)
    a.geo('stone', 0, N + 6).box((2.4, 0, N + 5.6), (W, H, N + 6.4), uvs=0.25)
    a.geo('stone', 0, N + 6).box((-2.4, 5, N + 5.6), (2.4, H, N + 6.4), uvs=0.25)
    a.entity('Door of Seasons', t3((0, 2.5, N + 6), (0, 0, 0), (4.8, 5.0, 0.5)), mesh('cube', '#d8b860ff', 'art/stone.png'), collider('box'),
             tags('interact', 'focusable'), script('scripts/songdoor.bs', song='rising', id='door:seasons', say='seasons_door', need='embers', reach=3.0))
    # the Pantry of Ages and the Cleaver of Dawn
    bz = N + 2.6
    a.entity('Block', t3((0, 0, bz)), mesh('model', '#a07850ff', 'art/bark.png', file='models/block.obj'), collider('box', (1.4, 1.0, 1.4), offset=(0, 0.5, 0)),
             tags('interact', 'focusable'), script('scripts/cleaver.bs'))
    a.entity('Block Cleaver', t3((0, 1.8, bz), (-90, 0, 0), 1.4), mesh('model', '#f0f4ffff', file='models/cleaver.obj', lit=False))
    a.entity('Cleaver Glow', t3((0, 1.6, bz)), particles(rate=10, max=30, lifetime=1.2, speed=0.4, spread=180, area=(0.6, 0.6), gravity=-0.3,
                                                        size_start=0.12, size_end=0, color_start='#ffffffff', color_end='#a0c0ff00', blend='add'))
    a.point_light(0, 4, bz, '#c0d8ffff', 1.4, 8)
    a.spawn_point('block', 0, 0.1, bz + 2.4, 0)
    a.save()
