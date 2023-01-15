from typing import NamedTuple, Tuple


class Call(NamedTuple):
    '''
    Represents a block of code which is "called".
    Becomes a "caller" when its execution involves calls to other code blocks.
    '''

    fq_module_text: str
    fq_module_tuple: Tuple[str]
    function_name: str
    line_index: int
