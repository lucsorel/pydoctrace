'''
This module provides formatting features to be used when producing the diagram code.
Some characters that can appear in function or module names can be interpreted by
the diagram syntax as formatting characters and thus should be replaced by unicode
entities or escaped.

The module proposes low-level functions adapted to be used in a Python string.Formatter
(see https://docs.python.org/3/library/string.html#string.Formatter) and follow
the signature of the Formatter.format_field(self, value: Any, format_spec: str) method
(see https://docs.python.org/3/library/string.html#string.Formatter.format_field).

These formatting functions can be then used as reusable components to build custom
formatters that suit specific needs only (depending on the diagram syntax).

In the string template to format, you can define and use specific format_spec flag
to activate a formatting feature of the formatter. For example, if you know that
some '__' dunder sdtrings need to be escaped, you can express it in the template:
CALL_TPL = r'{calling_function.name:dunder} -> {called_function.name:dunder}'

Once the formatting component has handled the dunder thing, the 'dunder' format_spec
must be replaced by '' when passed to the parent Formatter.format_field() method
because it would expect something supported by the Python formatting mini-language
(see https://docs.python.org/3/library/string.html#formatspec). Otherwise, an error
will be raised.
'''

from functools import reduce
from re import Pattern
from re import compile as re_compile
from string import Formatter
from typing import Any, Callable, Tuple

AROBASE_REPLACE_PATTERN: Pattern = re_compile('@')
AROBASE_IN_UNICODE: str = '<U+0040>'

DUNDER_REPLACE_PATTERN: Pattern = re_compile('__')


def replace_arobase_by_unicode(value: Any, format_spec: str) -> Tuple[Any, str]:
    '''
    Replaces the '@' character by its unicode equivalent
    '''
    if value is not None and isinstance(value, str):
        value = AROBASE_REPLACE_PATTERN.sub(AROBASE_IN_UNICODE, value)

    return value, format_spec


def escape_dunder_with_tilde(value: Any, format_spec: str) -> Tuple[Any, str]:
    if format_spec == 'dunder':
        # escapes each text part of the given str value (splitted on '.') with '~' when format_spec is 'dunder'
        # to avoid PlantUML interpreting dunder symbols as striking formatting
        if isinstance(value, str):
            value = DUNDER_REPLACE_PATTERN.sub('~__', value)

        # dunder formatting is done, cancel it for parent formatting
        format_spec = ''

    return value, format_spec


def formatter_factory(formatter_class_name: str, *formatters: Callable[[Any, str], Tuple[Any, str]]) -> Formatter:
    '''
    Creates a custom string.Formatter with the given formatters as components.
    The formatters will be applied in the given order.
    '''
    def custom_format_field(self: Formatter, value: Any, format_spec: str):
        '''
        Applies all the formatters on the given value and format_spec, which are updated by each formatter.
        '''
        updated_value, updated_format_spec = reduce(
            lambda value_and_format_spec, formatter: formatter(value_and_format_spec[0], value_and_format_spec[1]),
            formatters, (value, format_spec)
        )

        return super(self.__class__, self).format_field(updated_value, updated_format_spec)

    custom_formatter_class = type(formatter_class_name, (Formatter, ), {
        'format_field': custom_format_field
    })

    return custom_formatter_class()
