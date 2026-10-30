"""Building blocks for Pantry Quest 3D's areas: the entities every area has (the Game,
the camera, Sprig, Flicker, the HUD, lights), static level geometry (merged into chunks,
one mesh collider each) and the props people, enemies and treasure.

An area script makes an Area, adds geometry and things, and saves it:

    a = Area('sprouthollow', 'Sprouthollow', music='music/sprouthollow.wav')
    a.geo('grass').ground(...)          # level geometry, by material
    a.tree(4, 0, 6)
    a.save()
"""
import math
import os

from kit import (Scene, Obj, Chunked, t3, t2, mesh, collider, kinematic, tags, script, particles, light, q, path)

MATERIALS = {
    # material: (texture, colour, solid, cast shadows, lit, cull)
    'grass': ('art/grass.png', '#ffffffff', True, False, True, True),
    'flowers': ('art/flowers.png', '#ffffffff', True, False, True, True),
    'dirt': ('art/dirt.png', '#ffffffff', True, False, True, True),
    'cobble': ('art/cobble.png', '#ffffffff', True, False, True, True),
    'lava': ('art/lavacheese.png', '#ffffffff', False, False, False, True),
    'rock': ('art/stone.png', '#c8a080ff', True, False, True, True),
    'cliff': ('art/stone.png', '#c8d0b8ff', True, False, True, True),
    'stone': ('art/stone.png', '#ffffffff', True, True, True, True),
    'bark': ('art/bark.png', '#ffffffff', True, True, True, True),
    'planks': ('art/planks.png', '#ffffffff', True, True, True, True),
    'thatch': ('art/thatch.png', '#ffffffff', True, True, True, True),
    'leaves': ('art/leaves.png', '#ffffffff', True, True, True, True),
    'hedge': ('art/hedge.png', '#ffffffff', True, True, True, True),
    'canopy': ('art/leaves.png', '#b8d8a8ff', False, False, True, False),
    'water': ('art/water.png', '#ffffffc8', False, False, False, False),
    'flesh': ('art/flesh.png', '#ffffffff', True, False, True, True),
    'fizzrock': ('art/fizzrock.png', '#ffffffff', True, True, True, True),
    'sand': ('art/sand.png', '#ffffffff', True, False, True, True),
    'crock': ('art/crock.png', '#ffffffff', True, True, True, True),
    'dough': ('art/dough.png', '#ffffffff', True, False, True, True),
    'dough_wall': ('art/dough.png', '#e8d8c0ff', True, False, True, True),
    'crust': ('art/crust.png', '#ffffffff', True, True, True, True),
    'mould': ('art/mould.png', '#ffffffff', True, False, True, True),
    'rot': ('art/rot.png', '#ffffffff', True, False, True, True),
    'starter': ('art/dough.png', '#f0e0b8e0', False, False, True, False),
    'deco': ('art/planks.png', '#ffffffff', False, True, True, True),
    'ceiling': ('art/dough.png', '#a89878ff', True, False, True, True),
}


class Area:
    def __init__(self, id, name, music='', dungeon='', kill_y=-20.0, sky='#a8d8f0ff', fog=(22, 60), fog_color=None,
                 ambient=('#8090b0ff', 0.5), sun=('#fff2dcff', 0.95), sun_rot=(-55, -35, 0), shadows=False, chunk=24.0, variant='', hot=False):
        self.id, self.name = id, name
        self.file_id = id + ('_' + variant if variant else '')     # (the Risen era's version: areas/<id>_risen.scene)
        self.scene = Scene('%s - an area of Pantry Quest 3D.\nMade by tools/areas/%s.py: change that and run tools/make_all.py.' % (name, id))
        self.chunks = Chunked(chunk)
        self.kill_y = kill_y
        s = self.scene
        gk = dict(area=id, area_name=name, music=music, dungeon=dungeon, kill_y=kill_y)
        if hot:
            gk['hot'] = True
        s.entity('Game', t2(), script('scripts/game.bs', **gk))
        s.entity('Story', t2(), script('scripts/story.bs'))
        s.entity('Sun', t3((0, 30, 0), sun_rot), light('directional', sun[0], sun[1], shadows=shadows, shadow_range=14))
        s.entity('Sky Light', t3((0, 30, 0)), light('ambient', ambient[0], ambient[1]))
        fc = fog_color or sky
        s.entity('Camera', t3((0, 3, 6)),
                 ('Camera3D', [('fov', 62), ('near_clip', 0.15), ('far_clip', fog[1] + 2), ('clear_color', sky),
                               ('fog', True), ('fog_color', fc), ('fog_start', fog[0]), ('fog_end', fog[1])]),
                 script('scripts/camera.bs'))
        s.entity('Sprig', t3((0, 0.1, 0)), collider('capsule', (1, 1.1, 1), 0.28, offset=(0, 0.55, 0), friction=0),
                 kinematic(), tags('player'), script('scripts/sprig.bs'))
        s.entity('Flicker', t3((0, 1.5, 0), scale=0.16), mesh('sphere', '#9ad8ffff', lit=False, cast=False),
                 particles(rate=14, max=30, lifetime=0.5, lifetime_random=0.3, speed=0.4, spread=180, size_start=0.09,
                           size_end=0, color_start='#d0f0ffff', color_end='#60a0ff00', blend='add'),
                 script('scripts/flicker.bs'))
        s.entity('HUD', t2(), script('scripts/hud.bs'))

    # ---- level geometry ----
    def geo(self, material, x=0.0, z=0.0):
        """The Obj to add `material` geometry to, for the chunk around x, z."""
        return self.chunks.at(material, x, z)

    def save(self):
        n = 0
        tris = 0
        for (material, cx, cz), obj in self.chunks.items():
            if obj.empty():
                continue
            texture, color, solid, cast, lit, cull = MATERIALS[material]
            file = 'models/areas/%s/%s_%d_%d.obj' % (self.file_id, material, cx, cz)
            obj.save(file)
            comps = [t3((0, 0, 0)), mesh('model', color, texture, file=file, cast=cast, lit=lit, cull=cull)]
            if solid:
                comps.append(collider('mesh', friction=0.9))
            if material == 'canopy' or material == 'water':
                comps.append(tags('seethrough'))
            self.scene.entity('%s %d %d' % (material, cx, cz), *comps)
            n += 1
            tris += obj.tri_count()
        self.scene.save(os.path.join('areas', self.file_id + '.scene'))
        print('  %s: %d entities, %d level meshes, %d level triangles' % (self.file_id, self.scene.count, n, tris))

    # ---- things ----
    def spawn_point(self, name, x, y, z, yaw=0):
        self.scene.entity('spawn_' + name, t3((x, y, z), (0, yaw, 0)))

    def entity(self, name, *comps):
        return self.scene.entity(name, *comps)

    def tree(self, x, y, z, size=1.0, bonk_drop=''):
        """A round tree: a trunk (solid) and a ball of leaves. Rolling into it can shake down a drop."""
        h = 2.6 * size
        self.entity('Tree', t3((x, y + h / 2, z), (0, 0, 0), (0.6 * size, h, 0.6 * size)),
                    mesh('cylinder', '#ffffffff', 'art/bark.png', uv=(1, 2)),
                    collider('capsule', (1, 1, 1), 0.5), tags('tree'),
                    script('scripts/tree.bs', drop=bonk_drop))
        self.entity('Leaves', t3((x, y + h + 0.7 * size, z), (0, x * 37 % 360, 0), (2.6 * size, 2.0 * size, 2.6 * size)),
                    mesh('sphere', '#ffffffff', 'art/leaves.png', uv=(2, 2), shadow=True))

    def grass(self, x, y, z, drops=0.3):
        self.entity('Grass', t3((x, y, z), (0, (x * 53 + z * 17) % 360, 0), (0.55, 0.45, 0.55)),
                    mesh('cone', '#5aa848ff', cast=False),
                    collider('sphere', radius=0.6, trigger=True, offset=(0, 0.4, 0)),
                    script('scripts/cuttable.bs', kind='grass', drops=drops))

    def pot(self, x, y, z, fixed=''):
        kw = {'kind': 'pot', 'drops': 0.6}
        if fixed:
            kw['fixed'] = fixed
        self.entity('Pot', t3((x, y, z)), mesh('model', '#ffffffff', 'art/clay.png', file='models/pot.obj'),
                    collider('capsule', (1, 0.5, 1), 0.28, offset=(0, 0.25, 0)), script('scripts/cuttable.bs', **kw))

    def sign(self, x, y, z, yaw, say):
        self.entity('Sign', t3((x, y + 0.45, z), (0, yaw, 0), (0.1, 0.9, 0.1)), mesh('cube', '#ffffffff', 'art/planks.png'),
                    collider('box'))
        self.entity('Sign Board', t3((x, y + 0.85, z), (0, yaw, 0), (0.8, 0.5, 0.08)), mesh('cube', '#ffffffff', 'art/planks.png'),
                    collider('box'), tags('interact', 'focusable'), script('scripts/sign.bs', say=say))

    def npc(self, who, x, y, z, yaw=0, needs='', until='', reach=None, model=None):
        kw = {'who': who}
        if reach:
            kw['reach'] = reach
        if needs:
            kw['needs'] = needs
        if until:
            kw['until'] = until
        self.entity(who.capitalize(), t3((x, y, z), (0, yaw, 0)), mesh('model', file='models/%s.glb' % (model or who), shadow=True),
                    ('Animator', [('clip', q('idle')), ('speed', 1), ('loop', True), ('playing', True), ('blend', 0.2)]),
                    collider('capsule', (1, 1.1, 1), 0.3, offset=(0, 0.55, 0)), tags('npc', 'interact', 'focusable'),
                    script('scripts/npc.bs', **kw))

    def chest(self, x, y, z, yaw, item, id, appear='', big=False):
        s = 1.4 if big else 1.0
        kw = {'item': item, 'id': id}
        if appear:
            kw['appear'] = appear
        i = self.entity('Chest', t3((x, y, z), (0, yaw, 0), s), mesh('model', '#ffffffff', 'art/chest.png', file='models/chest_base.obj'),
                        collider('box', (1, 1.3, 0.7), offset=(0, 0.65, 0)), tags('chest', 'interact'),
                        script('scripts/chest.bs', **kw))
        self.entity('Lid', t3((0, 0.55, 0.35)), mesh('model', '#ffffffff', 'art/chest.png', file='models/chest_lid.obj'),
                    ('Parent', [('entity', i)]))

    def enemy(self, brain, x, y, z, yaw=0, hp=2, damage=2, group='', model=None, **more):
        model = model or {'fuzzball': 'fuzzball', 'larva': 'larva', 'scrub': 'scrub', 'stalebie': 'stalebie', 'crustling': 'crustling', 'roller': 'hardtack_kid', 'jelly': 'jelly'}[brain]
        kw = {'brain': brain, 'hp': hp, 'damage': damage}
        if group:
            kw['group'] = group
        kw.update(more)
        r, h = {'fuzzball': (0.35, 0.7), 'larva': (0.25, 0.5), 'scrub': (0.3, 0.7), 'stalebie': (0.32, 1.3), 'crustling': (0.4, 0.8), 'roller': (0.45, 1.0), 'jelly': (0.4, 0.8)}[brain]
        self.entity(brain.capitalize(), t3((x, y, z), (0, yaw, 0)), mesh('model', file='models/%s.glb' % model, shadow=True),
                    ('Animator', [('clip', q('idle')), ('speed', 1), ('loop', True), ('playing', True), ('blend', 0.1)]),
                    collider('capsule', (1, h, 1), r, offset=(0, h / 2, 0)), kinematic(),
                    tags('enemy', 'focusable'), script('scripts/enemy.bs', **kw))
        if brain == 'scrub':     # its bush
            self.entity('Scrub Bush', t3((x, y + 0.15, z), (0, 0, 0), (1.0, 0.45, 1.0)), mesh('sphere', '#ffffffff', 'art/hedge.png'))

    def bombflower(self, x, y, z):
        i = self.entity('Bomb Flower', t3((x, y, z)), mesh('model', '#4a9a3aff', file='models/bombflower.obj', cull=False),
                        tags('interact', 'focusable'), script('scripts/bombflower.bs'))
        self.entity('Bud', t3((0, 0.05, 0)), mesh('model', '#fff4d0ff', file='models/bomb.obj'), ('Parent', [('entity', i)]))

    def cracked(self, x, y, z, w, h, d, id, yaw=0, boulder=False):
        """A cracked wall (or a boulder) a bomb can break."""
        if boulder:
            self.entity('Boulder', t3((x, y + h / 2, z), (0, yaw, 0), (w, h, d)), mesh('sphere', '#c8b8a0ff', 'art/stone.png'),
                        collider('sphere', radius=0.5), tags('bombable', 'focusable'), script('scripts/bombable.bs', id=id, size_r=max(w, d) / 2))
        else:
            self.entity('Cracked Wall', t3((x, y + h / 2, z), (0, yaw, 0), (w, h, d)), mesh('cube', '#b8a890ff', 'art/crack.png', uv=(w / 2, h / 2)),
                        collider('box'), tags('bombable'), script('scripts/bombable.bs', id=id, size_r=max(w, d) / 2))

    def dummy(self, x, y, z, yaw=0):
        self.entity('Dummy', t3((x, y, z), (0, yaw, 0)), mesh('model', '#ffffffff', 'art/sack.png', file='models/dummy.obj'),
                    collider('capsule', (1, 1.4, 1), 0.3, offset=(0, 0.7, 0)), tags('enemy', 'focusable'),
                    script('scripts/enemy.bs', brain='dummy', hp=99))

    def loadzone(self, x, y, z, w, h, d, to='', at='start', say='', needs='', yaw=0, until=''):
        kw = {'to': to, 'at': at}
        if until:
            kw['until'] = until
        if say:
            kw['say'] = say
        if needs:
            kw['needs'] = needs
        self.entity('Load Zone', t3((x, y + h / 2, z), (0, yaw, 0)), collider('box', (w, h, d), trigger=True),
                    tags('loadzone'), script('scripts/loadzone.bs', **kw))

    def vine(self, x, y, z, width, height, out_yaw, top=None):
        """A climbable wall of vines on a wall facing out_yaw (degrees: 0 faces -z... the
        way something with rotation y = out_yaw looks). The vines are drawn; the trigger
        sits just in front."""
        fx, fz = -math.sin(math.radians(out_yaw)), -math.cos(math.radians(out_yaw))
        top = y + height if top is None else top
        self.entity('Vines', t3((x + fx * 0.05, y + height / 2, z + fz * 0.05), (0, out_yaw, 0), (width, height, 0.05)),
                    mesh('cube', '#7ac060ff', 'art/leaves.png', uv=(width, height)))
        self.entity('Vine Climb', t3((x + fx * 0.45, y + height / 2, z + fz * 0.45), (0, out_yaw, 0)),
                    collider('box', (width, height + 0.6, 0.7), trigger=True), tags('climbable'),
                    script('scripts/vine.bs', out=(round(fx, 4), 0, round(fz, 4)), top=top, bottom=y))

    def pickup(self, kind, x, y, z, id=''):
        kw = {'kind': kind}
        if id:
            kw['id'] = id
        files = {'heart': ('models/heart.obj', '#ff3048ff'), 'bean1': ('models/bean.obj', '#40e060ff'),
                 'bean5': ('models/bean.obj', '#4080ffff'), 'bean20': ('models/bean.obj', '#ff4040ff'),
                 'key': ('models/key.obj', '#f0c850ff')}
        f, c = files[kind]
        self.entity('Pickup', t3((x, y, z)), mesh('model', c, file=f, lit=False, cast=False, shadow=True), script('scripts/pickup.bs', **kw))

    def blocker(self, x, y, z, size, until, material='planks', yaw=0, color='#ffffffff'):
        tex = {'planks': 'art/planks.png', 'web': 'art/web.png', 'hedge': 'art/hedge.png'}[material]
        self.entity('Blocker', t3((x, y + size[1] / 2, z), (0, yaw, 0), size), mesh('cube', color, tex, uv=(size[0], size[1]), cull=material != 'web'),
                    collider('box'), script('scripts/blocker.bs', until=until))

    def water(self, x0, z0, x1, z1, surface, depth=3.0, round_=False):
        """A body of water: the surface drawn, a trigger under it (sprig.bs swims in it).
        The ground under it is the area's job. round_: a disc inscribed in the rectangle."""
        cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
        if round_:
            self.geo('water', cx, cz).cylinder((cx, surface, cz), (x1 - x0) / 2, 0.0, 20, top=True, uvs=0.15)
        else:
            self.geo('water', cx, cz).quad((x0, surface, z1), (x1, surface, z1), (x1, surface, z0), (x0, surface, z0),
                                           (x0 / 4, z1 / 4), (x1 / 4, z1 / 4), (x1 / 4, z0 / 4), (x0 / 4, z0 / 4))
        self.entity('Water', t3((cx, surface - depth / 2, cz)), collider('box', (x1 - x0, depth, z1 - z0), trigger=True),
                    tags('water'), script('scripts/water.bs', surface=surface))

    def floorswitch(self, x, y, z, id):
        self.entity('Floor Switch', t3((x, y, z)), mesh('model', '#d8b040ff', file='models/switch.obj'),
                    script('scripts/floorswitch.bs', id=id))

    def switchdoor(self, x, y, z, size, when, stay=False, yaw=0, material='flesh', color='#c86070ff'):
        tex = {'flesh': 'art/flesh.png', 'planks': 'art/planks.png', 'stone': 'art/stone.png'}[material]
        kw = {'when': when}
        if stay:
            kw['stay'] = True
        self.entity('Switch Door', t3((x, y + size[1] / 2, z), (0, yaw, 0), size), mesh('cube', color, tex, uv=(size[0], size[1])),
                    collider('box'), ('RigidBody3D', [('type', 'kinematic')]), script('scripts/switchdoor.bs', **kw))

    def tendril(self, x, y, z, id, set_='', count=3):
        self.entity('Tendril', t3((x, y, z)), mesh('model', '#e8d0b0ff', file='models/tendril.obj'), collider('capsule', (1, 2.4, 1), 0.25, offset=(0, -1.2, 0)),
                    tags('focusable'), script('scripts/tendril.bs', id=id, set=set_, count=count))

    def target(self, x, y, z, yaw=0):
        """A wooden target the Licorice Lash bites into (on a post or a wall)."""
        self.entity('Lash Target', t3((x, y, z), (0, yaw, 0), (0.8, 0.8, 0.25)), mesh('cube', '#c89058ff', 'art/planks.png'),
                    collider('box'), tags('hookable', 'focusable'), script('scripts/target.bs'))
        self.entity('Bullseye', t3((x - math.sin(math.radians(yaw)) * 0.14, y, z - math.cos(math.radians(yaw)) * 0.14), (90, yaw, 0), (0.45, 0.02, 0.45)),
                    mesh('cylinder', '#d03030ff', lit=False))

    def hammerswitch(self, x, y, z, id):
        self.entity('Rusty Switch', t3((x, y, z)), mesh('model', '#a07050ff', file='models/switch.obj'), collider('box', (1.4, 0.3, 1.4), offset=(0, 0.0, 0)),
                    tags('focusable'), script('scripts/hammerswitch.bs', id=id))

    def point_light(self, x, y, z, color, intensity, range_):
        self.entity('Lamp', t3((x, y, z)), light('point', color, intensity, range=range_))


# ---- geometry helpers ----

def stump_house(a, x, z, ground, r=2.4, h=3.0, door_yaw=0, roof='thatch'):
    """A hollow-stump house: a bark cylinder, a cone roof, a door (a dark plank on the side
    facing door_yaw)."""
    y = ground(x, z) - 0.3
    a.geo('bark', x, z).cylinder((x, y, z), r, h + 0.3, 14, top=True, uvs=0.5)
    if roof:
        roof_on(a, x, z, y, r, h, roof)
    door(a, x, z, y, r, door_yaw)


def roof_on(a, x, z, y, r, h, roof):
    a.geo(roof, x, z).cylinder((x, y + h + 0.3, z), r + 0.6, 0.35, 14, top=False, radius_top=r + 0.4, uvs=0.5)
    a.geo(roof, x, z).cone((x, y + h + 0.65, z), r + 0.4, 2.0, 14, uvs=0.5)


def door(a, x, z, y, r, door_yaw):
    fx, fz = -math.sin(math.radians(door_yaw)), -math.cos(math.radians(door_yaw))
    dx, dz = x + fx * (r + 0.02), z + fz * (r + 0.02)
    a.entity('Door', t3((dx, y + 0.3 + 0.75, dz), (0, door_yaw, 0), (1.0, 1.5, 0.08)), mesh('cube', '#5a3a20ff', 'art/planks.png'))
    # a round window either side
    for side in (-1, 1):
        ang = math.radians(door_yaw + side * 55)
        wx, wz = x - math.sin(ang) * (r + 0.02), z - math.cos(ang) * (r + 0.02)
        a.entity('Window', t3((wx, y + 0.3 + 1.6, wz), (0, door_yaw + side * 55, 0), (0.55, 0.55, 0.06)),
                 mesh('cube', '#f8e8a0ff', lit=False, cast=False))


def box_wall(a, material, x0, z0, x1, z1, y0, y1, thick=0.6, uvs=0.5):
    """A straight wall from (x0, z0) to (x1, z1), from y0 up to y1."""
    dx, dz = x1 - x0, z1 - z0
    L = math.hypot(dx, dz)
    yaw = math.degrees(math.atan2(-dx, -dz))     # (the wall's length runs along its local -z)
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    a.geo(material, cx, cz).box((cx - thick / 2, y0, cz - L / 2), (cx + thick / 2, y1, cz + L / 2), uvs=uvs, rot_y=yaw, center=(cx, cz))


# ---- dungeon geometry: rooms are round, joined by square tunnels ----

def ring_floor(o, cx, cz, r0, r1, y, a0=0.0, a1=360.0, segs=24, thick=0.5, uvs=0.35, edges=True):
    """A flat ring (or disc, r0 = 0) at height y from angle a0 to a1 (degrees: 0 is +x, 90 is
    +z), with its edges as thick as `thick`."""
    n = max(1, int(segs * (a1 - a0) / 360.0 + 0.5))
    P = lambda r, a, yy: (cx + math.cos(math.radians(a)) * r, yy, cz + math.sin(math.radians(a)) * r)
    U = lambda p: (p[0] * uvs, p[2] * uvs)
    for i in range(n):
        aa, ab = a0 + (a1 - a0) * i / n, a0 + (a1 - a0) * (i + 1) / n
        # (seen from above, angle grows clockwise here: x right, z down)
        if r0 > 0:
            q = [P(r0, aa, y), P(r0, ab, y), P(r1, ab, y), P(r1, aa, y)]
            o.quad(q[0], q[1], q[2], q[3], U(q[0]), U(q[1]), U(q[2]), U(q[3]))
        else:
            c = (cx, y, cz)
            o.tri(c, P(r1, ab, y), P(r1, aa, y), U(c), U(P(r1, ab, y)), U(P(r1, aa, y)))
        if edges and thick > 0:
            lo = y - thick
            o.quad(P(r1, aa, lo), P(r1, aa, y), P(r1, ab, y), P(r1, ab, lo), (0, 0), (0, thick * uvs), (1, thick * uvs), (1, 0))
            if r0 > 0:
                o.quad(P(r0, ab, lo), P(r0, ab, y), P(r0, aa, y), P(r0, aa, lo), (0, 0), (0, thick * uvs), (1, thick * uvs), (1, 0))
            o.quad(P(r1, aa, lo), P(r1, ab, lo), P(r0 if r0 > 0 else 0.001, ab, lo), P(r0 if r0 > 0 else 0.001, aa, lo))
    if edges and thick > 0 and a1 - a0 < 360:
        for a in (a0, a1):
            p0, p1 = P(r0, a, y - thick), P(r1, a, y - thick)
            p2, p3 = P(r1, a, y), P(r0, a, y)
            if a == a0:
                o.quad(p0, p1, p2, p3)
            else:
                o.quad(p1, p0, p3, p2)


def ring_wall(o, cx, cz, r, y0, y1, segs=24, holes=(), uvs=0.3):
    """The inside wall of a round room, from y0 up to y1, facing in. holes: (angle,
    half-width in units, y bottom, y top) - doorways."""
    step = 360.0 / segs
    off = 0.0
    if holes:                     # (turned so the first doorway is in the middle of a segment)
        off = (holes[0][0] % step) - step / 2
    for i in range(segs):
        aa, ab = off + step * i, off + step * (i + 1)
        mid = (aa + ab) / 2
        spans = [(y0, y1)]
        for ha, hw, hy0, hy1 in holes:
            d = abs(((mid - ha + 180) % 360) - 180)
            if math.radians(d) * r < hw:
                new = []
                for s0, s1 in spans:
                    if hy0 > s0:
                        new.append((s0, min(s1, hy0)))
                    if hy1 < s1:
                        new.append((max(s0, hy1), s1))
                spans = new
        for s0, s1 in spans:
            if s1 - s0 < 0.01:
                continue
            P = lambda a, yy: (cx + math.cos(math.radians(a)) * r, yy, cz + math.sin(math.radians(a)) * r)
            u0, u1 = math.radians(aa) * r * uvs, math.radians(ab) * r * uvs
            # facing the middle
            o.quad(P(aa, s0), P(ab, s0), P(ab, s1), P(aa, s1), (u0, s0 * uvs), (u1, s0 * uvs), (u1, s1 * uvs), (u0, s1 * uvs))


def ceiling_disc(o, cx, cz, r, y, hole=0.0, segs=24, uvs=0.3):
    """A ceiling (facing down), with an optional hole in the middle."""
    P = lambda rr, a: (cx + math.cos(math.radians(a)) * rr, y, cz + math.sin(math.radians(a)) * rr)
    for i in range(segs):
        aa, ab = 360.0 * i / segs, 360.0 * (i + 1) / segs
        if hole > 0:
            o.quad(P(hole, ab), P(hole, aa), P(r, aa), P(r, ab))
        else:
            o.tri((cx, y, cz), P(r, aa), P(r, ab))


def tunnel(o_floor, o_wall, x0, z0, x1, z1, y, w=2.4, h=2.8, uvs=0.35, ceiling=True):
    """A straight square tunnel between two points (open at both ends), floor at y."""
    dx, dz = x1 - x0, z1 - z0
    L = math.hypot(dx, dz)
    ux, uz = dx / L, dz / L
    px, pz = -uz * w / 2, ux * w / 2
    A, B = (x0, z0), (x1, z1)
    def p(c, side, yy):
        return (c[0] + px * side, yy, c[1] + pz * side)
    # floor (facing up)
    q = [p(A, 1, y), p(B, 1, y), p(B, -1, y), p(A, -1, y)]
    if (q[1][0] - q[0][0]) * (q[2][2] - q[0][2]) - (q[1][2] - q[0][2]) * (q[2][0] - q[0][0]) > 0:
        q = q[::-1]
    o_floor.quad(*q, *[(v[0] * uvs, v[2] * uvs) for v in q])
    o_floor.box((min(x0, x1) - abs(px), y - 0.5, min(z0, z1) - abs(pz)), (max(x0, x1) + abs(px), y, max(z0, z1) + abs(pz)), sides=('ny',))
    # walls (facing in) and a ceiling (facing down)
    for side in (1, -1):
        w0, w1 = p(A, side, y), p(B, side, y)
        quad = [w0, w1, (w1[0], y + h, w1[2]), (w0[0], y + h, w0[2])]
        # face inwards: towards the middle line
        n = ((quad[1][1] - quad[0][1]) * (quad[2][2] - quad[0][2]) - (quad[1][2] - quad[0][2]) * (quad[2][1] - quad[0][1]),
             0, 0)
        e1 = [quad[1][i] - quad[0][i] for i in range(3)]
        e2 = [quad[2][i] - quad[0][i] for i in range(3)]
        nx = e1[1] * e2[2] - e1[2] * e2[1]
        nz = e1[0] * e2[1] - e1[1] * e2[0]
        if nx * (-px * side) + nz * (-pz * side) < 0:
            quad = quad[::-1]
        o_wall.quad(*quad, (0, 0), (L * uvs, 0), (L * uvs, h * uvs), (0, h * uvs))
    if ceiling:
        q = [p(A, 1, y + h), p(B, 1, y + h), p(B, -1, y + h), p(A, -1, y + h)]
        if (q[1][0] - q[0][0]) * (q[2][2] - q[0][2]) - (q[1][2] - q[0][2]) * (q[2][0] - q[0][0]) < 0:
            q = q[::-1]
        o_wall.quad(*q, *[(v[0] * uvs, v[2] * uvs) for v in q])


def town_house(a, x, z, w, d, h, ground_y, wall='planks', roof='thatch', door_side='s', roof_h=None):
    """A box house (w along x, d along z) with a pitched roof (ridge along x) and a door on
    one side ('n', 's', 'e', 'w')."""
    y = ground_y - 0.3
    x0, x1, z0, z1 = x - w / 2, x + w / 2, z - d / 2, z + d / 2
    a.geo(wall, x, z).box((x0, y, z0), (x1, y + h + 0.3, z1), uvs=0.4, sides=('px', 'nx', 'pz', 'nz'))
    rh = roof_h if roof_h else d * 0.45
    top = y + h + 0.3
    o = a.geo(roof, x, z)
    e = 0.4                      # the eaves
    A, B = (x0 - e, top - 0.2, z0 - e), (x1 + e, top - 0.2, z0 - e)
    C, D = (x1 + e, top - 0.2, z1 + e), (x0 - e, top - 0.2, z1 + e)
    R0, R1 = (x0 - e, top + rh, z), (x1 + e, top + rh, z)
    s = 0.35
    o.quad(A, R0, R1, B, (0, 0), (0, rh * s * 2), (w * s, rh * s * 2), (w * s, 0))          # north slope (faces -z, up)
    o.quad(C, R1, R0, D, (0, 0), (0, rh * s * 2), (w * s, rh * s * 2), (w * s, 0))          # south slope
    g = a.geo(wall, x, z)
    g.tri((x0, top, z0), (x0, top, z1), (x0, top + rh - 0.1, z))                              # gables
    g.tri((x1, top, z1), (x1, top, z0), (x1, top + rh - 0.1, z))
    door_at = {'s': (x, z1 + 0.03, 180), 'n': (x, z0 - 0.03, 0), 'e': (x1 + 0.03, z, -90), 'w': (x0 - 0.03, z, 90)}[door_side]
    a.entity('Door', t3((door_at[0], y + 0.3 + 0.9, door_at[1]), (0, door_at[2], 0), (1.1, 1.8, 0.08)), mesh('cube', '#5a3a20ff', 'art/planks.png'))
    for side in (-1, 1):
        if door_side in 'ns':
            wx, wz = x + side * w * 0.3, door_at[1]
        else:
            wx, wz = door_at[0], z + side * d * 0.3
        a.entity('Window', t3((wx, y + 0.3 + 1.6, wz), (0, door_at[2], 0), (0.7, 0.6, 0.06)), mesh('cube', '#f8e8a0ff', lit=False, cast=False))


def stall(a, x, z, ground_y, color, yaw=0):
    """A market stall: a counter and a striped awning."""
    y = ground_y
    a.entity('Stall', t3((x, y + 0.5, z), (0, yaw, 0), (2.6, 1.0, 0.9)), mesh('cube', '#ffffffff', 'art/planks.png'), collider('box'))
    a.entity('Awning', t3((x, y + 2.4, z + (0.4 if yaw == 0 else -0.4)), (-14 if yaw == 0 else 14, yaw, 0), (3.0, 0.1, 2.0)), mesh('cube', color, 'art/thatch.png'))
    for dx in (-1.3, 1.3):
        a.entity('Pole', t3((x + dx, y + 1.2, z), (0, 0, 0), (0.1, 2.4, 0.1)), mesh('cylinder', '#ffffffff', 'art/bark.png'))
