"""

Provide a sudo random default dict of colors 
 
It pics a new color for each lookup that is not already in the colorpicker
"""
from itertools import cycle
from clyent import color

class ColorPicker(object):
    """
    defaultdict like object that populates each new lookup with a color
    """
    light_fg_colors = ['yello', 'white']
    light_bg_colors = [43, 46, 47, 103, 107]
    dark_fg_colors = ['blue', 'red', 'green', 30]
    dark_bg_colors = [40, 41, 42, 44, 45, 100, 102, 104, 105, 106]

    def next_color(self):
        yield color(None, (6,))
        yield color(None, (7,))

        for fg in self.light_fg_colors:
            for bg in self.dark_bg_colors:
                yield color(None, (fg, bg))

        for fg in self.dark_fg_colors:
            for bg in self.light_bg_colors:
                yield color(None, (fg, bg))

    def __init__(self):
        self.color_map = {}
        self.color_iter = iter(cycle(self.next_color()))

    def __getitem__(self, name):
        if name not in self.color_map:
            self.color_map[name] = next(self.color_iter)

        return self.color_map[name]


