from io import StringIO
from typing import Tuple

from pytest import fixture, mark, raises

from pydoctrace.callfilter import TRACE_ALL_FILTER
from pydoctrace.domain.execution import CallEnd, Error
from pydoctrace.exporters.plantuml.sequence import PlantUMLSequenceExporter
from pydoctrace.tracer import ExecutionTracer


@fixture(scope='function')
def sequence_exporter_and_writer() -> Tuple[PlantUMLSequenceExporter, StringIO]:
    exported_contents = StringIO()
    exporter = PlantUMLSequenceExporter(exported_contents)

    return exporter, exported_contents


@mark.parametrize(
    'not_a_callable',
    [
        (None,),
        ('text',),
    ],
)
def test_executiontracer_runfunc_without_callable(not_a_callable):
    with raises(ValueError) as ve:
        ExecutionTracer(None, None).runfunc(None)

    assert str(ve.value) == 'A function or a callable object must be passed to trace its execution'


@mark.parametrize(
    ['current_callers_stack', 'call_end', 'arg', 'expected_contents_lines'],
    [
        # returns the value from the called to the caller
        (
            [CallEnd('math_cli.controller', ('math_cli', 'controller'), 'factorial', 25)],
            CallEnd('math_cli.validator', ('math_cli', 'validator'), 'is_positive_int', 4),
            24,
            [
                'return 24',
                'note right: line 4',
                '|||',
            ],
        ),
        # exits tracing with the returned value from the caller
        (
            [],
            CallEnd('math_cli.controller', ('math_cli', 'controller'), 'factorial', 25),
            24,
            [
                '[<-- "math_cli.controller\\nfactorial": 24',
                'note right: line 25',
            ],
        ),
    ],
)
def test_executiontracer_on_return_or_exit(
    sequence_exporter_and_writer: Tuple[PlantUMLSequenceExporter, StringIO],
    current_callers_stack,
    call_end,
    arg,
    expected_contents_lines,
):
    exporter, contents_writer = sequence_exporter_and_writer

    tracer = ExecutionTracer(exporter, TRACE_ALL_FILTER)
    tracer.callers_stack.extend(current_callers_stack)
    tracer.on_return_or_exit(call_end, arg)

    assert contents_writer.getvalue() == '\n' + '\n'.join(expected_contents_lines) + '\n'


@mark.parametrize(
    ['exception', 'expected_error'],
    [
        (NotImplementedError(), Error('NotImplementedError', 'NotImplementedError()')),
        (ValueError('value must be positive'), Error('ValueError', 'value must be positive')),
    ],
)
def test_executiontracer_error_from_exception(exception, expected_error):
    assert ExecutionTracer(None, None).error_from_exception(exception) == expected_error
