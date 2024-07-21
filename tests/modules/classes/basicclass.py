class Person:
    firstname: str
    lastname: str

    def __init__(self, firstname: str, lastname: str):
        self.firstname = firstname
        self.lastname = lastname

    def full_name(self) -> str:
        return f'{self.firstname} {self.lastname}'

    @staticmethod
    def factory(firstname: str, lastname: str):
        return Person(firstname, lastname)


def create_person(firstname, lastname):
    person_factory = Person.factory
    return person_factory(firstname, lastname)


def main_basic_class():
    return create_person('Suzie', 'Q').full_name()
