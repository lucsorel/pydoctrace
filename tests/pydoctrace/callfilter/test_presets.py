from typing import Tuple, Type

from pytest import mark, raises

from pydoctrace.callfilter.presets import (
    EXCLUDE_BUILTINS_PRESET,
    EXCLUDE_CALL_DEPTH_PRESET_FACTORY,
    EXCLUDE_DEPTH_BELOW_5_PRESET,
    EXCLUDE_STDLIB_PRESET,
    EXCLUDE_TESTS_PRESET,
    TRACE_ALL_PRESET,
    Preset,
    _depth_preset_factory,
)


def test_filter_builtins_isinstance_out():
    assert EXCLUDE_BUILTINS_PRESET.exclude_call(isinstance.__module__.split('.'), isinstance.__name__, 1), (
        'call to isinstance must not be traced with the builtins preset'
    )


def test_filter_builtins_function_in():
    assert not EXCLUDE_BUILTINS_PRESET.exclude_call(('package', 'module'), 'function', 1), (
        'call to function must be traced with the builtins preset'
    )


def test_filter_stdlib_isinstance_out():
    assert EXCLUDE_STDLIB_PRESET.exclude_call(isinstance.__module__.split('.'), isinstance.__name__, 1), (
        'call to isinstance must not be traced with the stdlib preset'
    )


def test_filter_stdlib_function_in():
    assert not EXCLUDE_STDLIB_PRESET.exclude_call(('package', 'module'), 'function', 1), (
        'call to function not traced with the stdlib preset'
    )


def test_filter_test_isinstance_in():
    assert not EXCLUDE_TESTS_PRESET.exclude_call(isinstance.__module__.split('.'), isinstance.__name__, 1), (
        'call to isinstance must be traced with the tests preset'
    )


def test_filter_test_raises_in():
    assert EXCLUDE_TESTS_PRESET.exclude_call(raises.__module__.split('.'), raises.__name__, 1), (
        'call to raises must not be traced with the tests preset'
    )


@mark.parametrize(
    ['module_parts', 'function_name'],
    [
        (isinstance.__module__.split('.'), isinstance.__name__),
        (raises.__module__.split('.'), raises.__name__),
        (('package', 'module'), 'function'),
    ],
)
def test_trace_all_preset(module_parts: Tuple[str], function_name: str):
    assert not TRACE_ALL_PRESET.exclude_call(module_parts, function_name, 1), 'TRACE_ALL_PRESET always allow tracing'


@mark.parametrize(
    ['invalid_depth_threshold', 'expected_error_class', 'expected_error_message'],
    [
        (None, TypeError, 'depth threshold must be an integer'),
        ('zero', TypeError, 'depth threshold must be an integer'),
        (1.0, TypeError, 'depth threshold must be an integer'),
        (-1, ValueError, "depth threshold must be a positive integer, got '-1'"),
    ],
)
def test_depth_preset_factory_with_invalid_values(
    invalid_depth_threshold, expected_error_class: Type, expected_error_message: str
):
    with raises(expected_error_class) as expected_error:
        _depth_preset_factory(invalid_depth_threshold)

    assert str(expected_error.value) == expected_error_message


def test_depth_preset_factory_depth_one():
    preset = _depth_preset_factory(1)
    assert isinstance(preset, Preset)
    assert preset.include_call is None, 'no include_call feature for depth-1 preset'
    module_parts = 'package', 'module'
    function_name = 'function'
    assert not preset.exclude_call(module_parts, function_name, 0), '0-depth call is traced'
    assert not preset.exclude_call(module_parts, function_name, 1), '1-depth call is traced'
    assert preset.exclude_call(module_parts, function_name, 2), '2-depth call is not traced'


def test_exclude_call_depth_preset_factory():
    above_3_preset = EXCLUDE_CALL_DEPTH_PRESET_FACTORY(3)
    assert isinstance(above_3_preset, Preset)
    assert above_3_preset.include_call is None
    module_parts = 'package', 'module'
    function_name = 'function'
    assert not above_3_preset.exclude_call(module_parts, function_name, 1)
    assert not above_3_preset.exclude_call(module_parts, function_name, 2)
    assert not above_3_preset.exclude_call(module_parts, function_name, 3)
    assert above_3_preset.exclude_call(module_parts, function_name, 4)
    assert above_3_preset.exclude_call(module_parts, function_name, 5)


@mark.parametrize(
    ['call_depth', 'expected_exclusion'],
    [
        (0, False),
        (1, False),
        (2, False),
        (3, False),
        (4, False),
        (5, False),
        (6, True),
        (10, True),
    ],
)
def test_exclude_depth_below_5_preset(call_depth: int, expected_exclusion: bool):
    module_parts = 'package', 'module'
    function_name = 'function'
    assert EXCLUDE_DEPTH_BELOW_5_PRESET.exclude_call(module_parts, function_name, call_depth) == expected_exclusion
