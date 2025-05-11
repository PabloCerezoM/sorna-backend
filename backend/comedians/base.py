from typing import Any
from backend.database.enums.comedians import ComedianStrEnum

class MetaComedian(type):
    comedians: dict[ComedianStrEnum, type["BaseComedian"]] = {}

    def __init__(cls, name, bases, attrs: dict[str, Any]):
        if bases and len(bases) > 1:
            raise TypeError("BaseComedian cannot be inherited from multiple classes.")
        if bases:
            base: type[BaseComedian] = bases[0]
            if base is not BaseComedian:
                raise TypeError(f"Comedian classes only can inherit from BaseComedian. Please check implementation of {name}")
            
            comedian_name = attrs.get("name")

            if not comedian_name or not isinstance(comedian_name, ComedianStrEnum):
                raise TypeError(f"{name}.name must be an instance of ComedianStrEnum. Please check implementation of {name}")
            
            if comedian_name in cls.comedians:
                raise ValueError(f"Comedian {name} already exists. Please check implementation of {name}")
            
            cls.comedians[comedian_name] = cls # type: ignore
            
        super(MetaComedian, cls).__init__(name, bases, attrs)

    @classmethod
    def get_comedian(cls, name: ComedianStrEnum) -> type["BaseComedian"]:
        if name not in cls.comedians:
            raise ValueError(f"Comedian {name} does not exist. Please check implementation of {name}")
        return cls.comedians[name]
    

class BaseComedian(metaclass=MetaComedian):
    name: ComedianStrEnum
    name_comedian: str

    @staticmethod
    def get_context() -> str: ...