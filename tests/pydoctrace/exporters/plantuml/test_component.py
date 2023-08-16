from io import StringIO
from typing import Any, Dict, Iterable, Union

from pytest import mark

from pydoctrace.exporters.plantuml.component import PLANTUML_COMPONENT_FORMATTER, PlantUMLComponentExporter


@mark.parametrize(
    ['text_to_format', 'values_by_key', 'formatted_text'],
    [
        ('', {}, ''),
        ('@startuml {diagram_name}', {
            'diagram_name': 'diagram_name'
        }, '@startuml diagram_name'),

        # no need to replace '@' occurrences in the PlantUML component diagram syntax
        ('function {decorator}', {
            'decorator': '@tracer'
        }, 'function @tracer'),

        # '__' occurrences are escaped only when specified by the 'dunder' format_spec
        ('{styling} {name:dunder}', {
            'styling': '__italic__',
            'name': '__main__'
        }, '__italic__ ~__main~__'),
    ]
)
def test_plantuml_component_formatter(text_to_format: str, values_by_key: Dict[str, Any], formatted_text):
    assert PLANTUML_COMPONENT_FORMATTER.format(text_to_format, **values_by_key) == formatted_text


@mark.parametrize(
    ['ranks', 'label_ranks'], [
        ([], ''),
        ([1], '1'),
        ([1, 2], '1, 2'),
        ([1, 2, 3, 4, 5, 6, 7], '1, 2, 3, 4, 5, 6, 7'),
        ([1, 2, 3, 4, 5, 6, 7, 8], '1, 2, 3 ... 6, 7, 8'),
    ]
)
def test_plantuml_component_exporter_build_arrow_label_ranks(ranks: Iterable[Union[int, str]], label_ranks: str):
    assert PlantUMLComponentExporter(None).build_arrow_label_ranks(ranks) == label_ranks


def test_plantuml_component_exporter_on_headers():
    exported_contents = StringIO()
    exporter = PlantUMLComponentExporter(exported_contents)
    exporter.on_header('math_cli.__main__', 'factorial')
    assert exported_contents.getvalue().startswith('@startuml math_cli.__main__.factorial-component\n')
