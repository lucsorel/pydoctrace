from io import StringIO
from typing import Any, Dict, Tuple

from pytest import fixture, mark

from pydoctrace.domain.execution import CallEnd, Error
from pydoctrace.exporters.plantuml.sequence import PLANTUML_SEQUENCE_FORMATTER, PlantUMLSequenceExporter


@fixture(scope='function')
def sequence_exporter_and_writer() -> Tuple[PlantUMLSequenceExporter, StringIO]:
    exported_contents = StringIO()
    exporter = PlantUMLSequenceExporter(exported_contents)

    return exporter, exported_contents


@mark.parametrize(
    ['text_to_format', 'values_by_key', 'formatted_text'],
    [
        ('', {}, ''),
        ('@startuml {diagram_name}', {
            'diagram_name': 'pydoctrace'
        }, '@startuml pydoctrace'),

        # '@' occurrences are replaced in the PlantUML sequence diagram syntax
        ('function {decorator}', {
            'decorator': '@tracer'
        }, 'function <U+0040>tracer'),

        # '__' occurrences are escaped only when specified by the 'dunder' format_spec
        ('{styling} {name:dunder}', {
            'styling': '__italic__',
            'name': '__main__'
        }, '__italic__ ~__main~__'),
    ]
)
def test_plantuml_sequence_formatter(text_to_format: str, values_by_key: Dict[str, Any], formatted_text):
    assert PLANTUML_SEQUENCE_FORMATTER.format(text_to_format, **values_by_key) == formatted_text


@mark.parametrize(['arg', 'formatted_arg'], [
    (None, ''),
    ('', ''),
    ('text', 'text'),
    (3.1426, 3.1426),
])
def test_plantuml_sequence_exporter_format_arg_value(arg: Any, formatted_arg: Any):
    assert PlantUMLSequenceExporter(None).format_arg_value(arg) == formatted_arg


def test_plantuml_sequence_exporter_on_header(sequence_exporter_and_writer: Tuple[PlantUMLSequenceExporter, StringIO]):
    exporter, contents_writer = sequence_exporter_and_writer

    exporter.on_header('math_cli.__main__', 'factorial')

    assert contents_writer.getvalue().startswith('@startuml math_cli.__main__.factorial-sequence\n')


def test_plantuml_sequence_exporter_on_tracing_start(
    sequence_exporter_and_writer: Tuple[PlantUMLSequenceExporter, StringIO]
):
    exporter, contents_writer = sequence_exporter_and_writer
    start_called = CallEnd('math_cli.__main__', ('math_cli', '__main__'), 'factorial', 16)

    exporter.on_tracing_start(start_called)

    assert contents_writer.getvalue() == r'''
[o-> "math_cli.~__main~__\nfactorial"
note right: line 16
'''


def test_plantuml_sequence_exporter_on_start_call(
    sequence_exporter_and_writer: Tuple[PlantUMLSequenceExporter, StringIO]
):
    exporter, contents_writer = sequence_exporter_and_writer
    caller = CallEnd('math_cli.controller', ('math_cli', 'controller'), 'factorial', 25)
    called = CallEnd('math_cli.validator', ('math_cli', 'validator'), 'is_positive_int', 4)

    exporter.on_start_call(caller, called)

    assert contents_writer.getvalue() == r'''
"math_cli.controller\nfactorial" -> "math_cli.validator\nis_positive_int" ++
note left: line 25
note right: line 4
'''


def test_plantuml_sequence_exporter_on_error_propagation(
    sequence_exporter_and_writer: Tuple[PlantUMLSequenceExporter, StringIO]
):
    exporter, contents_writer = sequence_exporter_and_writer
    caller = CallEnd('math_cli.__main__', ('math_cli', '__main__'), 'factorial', 4)
    called = CallEnd('math_cli.validator', ('math_cli', 'validator'), 'validate_positive_int', 25)
    validation_error = Error('ValueError', 'must be a positive integer')

    exporter.on_error_propagation(called, caller, validation_error)

    assert contents_writer.getvalue() == r'''
"math_cli.~__main~__\nfactorial" o<--x "math_cli.validator\nvalidate_positive_int": ""ValueError""\nmust be a positive integer
deactivate "math_cli.validator\nvalidate_positive_int"
note right: line 25
note left: line 4
'''


def test_plantuml_sequence_exporter_on_return(sequence_exporter_and_writer: Tuple[PlantUMLSequenceExporter, StringIO]):
    exporter, contents_writer = sequence_exporter_and_writer
    caller = CallEnd('math_cli.controller', ('math_cli', 'controller'), '__main__', 25)
    called = CallEnd('math_cli.compute', ('math_cli', 'compute'), 'factorial', 4)
    returned_value = 24

    exporter.on_return(caller=caller, called=called, arg=returned_value)

    assert contents_writer.getvalue() == r'''
return 24
note right: line 4
|||
'''


def test_plantuml_sequence_exporter_on_tracing_end(
    sequence_exporter_and_writer: Tuple[PlantUMLSequenceExporter, StringIO]
):
    exporter, contents_writer = sequence_exporter_and_writer
    called = CallEnd('math_cli.formatting', ('math_cli', 'formatting'), '__to_italic', 25)
    returned_value = '__italic_text__'

    exporter.on_tracing_end(called, returned_value)

    assert contents_writer.getvalue() == r'''
[<-- "math_cli.formatting\n~__to_italic": ~__italic_text~__
note right: line 25
'''


def test_plantuml_sequence_exporter_on_unhandled_error_end(
    sequence_exporter_and_writer: Tuple[PlantUMLSequenceExporter, StringIO]
):
    exporter, contents_writer = sequence_exporter_and_writer
    called = CallEnd('math_cli.validator', ('math_cli', 'validator'), 'validate_positive_int', 25)
    validation_error = Error('ValueError', 'must be a positive integer')

    exporter.on_unhandled_error_end(called, validation_error)

    assert contents_writer.getvalue() == r'''
[<-->x "math_cli.validator\nvalidate_positive_int": ""ValueError""\nmust be a positive integer
note right: line 25
'''


def test_plantuml_sequence_exporter_on_footer(sequence_exporter_and_writer: Tuple[PlantUMLSequenceExporter, StringIO]):
    exporter, contents_writer = sequence_exporter_and_writer

    exporter.on_footer()

    assert contents_writer.getvalue() == r'''
footer Generated by //pydoctrace//
@enduml
'''
