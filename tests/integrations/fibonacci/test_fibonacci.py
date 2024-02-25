from pytest import mark

from pydoctrace.exporters.plantuml.component import PlantUMLComponentExporter
from pydoctrace.exporters.plantuml.sequence import PlantUMLSequenceExporter

from tests.integrations import TESTS_INTEGRATIONS_FOLDER, _get_file_suffix, integration_test
from tests.modules.fibonacci import fibonacci


@mark.parametrize('exporter_class', [PlantUMLSequenceExporter, PlantUMLComponentExporter])
def test_fibonacci_valid_cases(exporter_class):
    suffix = _get_file_suffix(exporter_class)
    integration_test(
        TESTS_INTEGRATIONS_FOLDER / 'fibonacci' / f'test_fibonacci-4-3-{suffix}.puml',
        3,
        fibonacci,
        (4,),
        None,
        exporter_class,
        # overwrite_expected_contents=True,
    )
