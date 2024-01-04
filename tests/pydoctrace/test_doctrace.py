from io import StringIO
from pathlib import Path
from typing import Callable, Type

from pytest import mark

from pydoctrace.callfilter import FILTER_OUT_STDLIB, TRACE_ALL_FILTER, call_filter_factory
from pydoctrace.callfilter.presets import EXCLUDE_CALL_DEPTH_PRESET_FACTORY, Preset
from pydoctrace.doctrace import trace_to_component_puml, trace_to_sequence_puml
from pydoctrace.exporters import Exporter
from pydoctrace.exporters.plantuml.component import PlantUMLComponentExporter
from pydoctrace.exporters.plantuml.sequence import PlantUMLSequenceExporter
from pydoctrace.tracer import ExecutionTracer

from tests import TESTS_FOLDER
from tests.integrations.calldepth import depth_1
from tests.modules.factorial import factorial_recursive


def integration_test(
    expected_exported_contents_path: Path,
    expected_result,
    function_to_trace: Callable,
    exporter_class: Type[Exporter],
    *presets: Preset,
    overwrite_expected_contents: bool = False,
):
    exported_io = StringIO()
    exporter = exporter_class(exported_io)
    exporter.on_header(depth_1.__module__, depth_1.__name__)
    result = ExecutionTracer(exporter, call_filter_factory(presets)).runfunc(function_to_trace)
    assert result == expected_result
    exporter.on_footer()

    # useful to create or update integration files
    if overwrite_expected_contents:
        with open(expected_exported_contents_path, 'w', encoding='utf8') as expected_contents_file:
            expected_contents_file.writelines(exported_io.getvalue().splitlines(keepends=True))
    # compares expected and produced contents
    else:
        with open(expected_exported_contents_path, encoding='utf8') as expected_contents_file:
            for line_index, (expected_line, produced_line) in enumerate(
                zip(expected_contents_file.readlines(), exported_io.getvalue().splitlines(keepends=True))
            ):
                assert expected_line == produced_line, f'line {line_index + 1} of {expected_exported_contents_path}'


@mark.parametrize(
    ['expected_contents_file', 'depth_threshold'],
    [
        ('test_depth_1-component-above_depth_3_preset.puml', 3),
        ('test_depth_1-component-above_depth_4_preset.puml', 4),
        ('test_depth_1-component-above_depth_5_preset.puml', 5),
    ],
)
def test_call_depth_with_threshold_of(expected_contents_file: str, depth_threshold: int):
    integration_test(
        TESTS_FOLDER / 'integrations' / 'calldepth' / expected_contents_file,
        12,
        depth_1,
        PlantUMLComponentExporter,
        EXCLUDE_CALL_DEPTH_PRESET_FACTORY(depth_threshold),
        # overwrite_expected_contents=True
    )


def test_tracer_sequence():
    def trace_factorial_6():
        tracing_factorial_recursive = trace_to_sequence_puml(factorial_recursive)

        return tracing_factorial_recursive(6)

    with open('traced_factorial-sequence.puml', 'w', encoding='utf8') as puml_file:
        exporter = PlantUMLSequenceExporter(puml_file)
        exporter.on_header(trace_factorial_6.__module__, trace_factorial_6.__name__)

        try:
            result = ExecutionTracer(exporter, TRACE_ALL_FILTER).runfunc(trace_factorial_6)
            assert result == 720
        finally:
            exporter.on_footer()


def test_tracer_component():
    def trace_factorial_6():
        tracing_factorial_recursive = trace_to_component_puml(factorial_recursive)

        return tracing_factorial_recursive(6)

    with open('traced_factorial-component.puml', 'w', encoding='utf8') as puml_file:
        exporter = PlantUMLComponentExporter(puml_file)
        exporter.on_header(trace_factorial_6.__module__, trace_factorial_6.__name__)

        try:
            result = ExecutionTracer(exporter, TRACE_ALL_FILTER).runfunc(trace_factorial_6)
            assert result == 720
        finally:
            exporter.on_footer()


def test_tracer_component_without_stdlib_modules():
    def trace_factorial_6():
        tracing_factorial_recursive = trace_to_component_puml(factorial_recursive)

        return tracing_factorial_recursive(6)

    with open('traced_factorial-no_stdlib-component.puml', 'w', encoding='utf8') as puml_file:
        exporter = PlantUMLComponentExporter(puml_file)
        exporter.on_header(trace_factorial_6.__module__, trace_factorial_6.__name__)

        try:
            result = ExecutionTracer(exporter, FILTER_OUT_STDLIB).runfunc(trace_factorial_6)
            assert result == 720
        finally:
            exporter.on_footer()
