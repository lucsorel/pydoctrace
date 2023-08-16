from io import StringIO
from typing import Any, Dict

from pytest import mark

from pydoctrace.exporters.plantuml.sequence import PLANTUML_SEQUENCE_FORMATTER, PlantUMLSequenceExporter


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


def test_plantuml_sequence_exporter_on_headers():
    exported_contents = StringIO()
    exporter = PlantUMLSequenceExporter(exported_contents)
    exporter.on_header('math_cli.__main__', 'factorial')
    assert exported_contents.getvalue().startswith('@startuml math_cli.__main__.factorial-sequence\n')
