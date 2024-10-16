from matplotlib import cm
from matplotlib.colors import rgb2hex
from math import floor
from typing import List, Dict, Any
from Smartscope.lib.Datatypes.base_plugin import BaseFeatureAnalyzer


class CTFFitViewer(BaseFeatureAnalyzer):
    name: str = 'CTF viewer'
    description: str = 'Color areas by their CTF resolution'
    range: List = [3, 10]
    step: float = 0.5
    colors: List = []
    # clusters:Dict[(str, Any)] = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.colors = self.get_colors()

    def get_colors(self):
        colors = list()
        steps = range(int(self.range[0] / self.step), int(self.range[1] / self.step) + 1)
        n_steps = len(steps)
        cmap = cm.plasma
        cmap_step = int(floor(cmap.N / n_steps))
        for c, v in zip(range(cmap.N, 0, -cmap_step), steps):
            prefix = ''
            val = v * self.step
            if val == self.range[0]:
                prefix = '\u2264'
            if val == self.range[1]:
                prefix = '\u2265'
            # print(f'From CTF {prefix}{v*self.step}, color is {rgb2hex(cmap(c))}')
            colors.append((rgb2hex(cmap(c)), v * self.step, prefix))

        return colors

    def get_label(self, label):
        # if label is None:
        #     return 'blue', 'target', ''
        if label > self.range[1]:
            label = self.range[1]
        if label < self.range[0]:
            label = self.range[0]

        label = floor((label - self.range[0]) / self.step)
        # print(label)
        return self.colors[label]
