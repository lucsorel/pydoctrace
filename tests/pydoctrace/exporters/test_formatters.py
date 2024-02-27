from typing import Any, Tuple

from pytest import mark

from pydoctrace.exporters.formatters import escape_dunder_with_tilde, replace_arobase_by_unicode


@mark.parametrize(
    ['raw_text', 'format_spec', 'formatted_text_and_format_spec'],
    [
        (None, None, (None, None)),
        # the 'dunder' spec is always replaced, whatever the value to format
        (None, 'dunder', (None, '')),
        (1, 'dunder', (1, '')),
        ('text', 'dunder', ('text', '')),
        # replaces each '__' occurrence by '~__'
        ('____', 'dunder', ('~__~__', '')),
        ('__main__', 'dunder', ('~__main~__', '')),
        ('package.__dundermodule__.module', 'dunder', ('package.~__dundermodule~__.module', '')),
        ('package.__dundermodule__.module.__init__', 'dunder', ('package.~__dundermodule~__.module.~__init~__', '')),
        # no replacement is done if the 'dunder' format_spec is not specified
        ('____', '', ('____', '')),
        ('__main__', '', ('__main__', '')),
        ('package.__dundermodule__.module', '', ('package.__dundermodule__.module', '')),
        ('package.__dundermodule__.module.__init__', '', ('package.__dundermodule__.module.__init__', '')),
    ],
)
def test_escape_dunder_with_tilde(raw_text: str, format_spec: str, formatted_text_and_format_spec: Tuple[Any, str]):
    assert escape_dunder_with_tilde(raw_text, format_spec) == formatted_text_and_format_spec


@mark.parametrize(
    ['raw_text', 'format_spec', 'formatted_text_and_format_spec'],
    [
        (None, None, (None, None)),
        # this formatter does not use nor consume the format_spec and just passes it to the sibling and parent formatters
        (0, None, (0, None)),
        (0.123456, '.1%', (0.123456, '.1%')),
        (True, None, (True, None)),
        (False, 'dunder', (False, 'dunder')),
        # replaces each '@' occurrence by its unicode counterpart
        ('@', None, ('<U+0040>', None)),
        ('@', '.3%', ('<U+0040>', '.3%')),
        ('__main__.@decorate(@decorator)', '', ('__main__.<U+0040>decorate(<U+0040>decorator)', '')),
        ('__main__.@decorate(@decorator)', 'dunder', ('__main__.<U+0040>decorate(<U+0040>decorator)', 'dunder')),
    ],
)
def test_replace_arobase_by_unicode(raw_text: Any, format_spec: str, formatted_text_and_format_spec: Tuple[Any, str]):
    assert replace_arobase_by_unicode(raw_text, format_spec) == formatted_text_and_format_spec
