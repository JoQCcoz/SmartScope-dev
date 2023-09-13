import pytest
from pydantic import BaseModel

from ..decorators import parse_output


def test_parse_output():
    class MockModel(BaseModel):
        x:int
    
    @parse_output
    def mock_get_API(url, output_type:MockModel) -> BaseModel:
        return dict(x=1)
    
   
    assert isinstance(mock_get_API(url='bla',output_type=MockModel), MockModel)

    with pytest.raises(AssertionError, match='proper return type'):
        @parse_output
        def wrong_mock_get_API(url, output_type:MockModel)-> None:
            return dict(x=1)
