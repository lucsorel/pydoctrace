from typing import Any, Callable


def is_positive_int(value: Any):
    if not (isinstance(value, int) and value >= 0):
        message = f'Value must be a positive integer, got {value}.'
        raise_value_error(message)


def raise_value_error(message: str):
    raise ValueError(message)


class FactorialError(BaseException):
    pass


def log_factorial_error(factorial_error: FactorialError):
    # print(f'Got error {factorial_error}')
    pass


def check_or_wrap_error(value_to_check: Any, validator: Callable) -> Any:
    try:
        if validator(value_to_check):
            return value_to_check
    except BaseException:
        raise FactorialError() from None
