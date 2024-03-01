from typing import NamedTuple


class Person(NamedTuple):
    firstname: str
    lastname: str


def create_person(firstname, lastname):
    return Person(firstname, lastname)


def main():
    return create_person('Suzie', 'Q')
