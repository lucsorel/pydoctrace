from io import StringIO
from pathlib import Path
from typing import Any, Callable, Type

from pydoctrace.callfilter import call_filter_factory
from pydoctrace.callfilter.presets import Preset
from pydoctrace.exporters import Exporter
from pydoctrace.exporters.plantuml.component import PlantUMLComponentExporter
from pydoctrace.exporters.plantuml.sequence import PlantUMLSequenceExporter
from pydoctrace.tracer import ExecutionTracer

TESTS_INTEGRATIONS_FOLDER = Path(__file__).parent


def _get_file_suffix(exporter_class) -> str:
    if exporter_class is PlantUMLComponentExporter:
        suffix = 'component'
    elif exporter_class is PlantUMLSequenceExporter:
        suffix = 'sequence'
    else:
        raise ValueError(f'Unhandled class: {exporter_class}')
    return suffix


def diagram_integration_test(
    expected_exported_contents_path: Path,
    function_to_trace: Callable,
    function_args: tuple,
    function_kwargs: dict,
    exporter_class: Type[Exporter],
    *presets: Preset,
    overwrite_expected_contents: bool = False,
) -> Any:
    """
    Utility function to write an integration test comparing the tracing of a function call and the expected diagram contents:
    - expected_exported_contents_path: the file containing the expected diagram contents
    - overwrite_expected_contents: set to True temporarily to update the contents of expected_exported_contents_path.
      But you should commit calls only with overwrite_expected_contents set to False
    It returns the outcome of the traced execution for further testing.
    """
    exported_io = StringIO()
    exporter = exporter_class(exported_io)
    exporter.on_header(function_to_trace.__module__, function_to_trace.__name__)
    function_args = function_args or ()
    function_kwargs = function_kwargs or {}
    try:
        return ExecutionTracer(exporter, call_filter_factory(presets)).runfunc(
            function_to_trace, *function_args, **function_kwargs
        )

    except Exception as exception:
        raise exception
    finally:
        # in case of failures or error, the export is always finished and the contents comparison is performed
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
                    assert expected_line == produced_line, (
                        expected_exported_contents_path,
                        f'line {line_index + 1}',
                        expected_line,
                        produced_line,
                    )
