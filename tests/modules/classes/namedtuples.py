from pickle import dumps
from typing import NamedTuple
from urllib.parse import ParseResult, urlsplit


class Person(NamedTuple):
    firstname: str
    lastname: str

    def full_name(self) -> str:
        return f'{self.firstname} {self.lastname}'


def create_person(firstname, lastname):
    return Person(firstname, lastname)


def main_namedtuple():
    url_parts: ParseResult = urlsplit('http://Suzie/Q')
    return create_person(url_parts.netloc, url_parts.path[1:]).full_name()


class Pet(NamedTuple):
    name: str
    age: int = 0


def update_namedtuple(entry: NamedTuple, **update_kwargs):
    return entry._replace(**update_kwargs)


def main_namedtuple_disambiguation():
    suzie = Person('Suzie', 'Queue')
    suzie = update_namedtuple(suzie, lastname='Q')

    bemol = Pet(name='Bémol')
    bemol = update_namedtuple(bemol, age=2)

    # dumps(suzie) calls suzie.__getnewargs__() under the hood, repr(bemol) calls bemol.__repr__()
    return suzie, dumps(suzie), bemol._asdict(), repr(bemol)
