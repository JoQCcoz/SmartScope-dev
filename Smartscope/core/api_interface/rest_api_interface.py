import requests
import json
from typing import Dict, List
from Smartscope.core.settings.worker import API_BASE_URL, API_KEY

AUTH_HEADER={'Authorization':f'Token {API_KEY}'}

def generate_url(base_url:str=API_BASE_URL,route:str='',filters:Dict=dict()):
    url = f'{base_url}{route}'
    if filters != dict():
        url += '/?'

    for i,j in filters.items():
        url += f'{i}={j}&' 
    return url

def get_from_API(url, auth_header:Dict=AUTH_HEADER) -> List[Dict]:
    resp = requests.get(url,headers=auth_header)
    return resp
    # return json.loads(resp.content)['results']