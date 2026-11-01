"""
Domain models involved while tracing the code execution.

NamedTuples are used for immutability sake and for their light weight.
"""

from typing import NamedTuple, Tuple


class CallEnd(NamedTuple):
    """
    When a call is made, it is between a "calling end" (at a given line in a given module where a is function being executed)
    and a "called end" (a function whose body starts at a given line in a given module).
    """

    fq_module_text: str
    fq_module_tuple: Tuple[str]
    function_name: str
    line_index: int


class Error(NamedTuple):
    """
    Represents an error or an exception that is raised during the code execution.
    """

    class_name: str
    message: str
