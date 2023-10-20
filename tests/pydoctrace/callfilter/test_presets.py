from pydoctrace.callfilter.presets import FILTER_OUT_BUILTINS


def test_filter_out_builtins():
    assert FILTER_OUT_BUILTINS.exclude_call(
        isinstance.__module__.split('.')
    ), 'call to isinstance must not be traced with this preset'
