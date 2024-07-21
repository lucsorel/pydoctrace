from dataclasses import dataclass


@dataclass(order=True, unsafe_hash=True)
class Person:
    firstname: str
    lastname: str

    def full_name(self) -> str:
        return f'{self.firstname} {self.lastname}'


def create_person(firstname, lastname):
    return Person(firstname=firstname, lastname=lastname)


def main_dataclass():
    suzie = create_person('Suzie', 'Q')
    suzie_hash = hash(suzie)
    frankie = Person('Frankie', 'Manning')
    frankie_repr = repr(frankie)
    comparison = suzie == frankie
    print(f'{suzie=}')

    return suzie.full_name(), suzie_hash, frankie_repr, comparison


if __name__ == '__main__':
    print(f'{main_dataclass()=}')
