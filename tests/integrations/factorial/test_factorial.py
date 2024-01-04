from typing import Callable

from pytest import mark, raises

from pydoctrace.doctrace import trace_to_component_puml, trace_to_sequence_puml

from tests.modules.factorial import (
    factorial_recursive,
    factorial_recursive_check_handled,
    factorial_recursive_check_unhandled,
    factorial_reduce_lambda,
    factorial_reduce_multiply,
    factorial_with_checker,
)


@mark.parametrize(
    ['factorial_function', 'input_param', 'expected_output'],
    [
        (factorial_recursive, 6, 720),
        (factorial_reduce_lambda, 6, 720),
        (factorial_reduce_multiply, 6, 720),
    ],
)
def test_factorial_sequence(factorial_function: Callable, input_param: int, expected_output: int):
    tracable_factorial_function = trace_to_sequence_puml(factorial_function)
    assert tracable_factorial_function(input_param) == expected_output


@mark.parametrize(
    ['factorial_function', 'input_param', 'expected_output'],
    [
        (factorial_recursive, 6, 720),
        (factorial_reduce_lambda, 6, 720),
        (factorial_reduce_multiply, 6, 720),
    ],
)
def test_factorial_component(factorial_function: Callable, input_param: int, expected_output: int):
    tracable_factorial_function = trace_to_component_puml(factorial_function)
    assert tracable_factorial_function(input_param) == expected_output


def test_factorial_recursive_check_unhandled_sequence():
    tracable_factorial_recursive_check_unhandled = trace_to_sequence_puml(factorial_recursive_check_unhandled)
    with raises(ValueError) as value_error:
        tracable_factorial_recursive_check_unhandled(None)
    assert str(value_error.value) == 'Value must be a positive integer, got None.'


def test_factorial_recursive_check_unhandled_component():
    tracable_factorial_recursive_check_unhandled = trace_to_component_puml(factorial_recursive_check_unhandled)
    with raises(ValueError) as value_error:
        tracable_factorial_recursive_check_unhandled(None)
    assert str(value_error.value) == 'Value must be a positive integer, got None.'


def test_factorial_recursive_check_handled_sequence():
    tracable_factorial_recursive_check_handled = trace_to_sequence_puml(factorial_recursive_check_handled)
    assert tracable_factorial_recursive_check_handled('invalid int') == 0


def test_factorial_recursive_check_handled_component():
    tracable_factorial_recursive_check_handled = trace_to_component_puml(factorial_recursive_check_handled)
    assert tracable_factorial_recursive_check_handled('invalid int') == 0


def test_factorial_with_checker_sequence():
    tracable_factorial_with_checker = trace_to_sequence_puml(factorial_with_checker)
    assert tracable_factorial_with_checker('int is resting') is None


def test_factorial_with_checker_component():
    tracable_factorial_with_checker = trace_to_component_puml(factorial_with_checker)
    assert tracable_factorial_with_checker('int is resting') is None
