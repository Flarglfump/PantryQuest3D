#!/usr/bin/env python3
"""Writes Pantry Quest 3D's prefabs (prefabs/*.scene) and the overlay scenes (dialogue,
pause menu, game over).

    python3 tools/make_prefabs.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'lib'))
from kit import Scene, t3, t2, mesh, collider, kinematic, tags, script, particles, light, q  # noqa: E402


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
    prefab('swingtrail', "The streak a swung spoon or cleaver leaves (sprig.bs puts it at the tip and turns it on while he swings).",
           ('Swing Trail', t3((0, 0, 0)), particles(emitting=False, rate=420, max=200, lifetime=0.16, speed=0, spread=0,
                                                   size_start=0.17, size_end=0.02, color_start='#fff8e0a8',
                                                   color_end='#ffd08000', blend='add')))
    prefab('shooter_held', "The Pea Shooter in Sprig's hand, while he aims (sprig.bs places it).",
           ('Shooter', t3((0, 0, 0)), mesh('model', '#a07040ff', file='models/shooter.obj', cast=False)))
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
             'peas': ('models/bean.obj', '#a0e040ff', 0.7), 'key': ('models/key.obj', '#f0c850ff', 1.0),
             'popcorn': ('models/bomb.obj', '#fff4d0ff', 0.6)}
    for kind, (file, color, s) in looks.items():
        prefab('pickup_' + kind, 'A pickup: ' + kind + ' (pickup.bs).',
               ('Pickup', t3((0, 0, 0), scale=s), mesh('model', color, file=file, lit=False, cast=False, shadow=True), tags('pickup'),
                script('scripts/pickup.bs', kind=kind)))
    prefab('larva', "A mite larva, laid by Queen Mildewmite (enemy.bs).",
           ('Larva', t3((0, 0, 0)), mesh('model', file='models/larva.glb', shadow=True),
            ('Animator', [('clip', q('idle')), ('speed', 1), ('loop', True), ('playing', True), ('blend', 0.1)]),
            collider('capsule', (1, 0.5, 1), 0.25, offset=(0, 0.25, 0)), kinematic(), tags('enemy', 'focusable', 'larva'),
            script('scripts/enemy.bs', brain='larva', hp=1, damage=1)))
    prefab('sight', "A guard's sight: a pale cone on the ground (guard.bs places it).",
           ('Sight', t3((0, 0, 0), (90, 0, 0)), mesh('cone', '#fff0a040', lit=False, cull=False, cast=False)))
    prefab('bomb', "A popcorn bomb (bomb.bs).",
           ('Bomb', t3((0, 0, 0)), mesh('model', '#fff4d0ff', file='models/bomb.obj', shadow=True, cast=False), tags('bomb'),
            particles(rate=25, max=20, lifetime=0.3, speed=0.8, spread=40, size_start=0.08, size_end=0, color_start='#ffe080ff',
                      color_end='#ff400000', blend='add', local=True, area=(0.05, 0.05)),
            script('scripts/bomb.bs')))
    prefab('fireball', "A gout of fire (shot.bs).",
           ('Fireball', t3((0, 0, 0), scale=0.4), mesh('sphere', '#ffa030ff', lit=False, cast=False),
            particles(rate=50, max=40, lifetime=0.4, speed=0.6, spread=180, size_start=0.3, size_end=0, color_start='#ffe080ff',
                      color_end='#ff200000', blend='add'),
            script('scripts/shot.bs', kind='fire', life=2.0)))
    prefab('boomerang', "The Spatula Boomerang in flight (boomerang.bs).",
           ('Boomerang', t3((0, 0, 0)), mesh('model', '#d0c0a0ff', file='models/spatula.obj', cast=False, cull=False), script('scripts/boomerang.bs')))
    prefab('cleaver', "The Cleaver of Dawn in Sprig's hand (placed by sprig.bs).",
           ('Cleaver', t3((0, 0, 0)), mesh('model', '#e0e8f0ff', file='models/cleaver.obj', cast=False)))
    prefab('lashline', "The Licorice Lash's line (sprig.bs stretches it).",
           ('Lash Line', t3((0, 0, 0), scale=(0.06, 0.06, 0.1)), mesh('cube', '#c02838ff', cast=False, lit=False)))
    prefab('arrow', "A skewer from the Skewer Bow (shot.bs).",
           ('Arrow', t3((0, 0, 0), scale=(0.05, 0.05, 0.7)), mesh('cube', '#e0c890ff', cast=False),
            particles(rate=40, max=30, lifetime=0.3, speed=0.3, spread=180, size_start=0.12, size_end=0,
                      color_start='#ffd040ff', color_end='#ff400000', blend='add', emitting=False),
            script('scripts/shot.bs', kind='arrow')))
    prefab('orb', "A ball of mould-light the Hollow Duke throws (orb.bs).",
           ('Orb', t3((0, 0, 0), scale=0.45), mesh('sphere', '#c0ff80ff', lit=False, cast=False), collider('sphere', radius=0.6, trigger=True),
            particles(rate=30, max=40, lifetime=0.4, speed=0.4, spread=180, size_start=0.3, size_end=0, color_start='#e0ffa0ff', color_end='#60a02000', blend='add'),
            script('scripts/orb.bs')))
    prefab('pickup_arrows', "A bundle of skewers to pick up (pickup.bs).",
           ('Pickup', t3((0, 0, 0), scale=(0.08, 0.08, 0.6)), mesh('cube', '#e0c890ff', lit=False, cast=False), tags('pickup'),
            script('scripts/pickup.bs', kind='arrows')))
    prefab('hammer', "The Meat Tenderizer in Sprig's hands (sprig.bs, while he swings it).",
           ('Hammer', t3((0, 0, 0)), mesh('model', '#c0c0c8ff', file='models/hammer.obj', cast=False)))
    prefab('dragonseg', "A piece of Gratinox's body (gratinox.bs moves it).",
           ('Dragon Body', t3((0, 0, 0), scale=1.1), mesh('sphere', '#d06030ff', 'art/crust.png', cast=False),
            particles(rate=6, max=10, lifetime=0.6, speed=0.5, spread=60, size_start=0.4, size_end=0, color_start='#ffb040c0', color_end='#ff400000', blend='add')))
    prefab('mawhand', "One of the Maw of Rot's hands (mawhand.bs).",
           ('Maw Hand', t3((0, 0, 0), scale=(1.6, 0.6, 1.8)), mesh('sphere', '#8a6a5aff', 'art/rot.png'), collider('sphere', radius=0.6, trigger=True),
            tags('enemy', 'focusable', 'shootable'), script('scripts/mawhand.bs')))
    prefab('bolt', "A witch's bolt (bolt.bs).",
           ('Bolt', t3((0, 0, 0), scale=0.4), mesh('sphere', '#ff6040ff', lit=False, cast=False),
            particles(rate=30, max=40, lifetime=0.4, speed=0.4, spread=180, size_start=0.3, size_end=0, color_start='#ffffffc0', color_end='#ffffff00', blend='add'),
            script('scripts/bolt.bs')))
    prefab('bigfire', "A great fire (the castle burning: storm.bs).",
           ('Big Fire', t3((0, 0, 0)), particles(rate=40, max=80, lifetime=1.4, speed=2.5, spread=20, area=(6, 2), gravity=-2,
                                                 size_start=2.4, size_end=0.3, color_start='#ffb040ff', color_end='#c0200000', blend='add'),
            light('point', '#ff7030ff', 2.0, range=22)))
    prefab('rain', "Rain round Sprig in the storm (storm.bs).",
           ('Rain', t3((0, 6, 0)), particles(rate=160, max=300, lifetime=0.6, speed=6, spread=5, angle=90, area=(18, 18), gravity=30,
                                             size_start=0.09, size_end=0.07, color_start='#d0e0ffe0', color_end='#c0d0f080')))
    prefab('knotarm', "One of the Gristle Knot's tendrils (knotarm.bs).",
           ('Knot Arm', t3((0, 0, 0)), mesh('model', '#e8d0b0ff', file='models/tendril.obj'), tags('focusable', 'shootable'), script('scripts/knotarm.bs')))
    prefab('fizzstone', "A fizz-stone for the diving game (divestone.bs).",
           ('Fizz Stone', t3((0, 0, 0)), mesh('model', '#a0f0ffff', file='models/fizzstone.obj', lit=False), script('scripts/divestone.bs')))
    prefab('fish', "A little fish in the shallows (fish.bs).",
           ('Fish', t3((0, 0, 0)), mesh('model', '#f0a040ff', file='models/fish.obj'), tags('fish'), script('scripts/fish.bs')))
    prefab('blast', "A bomb going off.",
           ('Blast', t3((0, 0, 0)), burst('#fff0b0ff', '#ff401000', 60, 6.0, 0.5, 0.6, -2.0, blend='add')))
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
                                               auto_destroy=True), script('scripts/burnout.bs', time=0.9)))

    # ---- overlay scenes (2D, drawn by their scripts) ----
    for name, file, comment in [('dialogue', 'scripts/dialogue.bs', 'The text box (pushed over an area).'),
                                ('pause', 'scripts/pause.bs', 'The pause menu (pushed over an area).'),
                                ('gameover', 'scripts/gameover.bs', 'Game over (pushed over an area).'),
                                ('pipe', 'scripts/pipe.bs', 'Playing the pipe (pushed over an area).'),
                                ('controls', 'scripts/controls.bs', 'The controls page (pushed over the title or the pause menu).'),
                                ('settings', 'scripts/settings.bs', 'The settings page: the volume sliders (pushed over the title or the pause menu).')]:
        s = Scene(comment + '\nMade by tools/make_prefabs.py.')
        s.entity(name.capitalize(), t2((0, 0)), script(file))
        s.save(name + '.scene')
    print('prefabs written')


if __name__ == '__main__':
    main()
