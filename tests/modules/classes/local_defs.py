from typing import Tuple


class Factory:
    @staticmethod
    def create_class(class_name: str, attributes: Tuple[str]):
        def constructor(self, **kwargs):
            for attribute in attributes:
                setattr(self, attribute, kwargs.get(attribute))

        return type(class_name, (object,), {'__init__': constructor})


class FullnameCombiner:
    def __init__(self, person):
        self.person = person

    def names_combiner_factory(self):
        def fullname_combiner():
            return f'{self.person.firstname} {self.person.lastname}'

        return fullname_combiner


def get_adder():
    def local_add_function(value_1, value_2):
        return value_1 + value_2

    return local_add_function


def main_local_defs():
    adder = get_adder()
    person_class = Factory.create_class('Person', ('firstname', 'lastname', 'age'))

    suzie = person_class(firstname='Suzie', lastname='Q', age=adder(18, 4))
    fullname_combiner = FullnameCombiner(suzie)
    names_combiner = fullname_combiner.names_combiner_factory()
    return names_combiner()


if __name__ == '__main__':
    assert main_local_defs() == 'Suzie Q'
