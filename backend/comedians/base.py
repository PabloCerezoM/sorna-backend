from backend.database.enums.comedians import ComedianStrEnum

class MetaComedian(type):
    comedians: dict[ComedianStrEnum, "BaseComedian"] = {}

    def __init__(cls, name, bases, attrs):
        if bases and len(bases) > 1:
            raise TypeError("BaseComedian cannot be inherited from multiple classes.")
        if bases:
            base: type[BaseComedian] = bases[0]
            if not issubclass(base, BaseComedian):
                raise TypeError("BaseComedian must be inherited from BaseComedian.")
        super(MetaComedian, cls).__init__(name, bases, attrs)

class BaseComedian(metaclass=MetaComedian):
    def __init__(self, name: ComedianStrEnum):
        self.name = name