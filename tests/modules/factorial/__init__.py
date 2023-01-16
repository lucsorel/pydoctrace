from functools import reduce

from tests.modules.factorial.validator import is_positive_int


def factorial_recursive(value: int) -> int:
    if value <= 1:
        return value

    return value * factorial_recursive(value - 1)


def factorial_recursive_check_unhandled(value: int) -> int:
    if not (isinstance(value, int) and value >= 0):
        raise ValueError(f'Value must be a positive integer, got {value}.')
    if value <= 1:
        return value

    return value * factorial_recursive(value - 1)


def factorial_recursive_check_handled(value: int) -> int:
    try:
        is_positive_int(value)
    except ValueError:
        return 0

    if value <= 1:
        return value

    return value * factorial_recursive(value - 1)


def factorial_reduce_lambda(value: int) -> int:
    if value <= 1:
        return value

    return reduce(lambda agg, index: agg * index, range(1, value + 1), 1)


def factorial_reduce_multiply(value: int) -> int:
    if value <= 1:
        return value

    def multiply(agg: int, value: int) -> int:
        return agg * value

    return reduce(multiply, range(1, value + 1), 1)
