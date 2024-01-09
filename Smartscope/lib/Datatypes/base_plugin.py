
import importlib
from enum import Enum
from abc import ABC, abstractclassmethod
from typing import Any, Optional, Protocol, List, Dict, Union, Callable
import numpy as np
from matplotlib import cm
from matplotlib.colors import rgb2hex
from math import floor
from pydantic import BaseModel, Field
from Smartscope.lib.image.montage import Montage
from Smartscope.lib.image.targets import Targets

import logging
import sys

logger = logging.getLogger(__name__)


class TargetClass(Enum):
    FINDER = 'Finder'
    CLASSIFIER = 'Classifier'
    SELECTOR = 'Selector'
    METADATA = 'Metadata'


class classLabel(BaseModel):
    value: int
    name: str
    color: str


class FeatureAnalyzer(Protocol):
    description: Optional[str]
    kwargs: Optional[dict]


class BaseFeatureAnalyzer(BaseModel, ABC):
    name: str
    description: Optional[str] = ''
    reference: Optional[str]= ''
    method: Optional[str] = ''
    module: Optional[str] = ''
    kwargs: Optional[Dict[str, Any]] = Field(default_factory=dict)
    importPaths: Union[str,List] = Field(default_factory=list)

    @property
    def is_classifer(self) -> bool:
        """Check wheter this class is a classifier"""
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        [sys.path.insert(0, path) for path in self.importPaths]


    def run(self,
            montage:Montage,
            create_targets_method:Callable=Targets.create_targets_from_box,
            *args, **kwargs):
        """Where the main logic for the algorithm is"""
        module = importlib.import_module(self.module)
        function = getattr(module, self.method)
        output = function(montage,*args, **kwargs, **self.kwargs)
        targets = create_targets_method(output[0],montage)

        return targets, output[1],output[2]


class Finder(BaseFeatureAnalyzer):
    target_class: str = TargetClass.FINDER

    @property
    def is_classifier(self):
        return False


class Classifier(BaseFeatureAnalyzer):
    classes: Dict[(str, classLabel)]
    target_class: str = TargetClass.CLASSIFIER

    @property
    def is_classifier(self):
        return True

    def get_label(self, label):
        return self.classes[label].color, self.classes[label].name, ''


class Finder_Classifier(Classifier):
    target_class:str = TargetClass.CLASSIFIER


class Selector(BaseFeatureAnalyzer):
    clusters: Dict[(str, Any)] = Field(default_factory=dict)
    exclude: List[str] = Field(default_factory=list)
    target_class: str = TargetClass.SELECTOR
    kwargs: Dict[str, Any] = Field(default_factory=dict)
    limits: List[float] = [0.0,1.0]

    ###Legacy stuff v0.9.2 or earlier####
    def get_label(self, label):
        return self.clusters['colors'][int(label)], int(label), 'Cluster'
    
    def get_labels(self, targets):
        return [self.get_label(target.label) for target in targets]
    ### end legacy stuff ####

    def run(self, *args, **kwargs):
        """Where the main logic for the algorithm is"""
        module = importlib.import_module(self.module)
        function = getattr(module, self.method)
        output = function(*args, **kwargs, **self.kwargs)

        return output


class SelectorSorter:
    _limits = None
    _classes:List = None
    _labels:List = None
    _colors:List = None
    _values:List = None
    _from_server = False

    def __init__(self,selector:Selector, targets, n_classes=5, limits=None, from_server=False):
        self._selector: Selector = selector
        self._targets = targets
        self._n_classes = n_classes
        self._from_server = from_server
        # self.set_limits()

    def __getitem__(self, index):
        return self._targets[index], *self.labels[index]

    @property
    def classes(self):
        if self._classes is None:
            self.calculate_classes()
        return self._classes
    
    @property
    def labels(self):
        if self._labels is None:
            self.set_labels()
        return self._labels
    
    @property
    def limits(self):
        if self._limits is None:
            self.set_limits()
        return self._limits
    
    @property
    def colors(self):
        if self._colors is None:
            self.set_colors()
        return self._colors
    
    @property
    def values(self):
        if self._values is None:
            self.extract_values()
        return self._values
    
    @limits.setter
    def limits(self, value:List[float]):
        self._limits = value

    def set_limits(self):
        range_ = max(self.values) - min(self.values)
        self._limits = np.array(self._selector.limits) * range_ + min(self.values)

    def set_labels(self):
        logger.debug(f'Getting colored classes from selector {self._selector.name}. Inputs {len(self._targets)} targets and {self._n_classes} with {self.limits}.')
        # classes, limits = self.classes(self._targets, n_classes=n_classes, limits=limits)
        colors = self.set_colors(self._n_classes)
        logger.debug(f'Colors are {colors}')
        colored_classes = list(map(lambda x: (colors[x], x, 'Cluster'), self.classes))
        logger.debug(f'Colored classes are {colored_classes}')
        self._labels = colored_classes
        return colored_classes
        

    def calculate_classes(self):
        # logger.debug(f'Getting classes from selector {self._selector.name}. Inputs {len(self._targets)} targets and {self._n_classes} with limits {self.limits}.')
        map_in_bounds = self.included_in_limits()
        step = np.floor(np.diff(self.limits) / (self._n_classes -1))
        
        # for value, in_bounds in zip(values, map_in_bounds):
        def get_class(value, in_bounds) -> int:
            if not in_bounds:
                return 0
            return int(np.floor((value - self.limits[0]) / step) + 1)
        
        self._classes = list(map(get_class, self.values, map_in_bounds))
        logger.debug(f'Classes are {self._classes}')
        return self._classes

    def draw(self, n_classes=5, limits=None):
        pass

    def get_selector_value(self,target):
        if self._from_server:
            return self.get_selector_value_from_server(target)
        return self.get_selector_value_from_worker(target)

    def get_selector_value_from_worker(self,target):
        return next(filter(lambda x: x.method_name == self._selector.name ,target.selectors)).value
    
    def get_selector_value_from_server(self,target):
        return target.selectors.filter(method_name=self._selector.name).first().value
    
    def extract_values(self):
        self._values = list(map(self.get_selector_value,self._targets))

    def included_in_limits(self):
        if self.limits is None:
            self.set_limits()
        def selector_value_within_limits(target_value):
            # logger.debug(f'Checking if {target_value} is within {self.limits}')
            return self.limits[0] <= target_value <= self.limits[1]

        selector_value_within_limits = map(selector_value_within_limits,self.values)
        return list(selector_value_within_limits)

    def set_colors(self, n_classes: float):
        colors = list()
        cmap = cm.plasma
        cmap_step = int(floor(cmap.N / n_classes))
        for c in range(cmap.N, 0, -cmap_step):
            colors.append(rgb2hex(cmap(c)))
            continue
            prefix = ''
            val = v * self.step
            if val == self.range[0]:
                prefix = '\u2264'
            if val == self.range[1]:
                prefix = '\u2265'
            # print(f'From CTF {prefix}{v*self.step}, color is {rgb2hex(cmap(c))}')
            colors.append((rgb2hex(cmap(c)), v * self.step, prefix))

        # self._colors = colors
        return colors

class ImagingProtocol(BaseModel):
    squareFinders: List[str]
    holeFinders: List[str]
    highmagFinders: List[str] = Field(default_factory=list)
    squareSelectors: List[str]
    holeSelectors: List[str]
    
