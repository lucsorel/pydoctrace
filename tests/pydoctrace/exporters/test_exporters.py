from pytest import raises

from pydoctrace.exporters import Exporter


def test_exporter_must_implement_on_header():
    exporter = Exporter(None)
    with raises(NotImplementedError):
        exporter.on_header('module_start', 'func_name_start')


def test_exporter_must_implement_on_tracing_start():
    exporter = Exporter(None)
    with raises(NotImplementedError):
        exporter.on_tracing_start(called=None)


def test_exporter_must_implement_on_start_call():
    exporter = Exporter(None)
    with raises(NotImplementedError):
        exporter.on_start_call(caller=None, called=None)


def test_exporter_must_implement_format_arg_value():
    exporter = Exporter(None)
    with raises(NotImplementedError):
        exporter.format_arg_value(arg=None)


def test_exporter_must_implement_on_error_propagation():
    exporter = Exporter(None)
    with raises(NotImplementedError):
        exporter.on_error_propagation(error_called=None, error_caller=None, error=None)


def test_exporter_must_implement_on_return():
    exporter = Exporter(None)
    with raises(NotImplementedError):
        exporter.on_return(called=None, caller=None, arg=None)


def test_exporter_must_implement_on_tracing_end():
    exporter = Exporter(None)
    with raises(NotImplementedError):
        exporter.on_tracing_end(called=None, arg=None)


def test_exporter_must_implement_on_unhandled_error_end():
    exporter = Exporter(None)
    with raises(NotImplementedError):
        exporter.on_unhandled_error_end(called=None, error=None)


def test_exporter_must_implement_on_footer():
    exporter = Exporter(None)
    with raises(NotImplementedError):
        exporter.on_footer()
