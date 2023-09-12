import unittest
from Smartscope.core.api_interface.rest_api_interface import get_from_API

# def test_api_connection():
#     response = get_from_API()
#     print(response)
#     assert response.status_code == 200

def test_api_connection():
    response = get_from_API(url='http://nginx:80/api/')
    assert response.status_code == 200

# def test_get_from_API():
#     response = get_from_API('microscopes', dict(name='fake_scope'))
#     print(response)
#     assert len(response) == 1