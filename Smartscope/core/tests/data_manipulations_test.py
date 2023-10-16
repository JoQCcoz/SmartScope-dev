from ..data_manipulations import create_target, add_targets
from ..models import SquareModel
from Smartscope.lib.image.target import Target

def generate_target():
    target = Target(shape=[5,5,5,5],quality='bad')
    target.set_stage_coords(0,0,0)
    target.set_area_radius()
    return target

def test_create_target():
    target = generate_target()
    instance = create_target(target, SquareModel, 'test_finder', 'test_classifier', 10, atlas_id='1', grid_id='1')
    assert instance.finders[0].method_name == 'test_finder'
    assert instance.classifiers[0].method_name == 'test_classifier'
    assert instance.number == 10

def test_add_targets():
    targets = [generate_target() for _ in range(10)]
    instances = add_targets(targets, SquareModel, 'test_finder', 'test_classifier', 10, atlas_id='1', grid_id='1')
    assert len(instances) == 10
    assert instances[0].number == 10
    assert instances[9].number == 19
    assert instances[0].finders[0].method_name == 'test_finder'
    assert instances[0].classifiers[0].method_name == 'test_classifier'