"""Peppermill Village: a windmill town under Mount Fondue.

North is -z. The road from Breadbasket Fields comes in at the south-west; the windmill
stands in the middle, the dry well beside it, the graveyard to the east; the trail up
Mount Fondue leaves from the north gate, where a guard wants royal permission.
"""
import math
import random

from areakit import Area, box_wall, town_house
from kit import t3, mesh, collider, tags, script, particles, q

HALF = 44.0


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def height(x, z):
    h = 0.6 * math.sin(x * 0.12) * math.cos(z * 0.1)
    if z < -30:                                   # the foot of the mountain
        h += 6 * smooth((-30 - z) / 10) * smooth((abs(x) - 3) / 3)
    d = max(abs(x), abs(z)) - (HALF - 4)
    if d > 0 and not (abs(x + 30) < 5 and z > 30) and not (abs(x) < 4 and z < -30):
        h += 8 * smooth(d / 4)
    return h


def build():
    random.seed(17)
    a = Area('peppermill', 'Peppermill Village', music='music/peppermill.wav', kill_y=-20, sky='#b0dcf0ff', fog=(28, 58),
             ambient=('#8898b8ff', 0.55), chunk=22)
    a.entity('Sky', t3((0, 0, 0)), script('scripts/sky.bs'))
    for cz in range(-48, 48, 12):
        for cx in range(-48, 48, 12):
            a.geo('grass', cx + 6, cz + 6).ground(cx, cz, cx + 12, cz + 12, 3, 3, height, uvs=0.25)

    def path(points, width):
        for (x0, z0), (x1, z1) in zip(points, points[1:]):
            n = max(1, int(math.hypot(x1 - x0, z1 - z0) / 2.5))
            for i in range(n):
                ax, az = x0 + (x1 - x0) * i / n, z0 + (z1 - z0) * i / n
                bx, bz = x0 + (x1 - x0) * (i + 1) / n, z0 + (z1 - z0) * (i + 1) / n
                L = math.hypot(bx - ax, bz - az) or 1
                px, pz = -(bz - az) / L * width / 2, (bx - ax) / L * width / 2
                P = [(ax - px, az - pz), (bx - px, bz - pz), (bx + px, bz + pz), (ax + px, az + pz)]
                Y = [(p[0], height(*p) + 0.05, p[1]) for p in P]
                U = [(p[0] / 3, p[1] / 3) for p in P]
                o = a.geo('dirt', ax, az)
                if (P[1][0] - P[0][0]) * (P[2][1] - P[0][1]) - (P[1][1] - P[0][1]) * (P[2][0] - P[0][0]) < 0:
                    o.quad(Y[0], Y[1], Y[2], Y[3], *U)
                else:
                    o.quad(Y[3], Y[2], Y[1], Y[0], U[3], U[2], U[1], U[0])
    path([(-30, 46), (-24, 30), (-10, 14), (0, 4), (0, -20), (0, -46)], 3.0)
    path([(0, 4), (22, 0), (30, -6)], 2.2)

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
    a.npc('miller', wx + 3.2, wy, wz + 4.5, 160)
    # the well
    a.geo('stone', 6, 6).cylinder((6, height(6, 6) - 0.3, 6), 1.4, 1.2, 12, top=False, uvs=0.6)
    a.geo('stone', 6, 6).cylinder((6, height(6, 6) - 0.3, 6), 1.1, 1.18, 12, top=False, uvs=0.6, inside=True)
    a.entity('Well Ring', t3((6, height(6, 6) + 0.45, 6)), collider('capsule', (1, 1, 1), 1.4), tags('seethrough'))
    a.entity('Well', t3((6, height(6, 6) + 0.6, 6)), tags('interact', 'focusable'), script('scripts/sign.bs', say='sign_well', prompt='Look', reach=2.4))
    # houses
    for x, z, w, d, side in [(-24, 6, 7, 6, 'e'), (-26, -16, 7, 6, 'e'), (14, 20, 7, 6, 'n'), (-10, 24, 6, 6, 'n'), (18, -20, 7, 6, 's')]:
        town_house(a, x, z, w, d, 3.8, height(x, z), wall='planks', roof='thatch', door_side=side)
    a.sign(18, height(18, -16.2), -16.2, 0, 'sign_potions')
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
    a.npc('gravekeeper', gx, height(gx, gz + 9), gz + 9, 180)
    a.sign(gx - 3, height(gx - 3, gz + 9), gz + 9, 180, 'sign_grave')
    # the mountain gate
    gz2 = -30
    for xx in (-4.5, 4.5):
        a.geo('stone', xx, gz2).box((xx - 1.2, height(xx, gz2) - 1, gz2 - 1.2), (xx + 1.2, height(xx, gz2) + 5, gz2 + 1.2), uvs=0.3)
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
