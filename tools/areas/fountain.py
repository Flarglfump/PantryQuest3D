"""Fizzwater Fountain: the spring where the Fizzlings' river begins, behind the throne.

An open hollow in the mountain, under the sky. The tunnel from the Domain comes in at the
south onto a shore of blue stone, with shallows where little fish dart. A stone pier runs
out to Lord Gulp's altar; the great sturgeon floats asleep beyond it.
"""
import math
import random

from areakit import Area
from kit import t3, mesh, collider, tags, script, particles


SURF = -0.3


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def height(x, z):
    r = math.hypot(x, z + 6)
    h = 0.0 if z > -2 else -5 + 5 * smooth((z + 6) / 4)
    if (x + 9) ** 2 / 25 + (z - 8) ** 2 / 16 < 1:             # the shallows
        h = min(h, -0.7)
    h += 14 * smooth((r - 30) / 5)                              # the hollow's walls
    return h


def build(era='fresh'):
    random.seed(41)
    risen = era == 'risen'
    a = Area('fountain', 'Fizzwater Fountain', music='music/fizz.wav' if not risen else 'music/castle.wav', kill_y=-20,
             sky='#c8e8f8ff' if not risen else '#d8e8f0ff', fog=(26, 60), ambient=('#98b8d8ff', 0.6) if not risen else ('#c0d0e0ff', 0.7),
             chunk=20, variant=era if risen else '')
    if not risen:
        a.entity('Sky', t3((0, 0, 0)), script('scripts/sky.bs', runs=False))
    for cz in range(-42, 30, 12):
        for cx in range(-36, 36, 12):
            a.geo('fizzrock', cx + 6, cz + 6).ground(cx, cz, cx + 12, cz + 12, 6, 6, height, uvs=0.25)
    if risen:      # frozen over: walk on it
        a.geo('ice', 0, -20).box((-34, SURF - 0.5, -40), (34, SURF, -1), uvs=0.2, sides=('py',))
        a.entity('Ice Sheet', t3((0, SURF - 0.25, -20.5)), collider('box', (68, 0.5, 39)))
        a.geo('ice', -9, 8).box((-14, SURF - 0.3, 4), (-4, SURF + 0.2, 12), uvs=0.25, sides=('py',))
        a.entity('Ice Shallows', t3((-9, SURF - 0.05, 8)), collider('box', (10, 0.5, 8)))
        # the Freezer Caves, across the ice (north)
        a.geo('stone', 0, -38).box((-4, SURF, -40), (4, 6, -38.6), uvs=0.3)
        a.entity('Cave Mouth', t3((0, SURF + 1.6, -38.5), (0, 0, 0), (3.0, 3.2, 0.1)), mesh('cube', '#081018ff', lit=False))
        a.loadzone(0, SURF, -38.2, 3, 3, 0.6, to='freezer', at='start')
        a.spawn_point('freezer', 0, SURF + 0.1, -36, 180)
        a.sign(2.5, SURF, -35, 180, 'sign_freezer')
    else:
        a.water(-34, -40, 34, -1, SURF, depth=6)
        a.water(-14, 4, -4, 12, SURF + 0.2, depth=1.2)
    # the tunnel from the Domain
    a.geo('fizzrock', 0, 26).box((-3, 0, 22), (3, 0.2, 30), uvs=0.3)
    a.loadzone(0, 0, 25.5, 3, 3, 0.8, to='fizzdomain', at='fountain')
    a.spawn_point('start', 0, 0.1, 20, 0)
    # the pier and Lord Gulp's altar
    a.geo('stone', 0, -6).box((-1.6, -5, -12), (1.6, 0.1, -1), uvs=0.4)
    a.geo('stone', 0, -12).box((-2.6, -5, -14.5), (2.6, 0.3, -11.5), uvs=0.4)
    for xx in (-2.2, 2.2):
        a.geo('stone', xx, -14).box((xx - 0.3, 0.3, -14.3), (xx + 0.3, 2.2, -13.7), uvs=0.4)
    for x, z in [(18, 8), (-20, 18), (20, 18)]:
        a.tree(x, height(x, z), z, random.uniform(1.0, 1.3))
    n = 0
    while n < 14:
        x, z = random.uniform(-24, 24), random.uniform(2, 22)
        if abs(x) < 4 or (x + 9) ** 2 / 36 + (z - 8) ** 2 / 25 < 1:
            continue
        a.grass(x, height(x, z), z)
        n += 1
    if risen:
        a.save()
        return
    gi = a.entity('Lord Gulp', t3((0, -2.8, -21.5), (0, 180, 0)), mesh('model', '#a0b4c8ff', 'art/fizzrock.png', file='models/gulp.obj'),
                  collider('sphere', radius=4.0, offset=(0, 3.2, 1.5)), tags('interact', 'focusable', 'fishfeed'),
                  script('scripts/gulpaltar.bs', reach=9))
    a.entity('Jaw', t3((0, 2.5, -4.0), (0, 0, 0), (3.0, 0.6, 2.0)), mesh('cube', '#6a7890ff', 'art/stone.png'), ('Parent', [('entity', gi)]))
    for sx in (-1, 1):
        a.entity('Gulp Eye', t3((sx * 2.9, 4.2, -1.4), (0, 0, 0), 0.9), mesh('sphere', '#f0f0e0ff', lit=False), ('Parent', [('entity', gi)]))
        a.entity('Gulp Pupil', t3((sx * 3.25, 4.2, -1.7), (0, 0, 0), (0.3, 0.12, 0.3)), mesh('sphere', '#101018ff', lit=False), ('Parent', [('entity', gi)]))
    a.entity('Gulp Fin', t3((0, 6.4, 1.5), (20, 0, 0), (0.3, 1.6, 3.0)), mesh('cube', '#6a7890ff', 'art/stone.png'), ('Parent', [('entity', gi)]))
    a.entity('Gulp Bubbles', t3((0, SURF, -17)), particles(rate=3, max=10, lifetime=1.5, speed=0.8, spread=20, area=(1, 1), gravity=-0.5,
                                                            size_start=0.3, size_end=0.6, color_start='#ffffffa0', color_end='#ffffff00'))
    a.spawn_point('gulp', 0, 0.4, -11.5, 180)
    # fish in the shallows
    for x, z in [(-9, 7), (-7, 9), (-11, 9.5), (-8.5, 5.5)]:
        a.entity('Fish', t3((x, -0.5, z)), mesh('model', '#f0a040ff', file='models/fish.obj'), tags('fish'), script('scripts/fish.bs'))
    a.sign(-4, 0, 13, 90, 'gulp_look')
    # Fizzy, home again
    a.npc('fizzy', 3, 0, 4, 200, needs='gulp_done', reach=2.4)
    a.save()


def build_risen():
    build('risen')
