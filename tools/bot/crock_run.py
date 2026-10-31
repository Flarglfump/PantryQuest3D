#!/usr/bin/env python3
"""Plays the Great Crock through, start to boss, the way a player would: walking (camera-
relative keys), pushing blocks, riding the dough, shooting through flames. Run from anywhere:

    python3 tools/bot/crock_run.py [--shots DIR]

It stops at the first step that doesn't work, saying which.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from drive import Game, test_scene  # noqa: E402

SHOTS = sys.argv[sys.argv.index('--shots') + 1] if '--shots' in sys.argv else None


class Run:
    def __init__(self):
        self.g = Game(test_scene=test_scene('crock', items=['spoon', 'potlid', 'heartpie', 'heartpie', 'heartpie'], flags=['crock_entered'], spawn='start'))
        self.g.frames(40)
        self.n = 0

    def at(self):
        return self.g.var('Sprig', 'at')[0]

    def flag(self, f):
        fl = self.g.var('Game', 'flags')[0]
        return f in fl if isinstance(fl, str) else False

    def keys(self, kind):
        c = self.g.var('Game', 'counters')[0]
        return c

    def shot(self, name):
        self.n += 1
        if SHOTS:
            self.g.shot(os.path.join(SHOTS, '%02d_%s.bmp' % (self.n, name)))

    def fail(self, why):
        self.shot('FAILED')
        print('FAILED:', why, '| Sprig at', self.at(), self.g.var('Sprig', 'st'), '| errors', self.g.errors)
        sys.exit(1)

    def step_keys(self, dx, dz):
        """Hold the keys that move Sprig towards (dx, dz), as the camera sees it, for a few frames."""
        cam = self.g.var('Camera', 'pos')[0]
        me = self.at()
        fx, fz = me[0] - cam[0], me[2] - cam[2]
        l = math.hypot(fx, fz) or 1
        fx, fz = fx / l, fz / l
        rx, rz = -fz, fx                      # (right of the camera's forward, y up)
        f = dx * fx + dz * fz
        r = dx * rx + dz * rz
        ks = []
        if f > 0.38: ks.append('w')
        if f < -0.38: ks.append('s')
        if r > 0.38: ks.append('d')
        if r < -0.38: ks.append('a')
        return ks

    def goto(self, x, z, near=0.35, limit=600):
        stuck, last = 0, None
        for i in range(limit // 3):
            me = self.at()
            dx, dz = x - me[0], z - me[2]
            d = math.hypot(dx, dz)
            if d < near:
                return True
            ks = self.step_keys(dx / d, dz / d)
            for k in ks: self.g.key(k, True)
            self.g.frames(3)
            for k in ks: self.g.key(k, False)
            if last is not None and math.hypot(me[0] - last[0], me[2] - last[2]) < 0.01:
                stuck += 1
                if stuck > 40:
                    self.fail('stuck going to (%.1f, %.1f)' % (x, z))
            else:
                stuck = 0
            last = me
            self.advance_talk()
        self.fail('never reached (%.1f, %.1f)' % (x, z))

    def advance_talk(self):
        for i in range(10):
            if not any('dialogue' in s for s in self.g.scenes()):
                return
            self.g.press('space', 6)

    def face(self, yaw):
        """Turn to face a compass yaw (0: north, -z; 90: west; 180: south; 270: east)."""
        dx, dz = -math.sin(math.radians(yaw)), -math.cos(math.radians(yaw))
        for i in range(10):                   # (taps: he turns, hardly moving)
            ks = self.step_keys(dx, dz)
            for k in ks: self.g.key(k, True)
            self.g.frames(1)
            for k in ks: self.g.key(k, False)
            self.g.frames(3)
        self.g.frames(4)

    def aim(self, yaw):
        """Turn on the spot until he faces yaw (within a few degrees): one-frame taps."""
        for i in range(40):
            f = self.g.var('Sprig', 'facing')[0]
            err = (yaw - f + 540) % 360 - 180
            if abs(err) < 5:
                return
            turn = f + (50 if err > 0 else -50)
            ks = self.step_keys(-math.sin(math.radians(turn)), -math.cos(math.radians(turn)))
            for k in ks: self.g.key(k, True)
            self.g.frames(1)
            for k in ks: self.g.key(k, False)
            self.g.frames(3)

    def take_aim(self, x, z, yaw):
        """Stand at (x, z) facing yaw: turn there, then step back on to the spot behind the
        shield (which keeps him facing the same way)."""
        self.goto(x, z, near=0.2)
        self.aim(yaw)
        self.g.key('k', True)
        self.g.frames(4)
        self.goto(x, z, near=0.12)
        self.g.key('k', False)
        self.g.frames(4)

    def approach(self, x, z, yaw, run=2.5):
        """Walk the last bit to (x, z) going the way `yaw` faces, so he ends up facing it squarely."""
        dx, dz = -math.sin(math.radians(yaw)), -math.cos(math.radians(yaw))
        self.goto(x - dx * run, z - dz * run, near=0.25)
        self.goto(x, z, near=0.15)
        self.g.frames(10)
        self.aim(yaw)

    def use(self):
        self.g.press('space', 20)
        for i in range(30):
            self.advance_talk()
            self.g.frames(4)

    def push(self, yaw, times):
        dx, dz = -math.sin(math.radians(yaw)), -math.cos(math.radians(yaw))
        for i in range(int((40 * times + 20) / 3)):
            ks = self.step_keys(dx, dz)
            for k in ks: self.g.key(k, True)
            self.g.frames(3)
            for k in ks: self.g.key(k, False)
        self.g.frames(10)

    def block_near(self, x, z):
        from drive import parse
        best = None
        for f in self.g.find('Crust Block'):
            p = parse(self.g.cmd('var %d %d at' % f)[0])
            if isinstance(p, tuple) and (best is None or math.hypot(p[0] - x, p[2] - z) < math.hypot(best[0] - x, best[2] - z)):
                best = p
        return best

    def push_block(self, x, z, yaw, times):
        """Push the block nearest (x, z) `times` cells the way `yaw` faces: lining up behind it each time."""
        dx, dz = -math.sin(math.radians(yaw)), -math.cos(math.radians(yaw))
        for i in range(times):
            b = self.block_near(x, z)
            self.goto(b[0] - dx * 1.6, b[2] - dz * 1.6, near=0.2)
            self.face(yaw)
            ks = self.step_keys(dx, dz)
            for f in range(14):               # (until it slides: then let go, before he walks round it)
                for k in ks: self.g.key(k, True)
                self.g.frames(3)
                for k in ks: self.g.key(k, False)
                nb = self.block_near(b[0], b[2])
                if math.hypot(nb[0] - b[0], nb[2] - b[2]) > 0.2:
                    break
                ks = self.step_keys(dx, dz)
            self.g.frames(30)
            x, z = b[0] + dx * 1.6, b[2] + dz * 1.6

    def shoot(self, focus=False):
        """Fire a pea (trying again if he was busy - hurt, say - and no pea left the pouch)."""
        for tries in range(4):
            peas = self.g.var('Game', 'peas')[0]
            if focus:
                self.g.key('shift', True)
                self.g.frames(8)
            self.g.press('u', 30)
            if focus:
                self.g.key('shift', False)
            self.g.frames(20)
            if self.g.var('Game', 'peas')[0] < peas:
                return
            print('  (no shot: %s)' % self.g.var('Sprig', 'st'))

    def enemies(self, within=9.0):
        """[(scene, id, position)] of enemies still alive near Sprig."""
        me = self.at()
        out = []
        for name in ('Fuzzball', 'Scrub'):
            for f in self.g.find(name):
                v = self.g.cmd('var %d %d at dead' % f)
                if len(v) < 2 or v[1] == 'true':
                    continue
                from drive import parse
                p = parse(v[0])
                if isinstance(p, tuple) and math.hypot(p[0] - me[0], p[2] - me[2]) < within and abs(p[1] - me[1]) < 1.5:
                    out.append((f, p))
        return out

    def fight(self, within=9.0, rounds=40):
        """Beat the enemies near him: walk up, focus, swing."""
        for i in range(rounds):
            es = self.enemies(within)
            if not es:
                return
            me = self.at()
            f, p = min(es, key=lambda e: math.hypot(e[1][0] - me[0], e[1][2] - me[2]))
            d = math.hypot(p[0] - me[0], p[2] - me[2])
            if d > 1.4:
                ks = self.step_keys((p[0] - me[0]) / d, (p[2] - me[2]) / d)
                for k in ks: self.g.key(k, True)
                self.g.frames(6)
                for k in ks: self.g.key(k, False)
                continue
            self.g.key('shift', True)
            self.g.frames(3)
            for j in range(3):
                self.g.press('j', 8)
            self.g.key('shift', False)
            self.g.frames(4)
            self.advance_talk()

    def wait(self, n):
        self.g.frames(n)

    def need(self, cond, what):
        if not cond:
            self.fail(what)
        print('ok  ', what)


def main():
    r = Run()
    g = r.g
    # ---- the Crate Room: a block on the switch, the key behind the bars
    r.goto(0, 10)
    r.fight()
    r.goto(6, 1); r.goto(12, 0); r.goto(15.5, 0.6)
    r.shot('crate_room')
    r.fight(12)
    r.need(r.g.var('Chest', 'shown') is not None, 'the fuzzballs beaten')
    r.goto(24.0, -2.9)
    r.face(0)
    r.use()
    r.need(r.flag('crock_map'), 'the DUNGEON MAP, once the fuzzballs are beaten')
    r.goto(20.0, 1.0)
    r.push_block(18.6, -0.8, 0, 3)
    r.need(r.flag('crock_sw_crate'), 'the block pushed on to the switch: the bars open')
    r.goto(22, 3.0); r.goto(27.0, 3.0)
    r.face(270)
    r.use()
    r.need(r.flag('crock_key1'), 'the first small key')
    # ---- the Proofing Room
    r.goto(20, 1); r.goto(12, 0); r.goto(0, 1); r.goto(-9.0, 0)
    r.face(90)
    r.use()
    r.need(r.flag('door:crock_proof'), 'the locked door to the Proofing Room')
    r.goto(-14.5, 1.0)
    r.fight()
    r.goto(-16.2, 2.0)
    r.shot('proof_room')
    for (x, wait) in [(-18.0, 100), (-20.0, 100), (-22.0, 80)]:
        r.goto(x, 2.0, near=0.3)
        r.wait(wait)
    r.goto(-24.5, 2.0)
    r.need(r.at()[1] > 3.9, 'up the warm columns to the ledge')
    r.face(90)
    r.use()
    r.need('shooter' in g.var('Game', 'items')[0], 'the Pea Shooter')
    r.shot('shooter')
    r.goto(-20.0, 2.0); r.goto(-18.0, 2.0); r.goto(-15, 0.5); r.goto(-9, 0); r.goto(0, -1.5)
    # ---- the eye under the balcony
    r.face(0)
    r.shoot(focus=True)
    r.need(r.flag('crock_eye'), 'a pea in the eye: the Furnace Room bars open')
    # ---- the hall's web, burnt by a pea through the torch in front of it
    r.take_aim(7.5, 2.0, 0)
    r.shoot()
    r.need(r.flag('crock_web_hall'), 'a fire pea burns the web in front of the warm column')
    # ---- the Furnace Room: fire peas to the bowls, the cold columns rise
    r.goto(0, -6); r.goto(0, -13); r.goto(0, -16.0)
    r.shot('furnace')
    r.fight()
    for (x, f) in [(-5.5, 'crock_bowl_w'), (5.5, 'crock_bowl_e')]:
        r.take_aim(x, -16.3, 0)
        r.shoot()
        r.need(r.flag(f), 'a fire pea lights the bowl (%s)' % f)
    r.wait(150)
    r.goto(0, -18.5); r.goto(0, -22); r.goto(0, -26.5)
    r.need(r.at()[2] < -25, 'across the risen columns')
    r.goto(-6.5, -28.4)
    r.face(0)
    r.use()
    r.need(r.flag('crock_compass'), 'the COMPASS')
    r.take_aim(2.0, -29.5, 270)
    r.shoot()
    r.need(r.flag('crock_web_key'), 'a fire pea burns the web over the second key')
    r.goto(8.0, -29.5)
    r.face(270)
    r.use()
    r.need(r.flag('crock_key2'), 'the second small key')
    # ---- up the warm column to the balcony
    r.goto(0, -26.5); r.goto(0, -22); r.goto(0, -18); r.goto(0, -13); r.goto(0, -4); r.goto(7.5, -2.5)
    r.goto(7.5, -5.0, near=0.25)
    r.wait(150)
    r.goto(7.5, -8.0)
    r.need(r.at()[1] > 3.9, 'up the warm column on to the balcony')
    r.shot('balcony')
    r.goto(0, -10.0)
    r.face(0)
    r.use()
    r.need(r.flag('door:crock_bk'), 'the locked door to the Boss Key room')
    # ---- two blocks, two switches
    r.goto(0, -14)
    r.push_block(-2.4, -16.4, 0, 3)
    r.need(r.flag('crock_sw_a'), 'the first block on its switch')
    r.goto(-0.6, -17.0)
    r.push_block(0.8, -19.6, 270, 2)
    r.need(r.flag('crock_bk_gate'), 'the second block on its switch: the gate opens')
    r.goto(1.2, -18.0); r.goto(0, -23.4)
    r.face(0)
    r.use()
    r.need('bosskey_crock' in g.var('Game', 'items')[0], 'the BOSS KEY')
    # ---- the big door, and down
    r.goto(0, -14); r.goto(0, -10.5); r.goto(-6, -10); r.goto(-8.6, -10)
    r.face(90)
    r.use()
    r.need(r.flag('door:crock_boss_door'), 'the boss door')
    r.goto(-14, -10); r.goto(-19, -10, near=0.6, limit=900)
    r.wait(120)
    r.advance_talk()
    r.need(r.at()[1] < -11, 'down the shaft into the lair')
    r.shot('lair')
    # ---- Queen Mildewmite: a pea in her eye when it glows, then the spoon while she's down
    from drive import parse
    q = g.find('Queen')[-1]
    for i in range(900):
        v = g.cmd('var %d %d st glow hp' % q)
        if len(v) < 3:
            break
        st, glow, hp = v[0], float(v[1]), float(v[2])
        if r.flag('crock_boss') or st == 'dead':
            break
        r.advance_talk()
        g.key('shift', True)
        if glow > 0 and st in ('ceiling', 'hunt', 'charge'):
            g.key('shift', False); g.frames(1); g.key('shift', True); g.frames(3)
            g.press('u', 4)
        elif st == 'stunned':
            g.press('j', 6)
            g.key('w', True); g.frames(4); g.key('w', False)
        else:
            g.frames(6)
        if i % 60 == 0:
            print('  queen', st, 'hp', hp, '| sprig hearts', g.var('Game', 'hp')[0])
    g.key('shift', False)
    g.frames(200)
    r.advance_talk()
    r.need(r.flag('crock_boss'), 'Queen Mildewmite beaten')
    print('the Great Crock: all the way through. errors:', g.errors)


if __name__ == '__main__':
    main()
