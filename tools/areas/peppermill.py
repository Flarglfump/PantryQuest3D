"""Peppermill Village: a windmill town under Mount Fondue.

North is -z. The road from Breadbasket Fields comes in at the south-west; the windmill
stands in the middle, the dry well beside it, the graveyard to the east; the trail up
Mount Fondue leaves from the north gate, where a guard wants royal permission.
"""
import math
import random

from areakit import Area, box_wall, town_house
from kit import drawn, t3, mesh, collider, tags, script, particles, q

HALF = 44.0


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def height(x, z):
    h = 0.6 * math.sin(x * 0.12) * math.cos(z * 0.1)
    if z < -30:                                   # the foot of the mountain (the trail up its middle)
        h += 6 * smooth((-30 - z) / 10) * smooth((abs(x) - 3) / 7)
    d = max(abs(x), abs(z)) - (HALF - 4)
    if d > 0:                                     # the rim, with gaps for the roads: gently banked either side
        gap = 1.0
        if z > 30:
            gap = min(gap, smooth((abs(x + 30) - 4) / 7))
        if z < -30:
            gap = min(gap, smooth((abs(x) - 3) / 7))
        h += 8 * smooth(d / 4) * gap
    return h


def build(era='fresh'):
    global height
    random.seed(17)
    risen = era == 'risen'
    a = Area('peppermill', 'Peppermill Village', music='music/peppermill.wav', kill_y=-20, sky='#b0dcf0ff', fog=(60, 125),
             ambient=('#8898b8ff', 0.55), chunk=22, variant=era if risen else '')
    a.entity('Sky', t3((0, 0, 0)), script('scripts/sky.bs'))
    for cz in range(-48, 48, 12):
        for cx in range(-48, 48, 12):
            a.geo('grass', cx + 6, cz + 6).ground(cx, cz, cx + 12, cz + 12, 3, 3, height, uvs=0.25)

    height = drawn(height)        # (from here on, things are set on the ground as drawn: none float or sink)
    a.path([(-30, 46), (-30, 36), (-24, 30), (-10, 14), (0, 4), (0, -20), (0, -46)], 3.0)
    a.path([(0, 4), (22, 0), (30, -6)], 2.2)

    # ---- the way in from the field (south-west) ----
    a.loadzone(-30, height(-30, HALF - 1), HALF - 0.5, 8, 4, 1.4, to='fields', at='peppermill')
    a.spawn_point('start', -28, height(-28, 36) + 0.1, 36, 20)
    a.spawn_point('fields', -28, height(-28, 36) + 0.1, 36, 20)
    a.spawn_point('fondue', 0, height(0, -32) + 0.1, -32, 180)
    a.sign(-24, height(-24, 34), 34, 200, 'sign_pepper')

    # ---- the windmill ----
    wx, wz = -6, -6
    wy = height(wx, wz)
    a.geo('planks', wx, wz).cylinder((wx, wy - 0.3, wz), 3.4, 9.5, 12, top=False, radius_top=2.4, uvs=0.3)
    a.geo('thatch', wx, wz).cone((wx, wy + 9.2, wz), 2.9, 3.2, 12)
    a.entity('Door', t3((wx, wy + 1.0, wz + 3.35), (0, 0, 0), (1.2, 2.0, 0.1)), mesh('cube', '#5a3a20ff', 'art/planks.png'))
    a.entity('Sails', t3((wx, wy + 8.0, wz + 2.9), (0, 0, 0), (1, 1, 1)), mesh('model', '#e8e0c8ff', 'art/thatch.png', file='models/sails.obj', cull=False),
             script('scripts/spinner.bs', speed=40))
    if risen:
        a.npc('risen_miller', wx + 3.2, wy, wz + 4.5, 160, model='miller')
    else:
        a.npc('miller', wx + 3.2, wy, wz + 4.5, 160)
    # the well
    a.geo('stone', 6, 6).cylinder((6, height(6, 6) - 0.3, 6), 1.4, 1.2, 12, top=False, uvs=0.6)
    a.geo('stone', 6, 6).cylinder((6, height(6, 6) - 0.3, 6), 1.1, 1.18, 12, top=False, uvs=0.6, inside=True)
    a.entity('Well Ring', t3((6, height(6, 6) + 0.45, 6)), collider('capsule', (1, 1, 1), 1.4), tags('seethrough'))
    if risen:      # the Boiling Song dries it up: a way down
        a.entity('Well', t3((6, height(6, 6) + 0.6, 6)), tags('interact', 'focusable'),
                 script('scripts/climbdown.bs', to='well', at='start', needs='well_drained', say='well_look'))
        a.entity('Well Water', t3((6, height(6, 6) + 0.5, 6), (0, 0, 0), (2.1, 0.05, 2.1)), mesh('cylinder', '#304860ff', lit=False),
                 script('scripts/songdoor.bs', song='boiling', id='well_drained', say='well_look', reach=0.1))
        a.spawn_point('well', 6, height(6, 9) + 0.1, 9, 180)
    else:
        a.entity('Well', t3((6, height(6, 6) + 0.6, 6)), tags('interact', 'focusable'), script('scripts/sign.bs', say='sign_well', prompt='Look', reach=2.4))
    # houses
    for x, z, w, d, side in [(-24, 6, 7, 6, 'e'), (-26, -16, 7, 6, 'e'), (14, 20, 7, 6, 'n'), (-10, 24, 6, 6, 'n'), (18, -20, 7, 6, 's')]:
        town_house(a, x, z, w, d, 3.8, height(x, z), wall='planks', roof='thatch', door_side=side)
    a.sign(18, height(18, -16.2), -16.2, 0, 'sign_potions')
    a.npc('weevil_house', 14, height(14, 24), 24, 180, model='hardtack_kid', reach=2.4)
    a.sign(16.5, height(16.5, 24), 24, 180, 'sign_weevils')
    # the graveyard (east)
    gx, gz = 30, -6
    for i in range(3):
        for j in range(3):
            x, z = gx - 4 + i * 4, gz - 6 + j * 4
            a.entity('Grave', t3((x, height(x, z) + 0.5, z), (0, 0, 0), (0.9, 1.0, 0.25)), mesh('cube', '#a8a8b0ff', 'art/stone.png'),
                     collider('box'), tags('interact'), script('scripts/sign.bs', say='grave', reach=1.6))
    for x0, z0, x1, z1 in [(gx - 7, gz - 9, gx + 7, gz - 9), (gx - 7, gz + 7, gx - 2, gz + 7), (gx + 2, gz + 7, gx + 7, gz + 7),
                           (gx + 7, gz - 9, gx + 7, gz + 7), (gx - 7, gz - 9, gx - 7, gz + 7)]:
        box_wall(a, 'stone', x0, z0, x1, z1, height(x0, z0) - 0.3, height(x0, z0) + 0.9, thick=0.5)
    if risen:      # the Compost Crypt's door, at the back of the graveyard; Cinder, once the lens is found
        a.geo('stone', gx, gz - 10).box((gx - 3, height(gx, gz - 10) - 0.5, gz - 11.5), (gx + 3, height(gx, gz - 10) + 4.5, gz - 10.5), uvs=0.3)
        cy0 = height(gx, gz - 10)
        a.entity('Crypt Door', t3((gx, cy0 + 1.5, gz - 10.4), (0, 0, 0), (2.4, 3.0, 0.2)), mesh('cube', '#3a2a3aff', 'art/stone.png'),
                 collider('box'), tags('interact', 'focusable'), script('scripts/songdoor.bs', song='nocturne', id='door:crypt', say='crypt_door', reach=3.0))
        a.entity('Crypt Dark', t3((gx, cy0 + 1.5, gz - 10.47), (0, 0, 0), (2.44, 3.04, 0.1)), mesh('cube', '#08040aff', lit=False))     # (a little bigger than the door: its edges in the walls, not in the door's planes)
        a.loadzone(gx, cy0, gz - 10.2, 2.2, 3, 0.5, to='crypt', at='start', needs='door:crypt')
        a.spawn_point('crypt', gx, cy0 + 0.1, gz - 8.2, 180)
        a.spawn_point('graveyard', gx, height(gx, gz + 9) + 0.1, gz + 9, 180)
        a.npc('cinder', gx + 3, height(gx + 3, gz + 9.5), gz + 9.5, 200, needs='chest:well_lens', reach=2.4)
    if risen:      # the old gravekeeper's ghost, who races
        a.entity('Ghost', t3((gx, height(gx, gz + 4.8) + 0.2, gz + 4.8), (0, 180, 0)), mesh('model', '#c0e0ffa0', file='models/gravekeeper.glb'),
                 ('Animator', [('clip', q('idle')), ('speed', 1), ('loop', True), ('playing', True), ('blend', 0.2)]),
                 tags('interact', 'focusable'), script('scripts/racer.bs'))
    else:
        a.npc('gravekeeper', gx, height(gx, gz + 9), gz + 9, 180)
    a.sign(gx - 3, height(gx - 3, gz + 9), gz + 9, 180, 'sign_grave')
    # the mountain gate
    gz2 = -30
    for xx in (-4.5, 4.5):
        a.geo('stone', xx, gz2).box((xx - 1.2, height(xx, gz2) - 1, gz2 - 1.2), (xx + 1.2, height(xx, gz2) + 5, gz2 + 1.2), uvs=0.3)
    if not risen:
        a.blocker(0, height(0, gz2 + 0.5), gz2 + 0.5, (6.4, 1.6, 0.25), 'mountain_open')
        a.npc('mtguard', 2.0, height(2, gz2 + 2.4), gz2 + 2.4, 170, model='guard')
    a.loadzone(0, height(0, -HALF + 1), -HALF + 0.8, 6, 4, 1.2, to='fondue', at='start')
    # trees, pots, grass
    for x, z in [(-34, 18), (-36, -4), (32, 24), (34, 12), (-14, -26), (12, 32), (-38, 30)]:
        a.tree(x, height(x, z), z, random.uniform(1.0, 1.4), random.choice(['', 'bean1', 'heart']))
    for x, z in [(-20, 4), (-20.8, 4.8), (12, 18), (-8, 22), (16, -18)]:
        a.pot(x, height(x, z), z)
    n = 0
    while n < 30:
        x, z = random.uniform(-38, 38), random.uniform(-26, 38)
        if abs(x) < 3 or math.hypot(x - wx, z - wz) < 6 or (gx - 9 < x < gx + 9 and gz - 11 < z < gz + 11):
            continue
        a.grass(x, height(x, z), z)
        n += 1
    a.save()


def build_risen():
    build('risen')
