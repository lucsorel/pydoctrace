from pydoctrace.doctrace import trace_to_sequence_puml

from tests.modules.fibonacci import fibonacci


def test_fibonacci_valid_cases_sequence():
    tracable_fibonacci = trace_to_sequence_puml(fibonacci)
    assert tracable_fibonacci(4) == 3
