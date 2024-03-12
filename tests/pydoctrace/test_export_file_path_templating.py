"""
Automated tests documenting where and when template tags in the exported file name are handled.
"""

from datetime import datetime
from pathlib import Path
from typing import Callable, NamedTuple

from pytest import fixture, mark

from pydoctrace.callfilter.presets import TRACE_ALL_PRESET
from pydoctrace.doctrace import context_factory, trace_to_component_puml, trace_to_sequence_puml
from pydoctrace.exporters import Exporter

from tests.integrations import TESTS_INTEGRATIONS_FOLDER
from tests.integrations.calldepth import depth_1
from tests.modules.ecoindex import ecoindex


@mark.parametrize(
    ['function_to_trace', 'file_path_template', 'expected_templated_file_path'],
    [
        (depth_1, 'without_template_tag.puml', 'without_template_tag.puml'),
        # function name and module are handled when creating the context
        (depth_1, '${function_name}.puml', 'depth_1.puml'),
        (depth_1, '${function_module}.${function_name}.puml', 'tests.integrations.calldepth.depth_1.puml'),
        # call datetime is handled only the call to the traced function is actually called
        (depth_1, '${function_name}-${datetime_millis}.puml', 'depth_1-${datetime_millis}.puml'),
    ],
)
def test_context_factory_template_function_name_and_module(
    function_to_trace: Callable, file_path_template: str, expected_templated_file_path: str
):
    """
    Function and module names are handled when the tracing context is created.
    """
    context = context_factory(function_to_trace, None, file_path_template, None)
    assert context.export_file_path == expected_templated_file_path


@mark.parametrize(
    ['file_path_template', 'moment', 'expected_templated_file_path'],
    [
        ('depth_1.puml', datetime.fromisoformat('1963-08-28T11:37:24.042+01:00'), 'depth_1.puml'),
        # timezone details are discarded in the '${datetime_millis}' tag
        (
            'depth_1-${datetime_millis}.puml',
            datetime.fromisoformat('1963-08-28T11:37:24.042'),
            'depth_1-1963-08-28_11.37.24_042.puml',
        ),
        (
            'depth_1-${datetime_millis}.puml',
            datetime.fromisoformat('1963-08-28T11:37:24.042+01:00'),
            'depth_1-1963-08-28_11.37.24_042.puml',
        ),
    ],
)
def test_exporter_template_dynamic_tags(file_path_template: str, moment: datetime, expected_templated_file_path: str):
    assert Exporter._template_dynamic_tags(file_path_template, moment) == expected_templated_file_path


class Comparison(NamedTuple):
    comparison_folder_path: Path
    expected_contents_filename: str
    output_contents_filename_pattern: str


class CompareAndDelete:
    def __init__(self):
        self.comparison: Comparison = None

    def set_comparison(
        self, comparison_folder_path: Path, expected_contents_filename: str, output_contents_filename_pattern: str
    ):
        self.comparison = Comparison(
            comparison_folder_path, expected_contents_filename, output_contents_filename_pattern
        )

    def compare_and_delete(self, before: datetime, after: datetime):
        if self.comparison is None:
            raise ValueError('no contents to compare nor delete')

        # looks for the unique generated file
        output_contents = list(
            self.comparison.comparison_folder_path.rglob(self.comparison.output_contents_filename_pattern)
        )
        assert (
            len(output_contents) == 1
        ), f'only one file expected for pattern {self.comparison.comparison_folder_path / self.comparison.output_contents_filename_pattern}'
        output_contents_path = output_contents[0]

        # ensures that the '${datetime_millis}' tag was correctly replaced
        template_file_name = self.comparison.output_contents_filename_pattern.replace('-*-', '-${datetime_millis}-')
        before_filename = Exporter._template_dynamic_tags(template_file_name, before)
        after_filename = Exporter._template_dynamic_tags(template_file_name, after)
        assert (
            before_filename <= output_contents_path.name <= after_filename
        ), 'the ${datetime_millis} tag must be framed'

        # compares the contents
        expected_contents_path = self.comparison.comparison_folder_path / self.comparison.expected_contents_filename

        with open(expected_contents_path, encoding='utf8') as expected_contents, open(
            output_contents_path, encoding='utf8'
        ) as output_contents:
            for line_index, (expected_line, produced_line) in enumerate(
                zip(expected_contents.readlines(), output_contents.readlines())
            ):
                assert expected_line == produced_line, (
                    expected_contents_path,
                    f'line {line_index + 1}',
                    expected_line,
                    produced_line,
                )

        # deletes the generated file
        output_contents_path.unlink()


@fixture
def compare_and_delete() -> CompareAndDelete:
    compare_and_delete = CompareAndDelete()
    before = datetime.utcnow()
    yield compare_and_delete
    compare_and_delete.compare_and_delete(before, datetime.utcnow())


@mark.parametrize(
    ['tracing_decorator', 'expected_contents_filename', 'output_contents_filename_pattern', 'export_file_path_tpl'],
    [
        (
            trace_to_sequence_puml,
            'test_tests.modules.ecoindex.ecoindex-sequence.puml',
            'tests.modules.ecoindex.ecoindex-*-sequence.puml',
            'tests/integrations/ecoindex/${function_module}.${function_name}-${datetime_millis}-sequence.puml',
        ),
        (
            trace_to_component_puml,
            'test_tests.modules.ecoindex.ecoindex-component.puml',
            'tests.modules.ecoindex.ecoindex-*-component.puml',
            'tests/integrations/ecoindex/${function_module}.${function_name}-${datetime_millis}-component.puml',
        ),
    ],
)
def test_trace_with_dynamic_filename(
    compare_and_delete,
    tracing_decorator,
    expected_contents_filename,
    output_contents_filename_pattern,
    export_file_path_tpl,
):
    comparison_folder_path = TESTS_INTEGRATIONS_FOLDER / 'ecoindex'
    compare_and_delete.set_comparison(
        comparison_folder_path, expected_contents_filename, output_contents_filename_pattern
    )

    decorated_ecoindex = tracing_decorator(
        export_file_path_tpl=export_file_path_tpl, filter_presets=(TRACE_ALL_PRESET,)
    )(ecoindex)
    ecoindex_score = decorated_ecoindex(dom_elements_nb=960, requests_nb=70, size_kb=1500)

    assert abs(ecoindex_score - 41.234) < 0.001
