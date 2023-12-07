import requests
import logging
from typing import Dict, List
from Smartscope.lib.Datatypes.querylist import QueryList
from Smartscope.core.models.base_model import SmartscopeBaseModel
from Smartscope.core.settings.worker import API_BASE_URL, API_KEY

from .decorators import parse_output

logger = logging.getLogger(__name__)

AUTH_HEADER={'Authorization':f'Token {API_KEY}'}

class RequestUnsuccessfulError(Exception):
   
    def __init__(self, response: requests.Response):
        self.response = response
        super().__init__(self.generate_message())
    
    def generate_message(self):
        message = f'Request made to\n\t{self.response.url}\nreturned a {self.response.status_code}, {self.response.reason}'
        return message

def add_trailing_slash(url:str):
    if url[-1] == '/':
        return url
    return url + '/'

def generate_get_url(base_url:str=API_BASE_URL,route:str='',filters:Dict=dict(),route_suffixes:List[str]=list()) -> str:
    url = f'{add_trailing_slash(base_url)}{route}/'
    url += '/'.join(route_suffixes)
    url = add_trailing_slash(url)
    if filters != dict():
        url += '?'

    for i,j in filters.items():
        url += f'{i}={j}&' 
    return url

def generate_get_single_url(object_id:str, base_url:str=API_BASE_URL, route:str='', route_suffix:str='') -> str:
    if route_suffix != '':
        route_suffix = f'{route_suffix}/'
    return f'{add_trailing_slash(base_url)}{route}/{route_suffix}{object_id}/'


def get_from_API(url, auth_header:Dict=AUTH_HEADER) -> requests.Response:
    response = requests.get(url,headers=auth_header)
    if response.status_code != 200:
        raise RequestUnsuccessfulError(response)
    return response

def patch_single(url,data,auth_header:Dict=AUTH_HEADER) -> requests.Response:
    response = requests.patch(url=url,data=data,headers=auth_header)
    if response.status_code != 200:
        raise RequestUnsuccessfulError(response)
    return response

def post(url, data, auth_header:Dict=AUTH_HEADER) -> requests.Response:
    response = requests.post(url=url,json=data,headers=auth_header)
    if response.status_code != 201:
        raise RequestUnsuccessfulError(response)    
    return response.json()

@parse_output
def get_single(object_id,output_type:SmartscopeBaseModel, auth_header:Dict=AUTH_HEADER) -> SmartscopeBaseModel:
    url = generate_get_single_url(object_id=object_id, route=output_type.api_route)
    response =  get_from_API(url, auth_header)
    return response.json()

@parse_output
def get_many(output_type:SmartscopeBaseModel, auth_header:Dict=AUTH_HEADER, **filters) -> QueryList[SmartscopeBaseModel]:
    url = generate_get_url(route=output_type.api_route,filters=filters)
    response =  get_from_API(url, auth_header)
    return response.json()



def update(instance:SmartscopeBaseModel, auth_header:Dict=AUTH_HEADER, route_suffix:str='', **fields) -> SmartscopeBaseModel:
    url = generate_get_single_url(instance.uid,route=instance.api_route, route_suffix=route_suffix)
    reponse = patch_single(url=url, data=fields,auth_header=auth_header)
    return instance.model_validate(reponse.json())

def post_single(instance:SmartscopeBaseModel, auth_header:Dict=AUTH_HEADER) -> SmartscopeBaseModel:
    url = generate_get_url(route=instance.api_route)
    response = post(url,data=instance.model_dump(exclude_unset=True),auth_header=auth_header)
    return instance.model_validate(response)

@parse_output
def post_many(instances: QueryList[SmartscopeBaseModel],output_type:SmartscopeBaseModel, auth_header:Dict=AUTH_HEADER, route_suffixes=['post_many'] ) -> QueryList[SmartscopeBaseModel]:
    url = generate_get_url(route=instances.first().api_route, route_suffixes=route_suffixes)
    response = post(url,data=instances.dump_all(),auth_header=auth_header)
    return response

def delete_single(instance:SmartscopeBaseModel, auth_header:Dict=AUTH_HEADER) -> requests.Response:
    url = generate_get_single_url(instance.uid,route=instance.api_route)
    response = requests.delete(url=url,headers=auth_header)
    if response.status_code != 204:
        raise RequestUnsuccessfulError(response)
    return response

def delete_many(instances: QueryList[SmartscopeBaseModel], auth_header:Dict=AUTH_HEADER) -> requests.Response:
    url = generate_get_url(route=instances.first().api_route, route_suffixes=['delete_many'])
    logger.debug(f'Deleting {len(instances)} objects from {url}')
    response = requests.post(url=url,headers=auth_header, json=instances.dump_uids())
    if response.status_code != 204:
        raise RequestUnsuccessfulError(response)
    return response