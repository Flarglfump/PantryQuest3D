#!/usr/bin/env python3
"""Tries the controls and the moves that came with the Wind Waker / Ocarina style controls,
headless: the gamepad's buttons (LT focus, items on LB / RB / Y, the D-pad), the camera
moving the focus to the next enemy, the shield planting Sprig, the jump attack with nothing
focused, aiming the Pea Shooter, grabbing a block, floor switches that let go, locks that go
with their doors, and the MAP button. Run from anywhere:

    python3 tools/bot/controls_test.py

Prints ok / FAILED for each; exits 1 if any failed.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from drive import Game, test_scene, goto, parse, face, dir_keys  # noqa: E402

failed = []


def check(cond, what):
    print(('ok    ' if cond else 'FAILED') + ' ' + what)
    if not cond:
        failed.append(what)


def st(g):
    return g.var('Sprig', 'st')[0]


def block(g):
    """Where the Crate Room's block is (the one east of x 10)."""
    for f in g.find('Crust Block'):
        p = parse(g.cmd('var %d %d at' % f)[0])
        if isinstance(p, tuple) and p[0] > 10:
            return p
    return None


def flags(g):
    return g.var('Game', 'flags')[0]


def main():
    items = ['spoon', 'potlid', 'shooter', 'heartpie', 'heartpie', 'pipe', 'song_fennel', 'boots', 'hover']
    # ---- the Crate Room: a floor switch let go of, a block grabbed and pulled
    g = Game(test_scene=test_scene('crock', items=items, flags=['crock_entered', 'clear:crate'], spawn='t_crate'))
    g.frames(30)
    goto(g, 18.6, -5.6, near=0.25)
    g.frames(10)
    check('crock_sw_crate' in flags(g), 'standing on a floor switch holds it down')
    goto(g, 20.5, -3.0, near=0.3)
    g.frames(60)
    check('crock_sw_crate' not in flags(g), 'stepping off lets it go: its door shuts again')
    door = [parse(g.cmd('var %d %d up' % f)[0]) for f in g.find('Switch Door')]
    check(door and door[0] < 0.05, 'the door came back down (%s)' % door)
    # grab the block (Action, held) and pull it towards him
    goto(g, 18.6, 0.6, near=0.2)
    face(g, 0, -1, shield=False)
    g.key('space', True)
    g.frames(6)
    check(st(g) == 'grab', 'Action at a crust block grabs it (%s %s)' % (g.var('Sprig', 'at', 'facing', 'action_label'), block(g)))
    before = block(g)
    ks = dir_keys(g, 0, 1)                    # (back, away from it)
    for k in ks: g.key(k, True)
    g.frames(50)
    for k in ks: g.key(k, False)
    after = block(g)
    check(after[2] - before[2] > 1.4, 'pulled a step towards him (z %.2f -> %.2f)' % (before[2], after[2]))
    g.key('space', False)
    g.frames(5)
    check(st(g) == 'free', 'letting go of Action lets go of it')
    g.hold('w', 40)
    again = block(g)
    check(abs(again[2] - after[2]) < 0.05, 'walking into it no longer pushes it')
    # ---- the gamepad: LT focuses (every time), the camera stick moves to the next enemy
    g.quit()
    g = Game(test_scene=test_scene('crock', items=items, flags=['crock_entered'], spawn='start'))
    g.frames(30)
    # the shield, unfocused: planted, turning on the spot
    p0 = g.var('Sprig', 'at')[0]
    f0 = g.var('Sprig', 'facing')[0]
    g.axis('rt', 1.0); g.frames(4)
    g.axis('left_x', 1.0); g.frames(30); g.axis('left_x', 0.0)
    p1 = g.var('Sprig', 'at')[0]
    f1 = g.var('Sprig', 'facing')[0]
    check(math.hypot(p1[0] - p0[0], p1[2] - p0[2]) < 0.15 and abs(((f1 - f0 + 540) % 360) - 180) > 20,
          'the shield up and unfocused: he turns on the spot, not walking (%s %s -> %s %s)' % (p0, f0, p1, f1))
    g.axis('lt', 1.0); g.frames(4)
    g.axis('left_x', 1.0); g.frames(30); g.axis('left_x', 0.0)
    p2 = g.var('Sprig', 'at')[0]
    check(math.hypot(p2[0] - p1[0], p2[2] - p1[2]) > 0.5, 'focused behind the shield: he steps aside')
    g.axis('rt', 0.0); g.axis('lt', 0.0); g.frames(6)
    goto(g, 0, 9, near=0.4)
    hits = 0
    for i in range(5):
        g.axis('lt', 1.0)
        g.frames(1 if i % 2 else 3)
        if g.var('Sprig', 'focusing')[0] == 1.0:
            hits += 1
        g.axis('lt', 0.0)
        g.frames(4)
    check(hits == 5, 'LT focuses every time it is pulled (%d of 5)' % hits)
    g.axis('lt', 1.0)
    g.frames(4)
    t0 = g.var('Sprig', 'target')[0]
    g.axis('right_x', 1.0); g.frames(3); g.axis('right_x', 0.0); g.frames(3)
    t1 = g.var('Sprig', 'target')[0]
    g.axis('right_x', -1.0); g.frames(3); g.axis('right_x', 0.0); g.frames(3)
    t2 = g.var('Sprig', 'target')[0]
    check(t0 != 'nil' and (t1 != t0 or t2 != t1), 'the right stick moves the focus to the next thing (%s, %s, %s)' % (t0, t1, t2))
    g.axis('lt', 0.0)
    g.frames(4)
    # jump attack with nothing focused (back in the way in, away from the fuzzballs)
    goto(g, 0, 16, near=0.5)
    goto(g, 0, 19, near=0.5)
    g.key('shift', True); g.frames(3)
    check(g.var('Sprig', 'target')[0] == 'nil', '(nothing to focus on here)')
    g.key('w', True); g.frames(3)
    g.key('space', True); g.frames(2)
    s = st(g)
    g.key('space', False); g.key('w', False); g.key('shift', False)
    check(s == 'jumpatk', 'focused and holding forward, Action is a jump attack, with nothing focused (%s)' % s)
    g.frames(40)
    # the Pea Shooter on LB: aims first, then shoots
    peas = g.var('Game', 'peas')[0]
    g.pad_press('lb', 6)
    check(st(g) == 'aim', 'the Pea Shooter (LB) aims first')
    g.axis('left_y', -1.0); g.frames(10); g.axis('left_y', 0.0)
    check(g.var('Sprig', 'aim_pitch')[0] > 5, 'the stick tilts the aim')
    g.pad_press('lb', 6)
    check(g.var('Game', 'peas')[0] == peas - 1 and st(g) == 'aim', 'pressed again, it shoots (and he keeps aiming)')
    g.pad_press('b', 6)
    g.pad_press('x', 30)
    check(st(g) != 'aim', 'attack puts it away')
    # the D-pad: boots on and off, the pipe
    g.pad_press('left', 6)
    check('boots_on' in flags(g), 'D-pad left: the Cast-Iron Boots on')
    g.pad_press('right', 6)
    check('hover_on' in flags(g) and 'boots_on' not in flags(g), 'D-pad right: the Meringue Boots instead')
    g.pad_press('right', 6)
    g.pad_press('down', 10)
    check(any('pipe' in sc for sc in g.scenes()), 'D-pad down: the pipe')
    for b in ['rb', 'y', 'x', 'rb', 'y', 'x']:      # (down right left, twice: Fennel's Tune; the notes are A X LB Y RB)
        g.pad_press(b, 3)
    g.frames(120)
    check(not any('pipe' in sc for sc in g.scenes()), 'RB X Y RB X Y plays Fennel\'s Tune (and the pipe goes)')
    # the Map button
    g.pad_press('back', 10)
    check(any('pause' in sc for sc in g.scenes()), 'Back (Select) opens the menu, on the MAP')
    g.pad_press('back', 10)
    g.quit()
    # ---- a locked door's lock goes with it
    g = Game(test_scene=test_scene('crock', items=items, flags=['crock_entered', 'chest:crock_key1'], spawn='t_proof'))
    g.frames(30)
    g.cmd('var 0 0 x')
    locks = len(g.find('Lock'))
    g.quit()
    g = Game(test_scene=test_scene('crock', items=items, flags=['crock_entered', 'door:crock_proof'], spawn='t_proof'))
    g.frames(30)
    check(len(g.find('Lock')) == locks - 1, 'an opened door\'s lock is gone too (%d -> %d)' % (locks, len(g.find('Lock'))))
    g.quit()
    print('%d failed' % len(failed))
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
