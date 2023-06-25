from re import Pattern
from re import compile as re_compile
from string import Formatter
from typing import Any


class PlantUMLEscapeFormatter(Formatter):
    '''
    Formatter handling edge cases of the PlantUML syntax:
    - escape values having dunder ('__') substrings in them to prevent the PlantUML
      from interpreting them as underlining symbols of the Creole syntax.
      See https://plantuml-documentation.readthedocs.io/en/latest/formatting/creole.html#formatting-text
    - replace '@' by its unicode entity to prevent from breaking the PlantUML syntax
    '''

    DUNDER_REPLACE_PATTERN: Pattern = re_compile('__')
    AROBASE_REPLACE_PATTERN: Pattern = re_compile('@')
    UNICODE_AROBASE: str = '<U+0040>'

    def format_field(self, value: Any, format_spec: str) -> Any:
        if value is not None:
            # replaces '@' by '<U+0040>'
            value = self.AROBASE_REPLACE_PATTERN.sub(self.UNICODE_AROBASE, str(value))

        if format_spec == 'dunder':
            # escapes each text part of the given str value (splitted on '.') with '~'
            # when format_spec is 'dunder' to avoid PlantUML interpreting dunder symbols
            if isinstance(value, str):
                value = '.'.join((self.escape_dunder(part) for part in value.split('.')))

            # dunder formatting is done, cancel it for values that are not string
            format_spec = ''

        return super().format_field(value, format_spec)

    def escape_dunder(self, text: str):
        return self.DUNDER_REPLACE_PATTERN.sub('~__', text)
