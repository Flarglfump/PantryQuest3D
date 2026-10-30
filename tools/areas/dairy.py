"""Buttercup Dairy: the farm on the hill in Breadbasket Fields.

A farmyard: the barn, Crème's house, the paddock where Custard the pudding-pony trots, and
the cows. Fresh: Crème sings Custard's Song. Risen: Grubb runs the place; Custard won't
come to anyone... unless someone plays her song.
"""
import math
import random

from areakit import Area, box_wall, town_house
from kit import t3, mesh, collider, tags, script, particles, q


def build(era='fresh'):
    random.seed(91)
    risen = era == 'risen'
    a = Area('dairy', 'Buttercup Dairy', music='music/fields.wav', kill_y=-20, sky='#b0dcf0ff', fog=(26, 56),
             ambient=('#8898b8ff', 0.6), chunk=20, variant=era if risen else '')
    a.entity('Sky', t3((0, 0, 0)), script('scripts/sky.bs', runs=False))
    a.geo('grass', 0, 0).ground(-30, -30, 30, 30, 10, 10, lambda x, z: 0.2 * math.sin(x * 0.2) * math.cos(z * 0.2), uvs=0.25)
    for (x0, z0, x1, z1) in [(-30, -30, 30, -30), (-30, 30, -3, 30), (3, 30, 30, 30), (-30, -30, -30, 30), (30, -30, 30, 30)]:
        box_wall(a, 'planks', x0, z0, x1, z1, -0.5, 1.4, thick=0.4)
    a.loadzone(0, 0, 30.5, 6, 3, 1, to='fields', at='dairy')
    a.spawn_point('start', 0, 0.1, 26, 0)
    a.spawn_point('fields', 0, 0.1, 26, 0)
    # the barn and the house
    town_house(a, -14, -14, 10, 8, 5.0, 0, wall='planks', roof='thatch', door_side='s')
    town_house(a, 14, -16, 7, 6, 4.0, 0, wall='planks', roof='thatch', door_side='s')
    # the paddock (east)
    px, pz = 12, 8
    for k in range(20):
        a0, a1 = 2 * math.pi * k / 20, 2 * math.pi * (k + 1) / 20
        if k in (9, 10):
            continue
        box_wall(a, 'planks', px + math.cos(a0) * 9, pz + math.sin(a0) * 9, px + math.cos(a1) * 9, pz + math.sin(a1) * 9, -0.3, 1.1, thick=0.3)
    a.entity('Custard', t3((px, 0, pz), (0, 0, 0), 1.6), mesh('model', '#f8e0a0ff', file='models/custard.glb', shadow=True),
             ('Animator', [('clip', q('idle')), ('speed', 1), ('loop', True), ('playing', True), ('blend', 0.2)]),
             collider('capsule', (1, 1.0, 1), 0.5, offset=(0, 0.5, 0)), tags('focusable'), script('scripts/pony.bs'))
    for x, z in [(-8, 6), (-12, 10), (-6, 12)]:
        a.entity('Cow', t3((x, 0, z), (0, random.uniform(0, 360), 0), 1.3), mesh('model', '#ffffffff', file='models/cow.glb', shadow=True),
                 ('Animator', [('clip', q('idle')), ('speed', 1), ('loop', True), ('playing', True), ('blend', 0.2)]),
                 collider('capsule', (1, 1.0, 1), 0.5, offset=(0, 0.5, 0)))
    if risen:
        a.npc('creme_risen', 2, 0, -10, 180, model='townswoman', reach=2.4)
        a.npc('grubb', 6, 0, 2, 200, model='baker', reach=2.4)
    else:
        a.npc('creme', 2, 0, -10, 180, model='mint', reach=2.4)
        a.npc('grubb_lazy', -14, 0, -8.5, 160, model='baker', reach=2.4)
    a.sign(-3, 0, 24, 0, 'sign_dairy2')
    a.save()


def build_risen():
    build('risen')
