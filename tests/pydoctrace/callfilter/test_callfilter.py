from typing import Tuple

from pytest import mark

from pydoctrace.callfilter import (
    FILTER_OUT_STDLIB,
    TRACE_ALL_FILTER,
    TRACE_NONE_FILTER,
    CallFilter,
    call_filter_factory,
)
from pydoctrace.callfilter.presets import Preset


def test_callfilter_inclusion_over_exclusion_at_the_preset_level():
    exclude_package_include_function_preset = Preset(
        # excludes everything in the 'my_package' package
        exclude_call=lambda module_parts, *args: len(module_parts) > 0 and module_parts[0] == 'my_package',
        # but includes any functions called 'my_function'
        include_call=lambda module_parts, function_name, *args: function_name == 'my_function',
    )
    callfilter = CallFilter((exclude_package_include_function_preset,))
    assert callfilter.should_trace_call(('my_package', 'my_module'), 'my_function', 1), 'my_function should be traced'
    assert not callfilter.should_trace_call(
        ('my_package', 'my_module'), 'my_other_function', 1
    ), 'my_other_function should not be traced'


def test_callfilter_exclusion_over_inclusion_across_presets():
    """
    The callfilter excludes a call from the tracing as soon as a preset excludes it, whatever the presets order.
    """
    excluding_preset = Preset(
        # excludes everything in the 'my_package' package
        exclude_call=lambda module_parts, *args: len(module_parts) > 0 and module_parts[0] == 'my_package',
    )
    including_preset = Preset(
        # excludes nothing
        exclude_call=lambda *args: False
    )

    callfilter = CallFilter((excluding_preset, including_preset))
    assert not callfilter.should_trace_call(
        ('my_package', 'my_module'), 'my_function', 1
    ), 'my_function should not be traced'

    other_filter = CallFilter((including_preset, excluding_preset))
    assert not other_filter.should_trace_call(
        ('my_package', 'my_module'), 'my_function', 1
    ), 'my_function should not be traced'


@mark.parametrize(
    ['callfilter', 'module_parts', 'function_name', 'expected_filtering'],
    [
        (FILTER_OUT_STDLIB, isinstance.__module__.split('.'), isinstance.__name__, False),
        (FILTER_OUT_STDLIB, ('my_package', 'my_module'), 'my_function', True),
        # always traces the calls
        (TRACE_ALL_FILTER, isinstance.__module__.split('.'), isinstance.__name__, True),
        (TRACE_ALL_FILTER, ('my_package', 'my_module'), 'my_function', True),
        # never traces the calls
        (TRACE_NONE_FILTER, isinstance.__module__.split('.'), isinstance.__name__, False),
        (TRACE_NONE_FILTER, ('my_package', 'my_module'), 'my_function', False),
    ],
)
def test_callfilter_should_trace_call(
    callfilter: CallFilter, module_parts: Tuple[str], function_name: str, expected_filtering: bool
):
    assert callfilter.should_trace_call(module_parts, function_name, 1) is expected_filtering


@mark.parametrize(
    'empty_presets',
    [
        (None),
        (()),
        ([]),
    ],
)
def test_call_filter_factory_with_empty_presets(empty_presets: Tuple[Preset]):
    callfilter = call_filter_factory(empty_presets)
    assert len(callfilter.presets) == 0
    assert callfilter is TRACE_ALL_FILTER
    assert callfilter.should_trace_call(('my_package', 'my_module'), 'my_function', 1), 'always trace'
