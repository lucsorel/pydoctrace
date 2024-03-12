from typing import NamedTuple
from urllib.parse import ParseResult, urlsplit


class Person(NamedTuple):
    firstname: str
    lastname: str

    def full_name(self) -> str:
        return f'{self.firstname} {self.lastname}'


def create_person(firstname, lastname):
    return Person(firstname, lastname)


def main_named_tuple():
    url_parts: ParseResult = urlsplit('http://Suzie/Q')
    # return f'{url_parts.netloc} {url_parts.path[1:]}'
    return create_person(url_parts.netloc, url_parts.path[1:]).full_name()
