"""The title screen: Sprouthollow's scenery (taken from areas/sprouthollow.scene, without
its people, scripts or colliders), a camera drifting round it, and the menu (title.bs)."""
import os

from kit import Scene, t3, t2, script, light, path


def build():
    src = open(path('areas', 'sprouthollow.scene')).read().split('\n\nentity\n')
    keep = []
    for block in src[1:]:
        if 'Script' in block or 'Light' in block or 'Camera3D' in block or 'Mesh' not in block:
            continue
        lines = [l for l in block.split('\n')]
        out, skip = [], False
        for l in lines:
            if l.startswith('  ') and not l.startswith('    '):
                skip = l.strip() in ('Collider3D', 'RigidBody3D', 'Tags', 'Parent')
            if not skip:
                out.append(l)
        keep.append('\n'.join(out).rstrip())
    s = Scene('The title screen of Pantry Quest 3D.\nMade by tools/areas/title.py (from areas/sprouthollow.scene).')
    s.entity('Sun', t3((0, 30, 0), (-55, -35, 0)), light('directional', '#fff2dcff', 0.95, shadows=False))
    s.entity('Sky Light', t3((0, 30, 0)), light('ambient', '#8898b8ff', 0.55))
    s.entity('Camera', t3((0, 8, 30)), ('Camera3D', [('fov', 60), ('near_clip', 0.2), ('far_clip', 70), ('clear_color', '#b8e0f0ff'),
                                                   ('fog', True), ('fog_color', '#c8e8d8ff'), ('fog_start', 30), ('fog_end', 68)]),
             script('scripts/titlecam.bs'))
    s.entity('Title', t2(), script('scripts/title.bs'))
    text = '\n'.join(s.lines) + '\n' + '\n\n'.join('entity\n' + b for b in keep) + '\n'
    with open(path('title.scene'), 'w') as f:
        f.write(text)
    print('  title: %d scenery entities' % len(keep))
