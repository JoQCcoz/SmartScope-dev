from pydantic import BaseModel

class SmartscopeBaseModel(BaseModel):

    

    class Meta:
        api_route = 'NotImplemented'
        

    @classmethod
    @property
    def api_route(cls):
        assert cls.Meta.api_route != 'NotImplemented', f"Add the metaclass with api route to {cls.__name__} \nclass Meta:\n\tapi_route='route'\n"
        return cls.Meta.api_route