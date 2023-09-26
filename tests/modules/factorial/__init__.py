from functools import reduce

from tests.modules.factorial.validator import FactorialError, check_or_wrap_error, is_positive_int, log_factorial_error


def factorial_recursive(value: int) -> int:
    if value <= 1:
        return value

    return value * factorial_recursive(value - 1)


def factorial_recursive_check_unhandled(value: int) -> int:
    is_positive_int(value)

    return factorial_recursive(value)


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


def factorial_with_checker(value: int):
    try:
        return factorial_reduce_multiply(check_or_wrap_error(value, is_positive_int))
    except FactorialError as factorial_error:
        log_factorial_error(factorial_error)

        return None
