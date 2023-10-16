from .. import models


def extract_targets(data):
    target_labels= []
    target_labels += [(item,models.Finder) for item in data.pop('finders',[])]
    target_labels += [(item,models.Classifier) for item in data.pop('classifiers',[])]
    target_labels += [(item,models.Selector) for item in data.pop('selectors',[])]
    targets = data.pop('targets',[])
    return target_labels, data, targets

def create_target_label_instances(target_labels,instance,content_type):
    target_labels_models = []
    for label,label_class in target_labels:
        target_labels_models.append(label_class(**label,object_id=instance,content_type=content_type))    
    return target_labels_models