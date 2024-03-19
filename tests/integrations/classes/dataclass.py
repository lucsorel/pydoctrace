from dataclasses import dataclass


@dataclass
class Person:
    firstname: str
    lastname: str

    def full_name(self) -> str:
        return f'{self.firstname} {self.lastname}'


def create_person(firstname, lastname):
    return Person(firstname=firstname, lastname=lastname)


def main_dataclass():
    person = create_person('Suzie', 'Q')
    # print(f'{locals()=}')
    # print(f'{person=}')

    return person.full_name()


if __name__ == '__main__':
    print(f'{main_dataclass()=}')
