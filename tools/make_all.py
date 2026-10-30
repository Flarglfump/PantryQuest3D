#!/usr/bin/env python3
"""Makes everything generated in Pantry Quest 3D: art, sounds, music, models, prefabs and
the areas. Run from anywhere:  python3 tools/make_all.py
"""
import os
import runpy
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'lib'))
sys.path.insert(0, os.path.join(HERE, 'areas'))
os.chdir(os.path.join(HERE, '..'))

AREAS = ['sprouthollow', 'crock', 'fields', 'town', 'castle', 'peppermill', 'fondue', 'hardtack', 'hardcaves', 'gorge', 'fizzdomain', 'fountain', 'lake', 'gulp', 'title']


def main(what):
    if 'art' in what:
        runpy.run_path(os.path.join(HERE, 'make_art.py'), run_name='__main__')
    if 'sound' in what and os.path.exists(os.path.join(HERE, 'make_sound.py')):
        runpy.run_path(os.path.join(HERE, 'make_sound.py'), run_name='__main__')
    if 'music' in what and os.path.exists(os.path.join(HERE, 'make_music.py')):
        runpy.run_path(os.path.join(HERE, 'make_music.py'), run_name='__main__')
    if 'models' in what:
        runpy.run_path(os.path.join(HERE, 'make_models.py'), run_name='__main__')
    if 'prefabs' in what:
        runpy.run_path(os.path.join(HERE, 'make_prefabs.py'), run_name='__main__')
    one = [n for n in what if n in AREAS]
    if 'areas' in what or one:
        print('areas:')
        for name in (one or AREAS):
            if os.path.exists(os.path.join(HERE, 'areas', name + '.py')):
                mod = __import__(name)
                mod.build()


if __name__ == '__main__':
    main(sys.argv[1:] or ['art', 'sound', 'music', 'models', 'prefabs', 'areas'])
