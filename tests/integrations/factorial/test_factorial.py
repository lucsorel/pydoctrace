from typing import Callable, Type

from pytest import mark, raises

from pydoctrace.exporters.plantuml.component import PlantUMLComponentExporter
from pydoctrace.exporters.plantuml.sequence import PlantUMLSequenceExporter

from tests.integrations import TESTS_INTEGRATIONS_FOLDER, _get_file_suffix, integration_test
from tests.modules.factorial import (
    factorial_recursive,
    factorial_recursive_check_handled,
    factorial_recursive_check_unhandled,
    factorial_reduce_lambda,
    factorial_reduce_multiply,
    factorial_with_checker,
)


@mark.parametrize('exporter_class', [PlantUMLSequenceExporter, PlantUMLComponentExporter])
@mark.parametrize(
    ['factorial_function', 'input_param', 'expected_output'],
    [
        (factorial_recursive, 6, 720),
        (factorial_reduce_lambda, 6, 720),
        (factorial_reduce_multiply, 6, 720),
    ],
)
def test_factorial_tracing(exporter_class: Type, factorial_function: Callable, input_param: int, expected_output: int):
    suffix = _get_file_suffix(exporter_class)
    integration_test(
        TESTS_INTEGRATIONS_FOLDER
        / 'factorial'
        / f'test_{factorial_function.__name__}-{input_param}-{expected_output}-{suffix}.puml',
        expected_output,
        factorial_function,
        (input_param,),
        None,
        exporter_class,
        # overwrite_expected_contents=True,
    )


@mark.parametrize('exporter_class', [PlantUMLSequenceExporter, PlantUMLComponentExporter])
def test_factorial_unhandled_error(exporter_class):
    suffix = _get_file_suffix(exporter_class)
    with raises(ValueError) as value_error:
        integration_test(
            TESTS_INTEGRATIONS_FOLDER
            / 'factorial'
            / f'test_handled_error-factorial_recursive_check_unhandled-None-ValueError-{suffix}.puml',
            None,
            factorial_recursive_check_unhandled,
            (None,),
            None,
            exporter_class,
            # overwrite_expected_contents=True,
        )
    assert str(value_error.value) == 'Value must be a positive integer, got None.'


@mark.parametrize('exporter_class', [PlantUMLSequenceExporter, PlantUMLComponentExporter])
@mark.parametrize(
    ['factorial_function', 'invalid_input_param', 'expected_output'],
    [
        (factorial_recursive_check_handled, 'invalid_int', 0),
        (factorial_with_checker, 'int_is_resting', None),
    ],
)
def test_factorial_handled_error(exporter_class, factorial_function, invalid_input_param, expected_output):
    suffix = _get_file_suffix(exporter_class)

    integration_test(
        TESTS_INTEGRATIONS_FOLDER
        / 'factorial'
        / f'test_handled_error-{factorial_function.__name__}-{invalid_input_param}-{expected_output}-{suffix}.puml',
        expected_output,
        factorial_function,
        (invalid_input_param,),
        None,
        exporter_class,
        # overwrite_expected_contents=True,
    )
