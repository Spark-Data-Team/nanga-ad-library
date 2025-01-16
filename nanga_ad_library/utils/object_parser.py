import json


class ObjectParser:
    """
    ObjectParser instances are initialized with a dictionary describing their attributes.
        Usage example:
            >>> dict_to_parse = {"name": "nanga", "description": "the best digital marketing SaaS available"}
            >>> ad_library = ObjectParser(**dict_to_parse)
            >>> print(f"Welcome to {ad_library.name}: {ad_library.description}")
            Welcome to nanga: the best digital marketing SaaS available

    Attributes can be accessed using object.field, object["field"], or object.get("field").
    It also have the standard dict methods: .keys(), .values() and .items()
    """

    def __repr__(self):
        return json.dumps(self.__dict__)

    def __init__(self, **kwargs):
        self.__dict__ = kwargs

    def __getitem__(self, key):
        return self.__dict__[key]

    def get(self, key, default=None):
        return self.__dict__.get(key, default)

    def update(self, new_dict):
        self.__dict__.update(new_dict)

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()
