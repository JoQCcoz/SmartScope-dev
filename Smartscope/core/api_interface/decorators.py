from typing import get_args, get_origin, List
from ..models.base_model import SmartscopeBaseModel
import inspect

def parse_output(func):
    def wrapper_many(output_type:SmartscopeBaseModel,**kwargs) -> List[SmartscopeBaseModel]:
        results = func(output_type=output_type,*args,**kwargs)
        
        for i,item in enumerate(results):
            results[i] = output_type.model_validate(item)
        return results
        
    def wrapper_single(output_type:SmartscopeBaseModel, *args, **kwargs) -> SmartscopeBaseModel:
        output = func(output_type=output_type,*args,**kwargs)
        return output_type.model_validate(output)
    
    signature = inspect.signature(func)
    assert any([signature.return_annotation is SmartscopeBaseModel,
               get_origin(signature.return_annotation) is list and get_args(signature.return_annotation)[0] is SmartscopeBaseModel]), \
               'Function does not have the proper return type, It should be SmartscopeBaseModel or List[SmartscopeBaseModel]'

    if get_origin(signature.return_annotation) is list:
        return wrapper_many
    
    return wrapper_single