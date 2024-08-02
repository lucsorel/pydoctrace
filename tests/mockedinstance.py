from json import JSONEncoder, dumps
from typing import Any, Hashable, Mapping, Union, _GenericAlias, _SpecialForm


class MockedInstance(Mapping):
    """
    Creates an object instance from a dictionary.
    so that access paths like dict['key1']['key2']['key3'] can also be followed by instance.key1.key2.key3
    """

    def __init__(self, inner_attributes_as_dict: dict):
        self.update_instance_dict(self, inner_attributes_as_dict)

    def update_instance_dict(self, instance: 'MockedInstance', attributes_dict: dict):
        instance.__dict__.update(attributes_dict)
        for instance_attribute, value in attributes_dict.items():
            if isinstance(value, dict):
                setattr(instance, instance_attribute, MockedInstance(value))

    def get(self, key: Hashable, default: Any = None) -> Any:
        return self.__dict__.get(key, default)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __len__(self):
        return len(self.__dict__)

    def __iter__(self):
        yield from self.__dict__.__iter__()

    def __repr__(self):
        return dumps(self.__dict__, cls=MockedInstanceEncoder)


class MockedInstanceEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, MockedInstance):
            return obj.__dict__
        elif isinstance(obj, Union[_GenericAlias, _SpecialForm]):
            return obj._name
        return JSONEncoder.default(self, obj)
