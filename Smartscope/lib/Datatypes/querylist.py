from typing import Optional, Any


class QueryList(list):

    def first(self) -> Optional[Any]:
        if len(self) > 0:
            return self[0]