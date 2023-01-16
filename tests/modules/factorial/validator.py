def is_positive_int(value):
    if not (isinstance(value, int) and value >= 0):
        message = f'Value must be a positive integer, got {value}.'
        raise_value_error(message)
        # raise ValueError(message)


def raise_value_error(message: str):
    raise ValueError(message)
