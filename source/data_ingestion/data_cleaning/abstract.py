from abc import ABC, abstractmethod
from abc import ABC, abstractmethod
from typing import Dict, Any, List


class FieldCleaner(ABC):
    field_key: str = ""

    @abstractmethod
    def clean(self, key: str, value: Any, context: Dict = None) -> Any:
        pass
