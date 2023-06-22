from pytest import raises

from pydoctrace.doctrace import trace_to_sequence_puml

from tests.modules.factorial import (
    factorial_recursive, factorial_recursive_check_handled, factorial_recursive_check_unhandled,
    factorial_reduce_lambda, factorial_reduce_multiply, factorial_with_checker
)


def test_factorial_recursive_sequence():
    tracable_factorial_recursive = trace_to_sequence_puml(factorial_recursive)
    assert tracable_factorial_recursive(6) == 720


def test_factorial_reduce_lambda_sequence():
    tracable_factorial_reduce_lambda = trace_to_sequence_puml(factorial_reduce_lambda)
    assert tracable_factorial_reduce_lambda(6) == 720


def test_factorial_reduce_multiply_sequence():
    tracable_factorial_reduce_multiply = trace_to_sequence_puml(factorial_reduce_multiply)
    assert tracable_factorial_reduce_multiply(6) == 720


def test_factorial_recursive_check_unhandled_sequence():
    tracable_factorial_recursive_check_unhandled = trace_to_sequence_puml(factorial_recursive_check_unhandled)
    with raises(ValueError) as value_error:
        tracable_factorial_recursive_check_unhandled(None)
    assert str(value_error.value) == 'Value must be a positive integer, got None.'


def test_factorial_recursive_check_handled_sequence():
    tracable_factorial_recursive_check_handled = trace_to_sequence_puml(factorial_recursive_check_handled)
    assert tracable_factorial_recursive_check_handled('invalid int') == 0


def test_factorial_with_checker_sequence():
    tracable_factorial_with_checker = trace_to_sequence_puml(factorial_with_checker)
    assert tracable_factorial_with_checker('int is resting') is None
