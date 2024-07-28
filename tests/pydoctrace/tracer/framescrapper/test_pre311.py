from collections import namedtuple
from dataclasses import dataclass
from typing import Callable, NamedTuple, Tuple, Type

from pytest import mark, raises

from pydoctrace.tracer.framescrapper.pre311 import FrameScrapperPrePy311


@mark.parametrize(
    ['entry', 'expected_metadata_with_fake_id'],
    [
        (FrameScrapperPrePy311(), (FrameScrapperPrePy311, 21)),
        (FrameScrapperPrePy311, (FrameScrapperPrePy311, 4)),
    ],
)
def test_framescrapperpre311__parsed_entry_key(
    monkeypatch, entry: object, expected_metadata_with_fake_id: Tuple[Type, int]
):
    monkeypatch.setattr('builtins.id', lambda value: len(value.__class__.__qualname__))
    assert FrameScrapperPrePy311()._parsed_entry_key(entry) == expected_metadata_with_fake_id


@mark.parametrize(
    ['owner', 'expected_class_metadata'],
    [
        (None, (None, None)),
        (FrameScrapperPrePy311, ('pydoctrace.tracer.framescrapper.pre311', 'FrameScrapperPrePy311')),
        (FrameScrapperPrePy311(), ('pydoctrace.tracer.framescrapper.pre311', 'FrameScrapperPrePy311')),
        (str, ('builtins', 'str')),
        ('', ('builtins', 'str')),
    ],
)
def test_framescrapperpre311__get_owner_class_metadata(owner: object, expected_class_metadata: Tuple[str, str]):
    assert FrameScrapperPrePy311()._get_owner_class_metadata(owner) == expected_class_metadata


@dataclass(order=True, unsafe_hash=True)
class Person:
    firstname: str
    lastname: str

    def fullname(self) -> str:
        return f'{self.firstname} {self.lastname}'


class ContactManager:
    @dataclass
    class InnerContact:
        fullname: str


@mark.parametrize(
    ['method', 'owner', 'expected_fq_method_name'],
    [
        (Person.__init__, Person, 'test_pre311.Person.__init__'),
        (Person.__hash__, Person, 'test_pre311.Person.__hash__'),
        (Person.__repr__, Person, 'test_pre311.Person.__repr__'),
        (Person.__eq__, Person, 'test_pre311.Person.__eq__'),
        (Person.fullname, Person, 'test_pre311.Person.fullname'),
        (Person.__repr__, __builtins__, 'builtins.__repr__'),
        (
            ContactManager.InnerContact.__init__,
            ContactManager.InnerContact,
            'test_pre311.ContactManager.InnerContact.__init__',
        ),
    ],
)
def test_framescrapperpre311__dataclass_fq_method(method: Callable, owner: object, expected_fq_method_name: str):
    assert (
        FrameScrapperPrePy311()._dataclass_fq_method(method.__module__, method.__qualname__, owner)
        == expected_fq_method_name
    )


OldieNamedTuple = namedtuple('OldieNamedTuple', ['value'])


class ModernNamedTuple(NamedTuple):
    value: int

    def has_value(self) -> bool:
        return self.value is not None


@mark.parametrize(
    ['entry', 'expected_is_named_tuple'],
    [
        (None, False),
        (Person, False),
        (str, False),
        ('', False),
        (Person('Suzie', 'Q'), False),
        (OldieNamedTuple, True),
        (OldieNamedTuple(42), True),
        (ModernNamedTuple, True),
        (ModernNamedTuple(42), True),
    ],
)
def test_framescrapperpre311__is_a_named_tuple(entry: object, expected_is_named_tuple: bool):
    assert FrameScrapperPrePy311()._is_a_named_tuple(entry) is expected_is_named_tuple


@mark.parametrize(
    ['method', 'expected_fq_method_name'],
    [
        (ModernNamedTuple.has_value, 'test_pre311.ModernNamedTuple.has_value'),
        # the following methods refer to functions defined in the collections.namedtuple module
        (ModernNamedTuple._asdict, 'collections.namedtuple._asdict'),
        (ModernNamedTuple._make, 'collections.namedtuple._make'),
        (ModernNamedTuple._replace, 'collections.namedtuple._replace'),
        (ModernNamedTuple.__repr__, 'collections.namedtuple.__repr__'),
        (ModernNamedTuple.__getnewargs__, 'collections.namedtuple.__getnewargs__'),
    ],
)
def test_framescrapperpre311__namedtuple_fq_method(method, expected_fq_method_name: str):
    assert (
        FrameScrapperPrePy311()._namedtuple_fq_method(
            method.__module__,
            method.__qualname__,
        )
        == expected_fq_method_name
    )


@mark.parametrize(
    ['function_qualname', 'expected_component_qualname'],
    [
        ('module.function', 'module.function'),
        ('module.function.<locals>.local_function', 'module.function<locals>.local_function'),
        (
            'module.function.<locals>.Class.factory.<locals>.local_constructor',
            'module.function<locals>.Class.factory<locals>.local_constructor',
        ),
    ],
)
def test_framescrapperpre311__create_components_for_locals(function_qualname: str, expected_component_qualname: str):
    assert FrameScrapperPrePy311()._create_components_for_locals(function_qualname) == expected_component_qualname


def test_framescrapperpre311__not_yet_parsed_entries_iter_empty_cache():
    namespace = {'str': str, 'print': print}
    parsed_types = set()
    frame_scrapper = FrameScrapperPrePy311()
    entry_iter = frame_scrapper._not_yet_parsed_entries_iter(namespace, parsed_types=parsed_types)

    entry_name, entry = next(entry_iter)
    assert (entry_name, entry) == ('str', str)
    assert len(parsed_types) == 1, 'parsed_types cache now has 1 entry'
    assert frame_scrapper._parsed_entry_key(str) in parsed_types

    entry_name, entry = next(entry_iter)
    assert (entry_name, entry) == ('print', print)
    assert len(parsed_types) == 2, 'parsed_types cache now has 2 entries'
    assert frame_scrapper._parsed_entry_key(str) in parsed_types
    assert frame_scrapper._parsed_entry_key(print) in parsed_types

    # no more entry to yield
    with raises(StopIteration):
        next(entry_iter)


def test_framescrapperpre311__not_yet_parsed_entries_iter_with_cache():
    namespace = {'str': str, 'print': print}
    frame_scrapper = FrameScrapperPrePy311()
    parsed_types = set()
    parsed_types.add(frame_scrapper._parsed_entry_key(print))
    entry_iter = frame_scrapper._not_yet_parsed_entries_iter(namespace, parsed_types=parsed_types)

    entry_name, entry = next(entry_iter)
    assert (entry_name, entry) == ('str', str)
    assert len(parsed_types) == 2, 'parsed_types cache now has 2 entries'
    assert frame_scrapper._parsed_entry_key(str) in parsed_types

    # no more entry to yield
    with raises(StopIteration):
        next(entry_iter)
