from typing import Optional, Any, List


class QueryList(list):
    #List of Pydantic models

    def first(self) -> Optional[Any]:
        if len(self) > 0:
            return self[0]
        
    def dump_all(self) -> List[Any]:
        return [obj.model_dump() for obj in self]