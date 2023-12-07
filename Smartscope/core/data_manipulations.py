
from typing import List, Optional
import logging
import random
from Smartscope.lib.image.target import Target
from smartscope_connector.Datatypes.querylist import QueryList
from smartscope_connector import models

logger = logging.getLogger(__name__)

def create_target(target:models.target.Target, model:models.target.Target, finder:str, classifier:Optional[str]=None, start_number:int=0, **extra_fields):
    target_dict = target.to_dict()
    context = dict(number=start_number)
    context['finders'] = [models.target_label.Finder.model_validate(target_dict | dict(method_name=finder))]
    if classifier is not None:
        context['classifiers'] = [models.target_label.Classifier(method_name=classifier,label=target.quality)]
    data = target_dict | context | extra_fields
    obj = model.model_validate(data)
    return obj

def add_targets(targets:List[Target], model:Target, finder:str, classifier:Optional[str]=None, start_number:int=0, **extra_fields):
    output = []
    for ind, target in enumerate(targets):
        number = ind + start_number
        output.append(create_target(target, model, finder, classifier, number, **extra_fields))
    return QueryList(output)

def select_n_areas(parent, n, is_bis=False):
    filter_fields = dict(selected=False, status=None)
    if is_bis:
        filter_fields['bis_type'] = 'center'
    targets = parent.targets.filter(**filter_fields)

    if n <= 0:
        for t in targets:
            if t.is_good() and not t.is_excluded()[0]:
                pass
                # update(t, selected=True, status='queued')
        return

    clusters = dict()
    for t in targets:
        if not t.is_good():
            continue
        excluded, label = t.is_excluded()
        if excluded:
            continue
        try:
            clusters[label].append(t)
        except:
            clusters[label] = [t]

    if len(clusters) > 0:
        randomized_sample = clusters if n == len(clusters) else random.sample(list(clusters), n) if n < len(clusters) else [
            random.choice(list(clusters)) for i in range(n)]

        for choice in randomized_sample:
            sele = random.choice(clusters[choice])
            logger.debug(f'Selecting {sele.name} from cluster {choice}')
            # update(sele, selected=True, status='queued')
    else:
        logger.info('All targets are rejected, skipping')