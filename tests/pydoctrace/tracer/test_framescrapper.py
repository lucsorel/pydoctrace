from collections import namedtuple
from dataclasses import dataclass
from inspect import getmembers
from types import CodeType
from typing import Callable, NamedTuple, Tuple, Type

from pytest import mark, raises

from pydoctrace.tracer.framescrapper import FrameScrapper

from tests.mockedinstance import MockedInstance


@mark.parametrize(
    ['entry', 'expected_metadata_with_fake_id'],
    [
        (FrameScrapper(), (FrameScrapper, 13)),
        (FrameScrapper, (FrameScrapper, 4)),
    ],
)
def test_framescrapper__parsed_entry_key(monkeypatch, entry: object, expected_metadata_with_fake_id: Tuple[Type, int]):
    monkeypatch.setattr('builtins.id', lambda value: len(value.__class__.__qualname__))
    assert FrameScrapper()._parsed_entry_key(entry) == expected_metadata_with_fake_id


@mark.parametrize(
    ['owner', 'expected_class_metadata'],
    [
        (None, (None, None)),
        (FrameScrapper, ('pydoctrace.tracer.framescrapper', 'FrameScrapper')),
        (FrameScrapper(), ('pydoctrace.tracer.framescrapper', 'FrameScrapper')),
        (str, ('builtins', 'str')),
        ('', ('builtins', 'str')),
    ],
)
def test_framescrapper__get_owner_class_metadata(owner: object, expected_class_metadata: Tuple[str, str]):
    assert FrameScrapper()._get_owner_class_metadata(owner) == expected_class_metadata


@dataclass(order=True, unsafe_hash=True)
class Person:
    firstname: str
    lastname: str

    def fullname(self) -> str:
        return f'{self.firstname} {self.lastname}'


class ContactManager:
    def is_none(self) -> bool:
        """
        Just a method
        """
        return self is None

    @dataclass
    class InnerContact:
        fullname: str


@mark.parametrize(
    ['method', 'owner', 'expected_fq_method_name'],
    [
        (Person.__init__, Person, 'test_framescrapper.Person.__init__'),
        (Person.__hash__, Person, 'test_framescrapper.Person.__hash__'),
        (Person.__repr__, Person, 'test_framescrapper.Person.__repr__'),
        (Person.__eq__, Person, 'test_framescrapper.Person.__eq__'),
        (Person.fullname, Person, 'test_framescrapper.Person.fullname'),
        (Person.__repr__, __builtins__, 'builtins.__repr__'),
        (
            ContactManager.InnerContact.__init__,
            ContactManager.InnerContact,
            'test_framescrapper.ContactManager.InnerContact.__init__',
        ),
    ],
)
def test_framescrapper__dataclass_fq_method(method: Callable, owner: object, expected_fq_method_name: str):
    assert (
        FrameScrapper()._dataclass_fq_method(method.__module__, method.__qualname__, owner) == expected_fq_method_name
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
def test_framescrapper__is_a_named_tuple(entry: object, expected_is_named_tuple: bool):
    assert FrameScrapper()._is_a_named_tuple(entry) is expected_is_named_tuple


@mark.parametrize(
    ['method', 'expected_fq_method_name'],
    [
        (ModernNamedTuple.has_value, 'test_framescrapper.ModernNamedTuple.has_value'),
        # the following methods refer to functions defined in the collections.namedtuple module
        (ModernNamedTuple._asdict, 'collections.namedtuple._asdict'),
        (ModernNamedTuple._make, 'collections.namedtuple._make'),
        (ModernNamedTuple._replace, 'collections.namedtuple._replace'),
        (ModernNamedTuple.__repr__, 'collections.namedtuple.__repr__'),
        (ModernNamedTuple.__getnewargs__, 'collections.namedtuple.__getnewargs__'),
    ],
)
def test_framescrapper__namedtuple_fq_method(method, expected_fq_method_name: str):
    assert (
        FrameScrapper()._namedtuple_fq_method(
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
def test_framescrapper__create_components_for_locals(function_qualname: str, expected_component_qualname: str):
    assert FrameScrapper()._create_components_for_locals(function_qualname) == expected_component_qualname


def test_framescrapper__not_yet_parsed_entries_iter_empty_cache():
    namespace = {'str': str, 'print': print}
    parsed_types = set()
    frame_scrapper = FrameScrapper()
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


def test_framescrapper__not_yet_parsed_entries_iter_with_cache():
    namespace = {'str': str, 'print': print}
    frame_scrapper = FrameScrapper()
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


@mark.parametrize(
    ['owner', 'namespace', 'codeobject', 'expected_fq_method_name'],
    [
        # _iter_over_type_namespaces called with the globals/locals dict namespace (no owner)
        (None, {'Person': Person}, Person.fullname.__code__, 'test_framescrapper.Person.fullname'),
        (None, {'Person': Person}, Person.__init__.__code__, 'test_framescrapper.Person.__init__'),
        # called with the members of their owning class
        (Person, {'fullname': Person.fullname}, Person.fullname.__code__, 'test_framescrapper.Person.fullname'),
        (Person, dict(getmembers(Person)), Person.fullname.__code__, 'test_framescrapper.Person.fullname'),
        # namedtuples OldieNamedTuple
        (
            None,
            {'OldieNamedTuple': OldieNamedTuple},
            OldieNamedTuple._replace.__code__,
            'collections.namedtuple._replace',
        ),
        (
            None,
            {'ModernNamedTuple': ModernNamedTuple},
            ModernNamedTuple.has_value.__code__,
            'test_framescrapper.ModernNamedTuple.has_value',
        ),
        (
            None,
            {'ModernNamedTuple': ModernNamedTuple},
            ModernNamedTuple.has_value.__code__,
            'test_framescrapper.ModernNamedTuple.has_value',
        ),
        # classes
        (
            None,
            {'ContactManager': ContactManager},
            ContactManager.is_none.__code__,
            'test_framescrapper.ContactManager.is_none',
        ),
        (
            None,
            {'ContactManager': ContactManager},
            ContactManager.InnerContact.__init__.__code__,
            'test_framescrapper.ContactManager.InnerContact.__init__',
        ),
    ],
)
def test_framescrapper__iter_over_type_namespaces(
    owner: object, namespace: dict, codeobject: CodeType, expected_fq_method_name: str
):
    frame_scrapper = FrameScrapper()
    fullqualname_iter = frame_scrapper._iter_over_type_namespaces(owner, namespace, codeobject, parsed_types=set())
    assert next(fullqualname_iter, None) == expected_fq_method_name


def noop():
    pass


@mark.parametrize(
    ['called_frame_dict', 'expected_fq_method_name'],
    [
        # named tuple creation
        (
            {
                'f_code': {'co_name': '__new__'},
                'f_globals': {
                    '_tuple_new': ModernNamedTuple.__new__,
                },
                'f_locals': {
                    '_cls': ModernNamedTuple,
                },
            },
            'test_framescrapper.ModernNamedTuple.__new__',
        ),
        (
            {
                'f_code': {'co_name': '__new__'},
                'f_globals': {
                    '_tuple_new': OldieNamedTuple.__new__,
                },
                'f_locals': {
                    '_cls': OldieNamedTuple,
                },
            },
            'test_framescrapper.OldieNamedTuple.__new__',
        ),
        # function retrieval (usually imported in the globals of the calling frame)
        (
            {
                'f_code': noop.__code__,
                'f_globals': {},
                'f_back': {
                    'f_globals': {
                        'noop': noop,
                    },
                    'f_locals': {},
                },
            },
            'test_framescrapper.noop',
        ),
        # function retrieval (defined in the locals of the calling frame)
        (
            {
                'f_code': noop.__code__,
                'f_globals': {},
                'f_back': {
                    'f_globals': {},
                    'f_locals': {
                        'noop': noop,
                    },
                },
            },
            'test_framescrapper.noop',
        ),
        # fallback retrieval
        (
            {
                'f_code': noop.__code__,
                'f_globals': {'__name__': 'called.frame.module'},
                'f_back': {
                    'f_globals': {},
                    'f_locals': {},
                },
            },
            'called.frame.module.noop',
        ),
        # method retrieval
        (
            {
                'f_code': ContactManager.is_none.__code__,
                'f_globals': {},
                'f_back': {
                    'f_globals': {'ContactManager': ContactManager},
                    'f_locals': {},
                },
            },
            'test_framescrapper.ContactManager.is_none',
        ),
    ],
)
def test_framescrapper_scrap_callable_domain_and_name(called_frame_dict, expected_fq_method_name):
    called_frame = MockedInstance(called_frame_dict)
    assert FrameScrapper().scrap_callable_domain_and_name(called_frame) == expected_fq_method_name
