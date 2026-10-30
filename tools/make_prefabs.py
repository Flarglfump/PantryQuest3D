#!/usr/bin/env python3
"""Writes Pantry Quest 3D's prefabs (prefabs/*.scene) and the overlay scenes (dialogue,
pause menu, game over).

    python3 tools/make_prefabs.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'lib'))
from kit import Scene, t3, t2, mesh, collider, kinematic, tags, script, particles, q  # noqa: E402


def prefab(name, comment, *entities):
    s = Scene(comment + '\nMade by tools/make_prefabs.py.')
    for e in entities:
        s.entity(*e)
    s.save(os.path.join('prefabs', name + '.scene'))


def burst(color0, color1, count=24, speed=3.0, size=0.12, life=0.6, gravity=6.0, spread=180, blend='alpha'):
    return particles(rate=0, burst=count, max=count + 8, lifetime=life, lifetime_random=0.4, speed=speed,
                     speed_random=0.5, spread=spread, gravity=gravity, drag=1.2, size_start=size, size_end=0.02,
                     color_start=color0, color_end=color1, blend=blend, auto_destroy=True)


def main():
    prefab('sprig_body', "Sprig's body: the skinned model (sprig.bs turns, rolls and spins it).",
           ('SprigBody', t3((0, 0, 0)), mesh('model', file='models/sprig.glb', shadow=True),
            ('Animator', [('clip', q('idle')), ('speed', 1), ('loop', True), ('playing', True), ('blend', 0.12)])))
    prefab('spoon', "The wooden spoon (sprig.bs places it).",
           ('Spoon', t3((0, 0, 0)), mesh('model', '#d8a868ff', file='models/spoon.obj', cast=False)))
    prefab('potlid', "The pot-lid shield (sprig.bs places it).",
           ('PotLid', t3((0, 0, 0)), mesh('model', '#c0c0c8ff', file='models/potlid.obj', cast=False)))
    prefab('pea', "A pea from the pea shooter (shot.bs).",
           ('Pea', t3((0, 0, 0), scale=0.13), mesh('sphere', '#7ad040ff', cast=False),
            particles(rate=40, max=30, lifetime=0.3, speed=0.3, spread=180, size_start=0.12, size_end=0,
                      color_start='#ffd040ff', color_end='#ff400000', blend='add', emitting=False),
            script('scripts/shot.bs', kind='pea')))
    prefab('nut', "A nut spat by a scrub (shot.bs).",
           ('Nut', t3((0, 0, 0), scale=0.2), mesh('sphere', '#8a5a2aff', cast=False),
            script('scripts/shot.bs', kind='nut')))
    looks = {'heart': ('models/heart.obj', '#ff3048ff', 1.0), 'bean1': ('models/bean.obj', '#40e060ff', 1.0),
             'bean5': ('models/bean.obj', '#4080ffff', 1.0), 'bean20': ('models/bean.obj', '#ff4040ff', 1.1),
             'peas': ('models/bean.obj', '#a0e040ff', 0.7), 'key': ('models/key.obj', '#f0c850ff', 1.0)}
    for kind, (file, color, s) in looks.items():
        prefab('pickup_' + kind, 'A pickup: ' + kind + ' (pickup.bs).',
               ('Pickup', t3((0, 0, 0), scale=s), mesh('model', color, file=file, lit=False, cast=False, shadow=True),
                script('scripts/pickup.bs', kind=kind)))
    prefab('larva', "A mite larva, laid by Queen Mildewmite (enemy.bs).",
           ('Larva', t3((0, 0, 0)), mesh('model', file='models/larva.glb', shadow=True),
            ('Animator', [('clip', q('idle')), ('speed', 1), ('loop', True), ('playing', True), ('blend', 0.1)]),
            collider('capsule', (1, 0.5, 1), 0.25, offset=(0, 0.25, 0)), kinematic(), tags('enemy', 'focusable', 'larva'),
            script('scripts/enemy.bs', brain='larva', hp=1, damage=1)))
    prefab('poof', "A puff of smoke (an enemy beaten, something appearing).",
           ('Poof', t3((0, 0, 0)), burst('#f0f0e0e0', '#a0a09000', 30, 2.5, 0.3, 0.7, -1.0)))
    prefab('spark', "Sparks where a shot hits.",
           ('Spark', t3((0, 0, 0)), burst('#fff0a0ff', '#ff802000', 10, 3.0, 0.08, 0.3, 4.0, blend='add')))
    prefab('clippings', "Cut grass flying.",
           ('Clippings', t3((0, 0, 0)), burst('#70c050ff', '#40803000', 16, 2.8, 0.1, 0.6, 8.0)))
    prefab('shards', "A pot breaking.",
           ('Shards', t3((0, 0, 0)), burst('#c87848ff', '#80482800', 18, 3.5, 0.12, 0.6, 12.0)))
    prefab('slashfx', "A spark where the spoon hits.",
           ('SlashFx', t3((0, 0, 0)), burst('#ffffffff', '#a0d0ff00', 12, 4.0, 0.08, 0.25, 0.0, blend='add')))
    prefab('flame', "A fire burning a web away.",
           ('Flame', t3((0, 0, 0)), particles(rate=60, burst=40, max=120, lifetime=0.8, lifetime_random=0.4, speed=1.5,
                                               speed_random=0.5, spread=40, area=(1.6, 1.6), gravity=-2.0, size_start=0.3,
                                               size_end=0.02, color_start='#ffd060ff', color_end='#ff200000', blend='add',
                                               auto_destroy=True)))

    # ---- overlay scenes (2D, drawn by their scripts) ----
    for name, file, comment in [('dialogue', 'scripts/dialogue.bs', 'The text box (pushed over an area).'),
                                ('pause', 'scripts/pause.bs', 'The pause menu (pushed over an area).'),
                                ('gameover', 'scripts/gameover.bs', 'Game over (pushed over an area).')]:
        s = Scene(comment + '\nMade by tools/make_prefabs.py.')
        s.entity(name.capitalize(), t2((0, 0)), script(file))
        s.save(name + '.scene')
    print('prefabs written')


if __name__ == '__main__':
    main()
