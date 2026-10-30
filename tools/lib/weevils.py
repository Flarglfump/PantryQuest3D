"""Where the Golden Weevils are: for each area scene, (spawn point, dx, dz, only at night).

Each floats about a metre up, a few steps from a spawn point. 32 in all; the Weevil House
in Peppermill rewards 10, 20 and 30.
"""
WEEVILS = {
    'sprouthollow': [('start', 3, -2, False), ('fields', -3, -2, False)],
    'fields': [('sprouthollow', 6, -8, True), ('town', -6, 6, True), ('gorge', 4, 5, True), ('peppermill', -5, 4, True)],
    'town': [('start', 6, -4, False), ('castle', -4, 3, False)],
    'castle': [('start', 3, -3, False)],
    'peppermill': [('fields', 4, -3, False), ('fondue', -3, 4, True)],
    'fondue': [('start', 2.5, -3, False), ('city', 1.5, 2.5, False)],
    'hardtack': [('start', 3, -1, False)],
    'gorge': [('fields', -2, -4, False), ('falls', 2, 2.5, False), ('lake', 3, -3, False)],
    'fizzdomain': [('start', 4, -3, False)],
    'lake': [('gorge', 4, 3, True), ('island', 2, -1.5, False)],
    'fields_risen': [('thicket', -6, 4, True), ('dairy', -4, -5, True)],
    'town_risen': [('temple', -3, 3, False)],
    'peppermill_risen': [('graveyard', 3, -2, True)],
    'thicket_risen': [('glade', 3, 3, False), ('start', 4, 2, False)],
    'fondue_risen': [('forge', -2, 3, False)],
    'fountain_risen': [('start', 3, -4, False)],
    'dairy': [('start', 5, -4, False)],
    'flats': [('start', -6, 2, False)],
    'idol': [('requiem', 4, 3, False)],
}
