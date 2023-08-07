'''
Domain models completing the execution domain models while exporting diagrams.

NamedTuples are used for immutability sake and for their light weight.
'''

from typing import Dict, Iterable, NamedTuple, Tuple, Union


class Function(NamedTuple):
    '''
    Models a function (calling or being called):
    - it has a name
    - it is hosted in a module, modeled by its path as a tuple of strings
    '''
    name: str
    module_path: Tuple[str]

    @property
    def fqn(self) -> str:
        return '.'.join((*self.module_path, self.name))


class Call(NamedTuple):
    '''
    Flags the rank in the execution sequence when the execution leaves a block of code,
    when calling another block of code (another function).
    '''
    rank: int


class Return(NamedTuple):
    '''
    Flags the rank in the execution sequence when the execution exits a block of code normally,
    in an explicit or implicit return clause.
    '''
    rank: int


class Raised(NamedTuple):
    '''
    Flags the rank in the execution sequence when the execution exits a block of code abnormally,
    when an error is raised and not handled in the current block of code.
    '''
    rank: int
    error: str


class Interactions(NamedTuple):
    calls: Iterable[int]
    responses: Iterable[Union[Return, Raised]]


class Module(NamedTuple):
    name: str
    sub_modules: Dict[str, 'Module']
    functions: Dict[str, Function]
