import pytest
from ..rest_api_interface import get_from_API, get_single, update, patch_single, generate_get_url, RequestUnsuccessfulError
from Smartscope.core.models import Microscope, Detector

def test_generate_get_url():
    url = generate_get_url(base_url='http://testurl/api', route='microscopes', filters=dict(name='fake_scope', microscope_id='h0PgRUjUq2K2Cr1CGZJq3q08il8i5n' ))
    assert url == 'http://testurl/api/microscopes/?name=fake_scope&microscope_id=h0PgRUjUq2K2Cr1CGZJq3q08il8i5n&'

def test_api_connection():
    response = get_from_API(url='http://nginx:80/api/')
    assert response.status_code == 200

def test_api_connection_error():
    with pytest.raises(RequestUnsuccessfulError):
        get_from_API(url='http://nginx:80/wrongapi/')

def test_get_from_API():
    import json
    response = get_from_API(url='http://nginx:80/api/microscopes/?name=fake_scope&')
    assert len(json.loads(response.content)['results']) == 1

def test_get_single():
    response = get_single(object_id='h0PgRUjUq2K2Cr1CGZJq3q08il8i5n',output_type=Microscope)
    assert isinstance(response, Microscope)
    assert response.name == 'fake_scope'
    assert response.uid == 'h0PgRUjUq2K2Cr1CGZJq3q08il8i5n'

def test_patch_single():
    object_id = '3'
    url = f'http://nginx:80/api/detectors/{object_id}/'
    data = dict(atlas_max_tiles_X= 7)
    response = patch_single(url=url,data=data)
    assert response.status_code == 200
    assert response.json()['atlas_max_tiles_X'] == 7
    #Reset Value
    data = dict(atlas_max_tiles_X= 6)
    response = patch_single(url=url,data=data)
    assert response.json()['atlas_max_tiles_X'] == 6

def test_update():
    object_id = '3'
    instance = get_single(object_id=object_id,output_type=Detector)
    instance = update(instance=instance, atlas_max_tiles_X=7)
    assert isinstance(instance,Detector)
    assert instance.atlas_max_tiles_X == 7
    instance = update(instance=instance, atlas_max_tiles_X=6)
    assert instance.atlas_max_tiles_X == 6

