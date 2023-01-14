# quantiles
ELEMENTS_NB_QUANTILES = (
    0, 47, 75, 159, 233, 298, 358, 417, 476, 537, 603, 674, 753, 843, 949, 1076, 1237, 1459, 1801, 2479, 594601
)
REQUESTS_NB_QUANTILES = (0, 2, 15, 25, 34, 42, 49, 56, 63, 70, 78, 86, 95, 105, 117, 130, 147, 170, 205, 281, 3920)
SIZES_KB_QUANTILES = (
    0, 1.37, 144.7, 319.53, 479.46, 631.97, 783.38, 937.91, 1098.62, 1265.47, 1448.32, 1648.27, 1876.08, 2142.06,
    2465.37, 2866.31, 3401.59, 4155.73, 5400.08, 8037.54, 223212.26
)


def to_quantile_position(value: float, quantiles: tuple) -> float:
    if value is None or value < 0:
        raise ValueError('value must be a positive number')

    for lower_index, upper_value in enumerate(quantiles[1:]):
        if upper_value > value:
            lower_value = quantiles[lower_index]
            interpolated_position = lower_index + (value - lower_value) / (upper_value - lower_value)
            break
    else:
        # value is above the max threshold -> returns the maximum note (20)
        interpolated_position = len(quantiles) - 1

    return interpolated_position


def ecoindex(dom_elements_nb: int, requests_nb: int, size_kb: float) -> float:
    dom_quantile: float = to_quantile_position(dom_elements_nb, ELEMENTS_NB_QUANTILES)
    requests_quantile: float = to_quantile_position(requests_nb, REQUESTS_NB_QUANTILES)
    size_quantile: float = to_quantile_position(size_kb, SIZES_KB_QUANTILES)

    return 100 - (5 * (3 * dom_quantile + 2 * requests_quantile + size_quantile) / 6)
