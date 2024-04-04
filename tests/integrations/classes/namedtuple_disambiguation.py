from typing import NamedTuple


class Pet(NamedTuple):
    name: str
    age: int = 0


class Person(NamedTuple):
    firstname: str
    lastname: str


def update_namedtuple(entry: NamedTuple, **update_kwargs):
    return entry._replace(**update_kwargs)


def main_namedtuple_disambiguation():
    suzie = Person('Suzie', 'Queue')
    suzie = update_namedtuple(suzie, lastname='Q')

    bemol = Pet(name='Bémol')
    bemol = update_namedtuple(bemol, age=2)

    return suzie, bemol
