"""A small driver for Bronto's botrunner: plays Pantry Quest 3D headless with key presses,
reads script variables, and saves screenshots. Used by the play tests in this folder.

    from drive import Game
    g = Game()                       # the project, from the title (or test_scene=...)
    g.hold('w', 30)                  # hold W for 30 frames
    g.press('space'); g.shot('a.png')
"""
import math
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
BRONTO = os.environ.get('BRONTO', os.path.normpath(os.path.join(ROOT, '..', 'bronto')))
KEYS = {'space': 32, 'enter': 257, 'escape': 256, 'tab': 258, 'backspace': 259, 'delete': 261, 'right': 262, 'left': 263,
        'down': 264, 'up': 265, 'shift': 340}
for c in 'abcdefghijklmnopqrstuvwxyz':
    KEYS[c] = ord(c.upper())


class Game:
    def __init__(self, test_scene=None, log=False):
        cmd = [os.path.join(BRONTO, 'build', 'botrunner'), ROOT]
        if test_scene:
            cmd += ['--test-scene', test_scene]
        self.p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None if log else subprocess.DEVNULL, text=True, bufsize=1)
        self.errors = 0
        self.frame_no = 0
        while self.p.stdout.readline().rstrip('\n') != '.':     # ("ready <name>")
            pass

    def cmd(self, line):
        self.p.stdin.write(line + '\n')
        self.p.stdin.flush()
        out = []
        while True:
            l = self.p.stdout.readline()
            if l == '':
                raise RuntimeError('botrunner ended (after %r)' % line)
            l = l.rstrip('\n')
            if l == '.':
                return out
            out.append(l)

    def key(self, name, down):
        self.cmd('key %d %d' % (KEYS[name], 1 if down else 0))

    def frames(self, n):
        r = self.cmd('frame %d' % n)
        line = [l for l in r if l.startswith('frame ')][-1]
        parts = line.split()
        self.frame_no, self.errors = int(parts[1]), int(parts[2])
        return r

    def hold(self, keys, n):
        if isinstance(keys, str):
            keys = [keys]
        for k in keys:
            self.key(k, True)
        self.frames(n)
        for k in keys:
            self.key(k, False)
        self.frames(1)

    def press(self, k, after=4):
        self.hold(k, 2)
        self.frames(after)

    def find(self, name):
        """[(scene, id)] for entities of that name."""
        return [tuple(int(x) for x in l.split()[:2]) for l in self.cmd('find ' + name)]

    def var(self, name, *vars):
        f = self.find(name)
        if not f:
            return None
        s, i = f[-1]
        out = self.cmd('var %d %d %s' % (s, i, ' '.join(vars)))
        return [parse(v) for v in out]

    def scenes(self):
        return self.cmd('scenes')

    def shot(self, file):
        self.cmd('draw')
        self.frames(1)
        self.cmd('save ' + file)

    def quit(self):
        try:
            self.cmd('quit')
        except RuntimeError:
            pass


def parse(v):
    v = v.strip()
    m = re.match(r'^(?:vec3)?\(([-\d.e]+), ([-\d.e]+), ([-\d.e]+)\)$', v)
    if m:
        return tuple(float(x) for x in m.groups())
    m = re.match(r'^\(([-\d.e]+), ([-\d.e]+)\)$', v)
    if m:
        return tuple(float(x) for x in m.groups())
    try:
        return float(v)
    except ValueError:
        return v


def sprig_pos(g):
    v = g.var('Sprig', 'at')
    return v[0] if v and isinstance(v[0], tuple) else None


def goto(g, x, z, near=0.6, max_frames=900, step=3):
    """Walks Sprig towards (x, z) with the movement keys, steering by the camera. True if he
    got there."""
    held = set()
    done = False
    for _ in range(max_frames // step):
        p = sprig_pos(g)
        cam = g.var('Camera', 'pos')[0]
        dx, dz = x - p[0], z - p[2]
        if math.hypot(dx, dz) < near:
            done = True
            break
        ax, az = p[0] - cam[0], p[2] - cam[2]
        l = math.hypot(ax, az) or 1
        ax, az = ax / l, az / l                      # the camera's ahead, flat
        rx, rz = -az, ax                             # its right
        l = math.hypot(dx, dz)
        f, r = (dx * ax + dz * az) / l, (dx * rx + dz * rz) / l
        want = set()
        if f > 0.38: want.add('w')
        if f < -0.38: want.add('s')
        if r > 0.38: want.add('d')
        if r < -0.38: want.add('a')
        for k in held - want: g.key(k, False)
        for k in want - held: g.key(k, True)
        held = want
        g.frames(step)
    for k in held: g.key(k, False)
    g.frames(1)
    return done
