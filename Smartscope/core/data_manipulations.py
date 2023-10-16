
from typing import List, Optional
from Smartscope.lib.image.target import Target
from Smartscope.lib.Datatypes.querylist import QueryList
from . import models

def create_target(target:models.target.Target, model:models.target.Target, finder:str, classifier:Optional[str]=None, start_number:int=0, **extra_fields):
    target_dict = target.to_dict()
    context = dict(number=start_number)
    context['finders'] = [models.target_label.Finder.model_validate(target_dict | dict(method_name=finder))]
    if classifier is not None:
        context['classifiers'] = [models.target_label.Classifier(method_name=classifier,label=target.quality)]
    # context['targets'] = []
    # context['selectors'] = []
    # context['name'] = ''
    data = target_dict | context | extra_fields
    obj = model.model_validate(data)
    return obj

def add_targets(targets:List[Target], model:Target, finder:str, classifier:Optional[str]=None, start_number:int=0, **extra_fields):
    output = []
    for ind, target in enumerate(targets):
        number = ind + start_number
        output.append(create_target(target, model, finder, classifier, number, **extra_fields))
    return QueryList(output)