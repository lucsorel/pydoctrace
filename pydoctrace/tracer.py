"""
Module responsible for the execution of a function in a tracing context.

The tracing is based on the sys.settrace hook system, which takes:
- a global tracing function intercepting the calls to block of codes
- a local tracing function, returned by the global tracing function, handling:
  - the line executions (ignored by this tool)
  - the exit of the function (when returning a value or raising an error)
- an exception tracing function, returned by the local tracing function, handling either the error propagation
  or its handling by a try-except block
"""

from collections import deque
from pathlib import Path
from sys import gettrace, settrace
from typing import Any, Callable, List, NamedTuple, Tuple

from pydoctrace.callfilter import CallFilter
from pydoctrace.domain.execution import CallEnd, Error
from pydoctrace.exporters import Exporter


class TracedError(NamedTuple):
    """
    An error being traced by the tracer, holding metadata:
    - error: Error: information for display purposes in the diagram
    - line_index: int: the line at which the error entered the execution frame
    - exception: BaseException: the corresponding Python exception being traced
    """

    error: Error
    line_index: int


def module_name_from_filepath(script_filepath: str) -> str:
    """Return a plausible module name for the script_filepath."""
    # base = os.path.basename(script_filepath)
    # filename, _ = os.path.splitext(base)
    # return filename
    return None if script_filepath is None else Path(script_filepath).stem


class ExecutionTracer:
    """
    Traces the execution of a callable object and pushes events to the given exporter.

    The implementation of the tracing functions are based on the documentation of:
    - sys.settrace: https://docs.python.org/3/library/sys.html#sys.settrace
    - execution frames: https://docs.python.org/3/reference/datamodel.html#frame-objects

    Useful calls when implementing or debugging features (the contents are added as PlantUML comments in the exported diagram):
    self.exporter.on_raw_content(f"\n' {event} {frame=} {arg=}\n")
    self.exporter.on_raw_content(f"' {frame.f_back=}\n")
    """

    def __init__(self, exporter: Exporter, call_filter: CallFilter):
        self.exporter = exporter
        self.call_filter = call_filter
        self.callers_stack: List[CallEnd] = deque()
        self.error_to_handle_with_line: TracedError = None

    def runfunc(self, func: Callable, *args, **kwargs) -> Any:
        """
        Runs the given function with the given positional and keyword arguments and traces the calls sequence.
        """

        # ensures that a callable object has been passed
        if func is None or not callable(func):
            raise ValueError('A function or a callable object must be passed to trace its execution')

        # declares the tracing callbacks to trace calls, performs and traces the call, then removes the tracer
        tracing_function = gettrace()
        settrace(self.globaltrace)
        try:
            return func(*args, **kwargs)
        finally:
            settrace(tracing_function)

    def on_return_or_exit(self, called_end: CallEnd, arg: Any):
        # the calls stack is empty -> end of the tracing
        if len(self.callers_stack) == 0:
            self.exporter.on_tracing_end(called_end, arg)
        # normal return call
        else:
            self.exporter.on_return(called=called_end, caller=self.callers_stack[-1], arg=arg)

    def error_from_exception(self, exception: BaseException) -> Error:
        error_args = getattr(exception, 'args', None)
        error_message = repr(exception) if error_args is None or len(error_args) == 0 else error_args[0]

        return Error(exception.__class__.__name__, error_message)

    def get_module_path_and_function_name(self, frame) -> Tuple[str, str]:
        fq_module_text: str = frame.f_globals.get('__name__', None)
        if fq_module_text is None:
            fq_module_text = module_name_from_filepath(frame.f_globals.get('__file__', None))

        return fq_module_text, frame.f_code.co_name

    def globaltrace(self, frame, event: str, arg: Any):
        """
        Handler for call events.

        Returns:
        - a custom tracing function to trace the execution of the block
        - None if the execution block should be ignored
        """

        if event == 'call':
            # self.exporter.on_raw_content(f"\n' {event} {arg=}")
            # self.exporter.on_raw_content(f"\n' frame.f_globals={ {**frame.f_globals, '__builtins__':None, '__doc__':None}}")
            # self.exporter.on_raw_content(f"\n' {frame.f_locals=}")
            # # self.exporter.on_raw_content(f"\n' {getattr(frame.f_code, 'co_qualname', None)=}")
            # self.exporter.on_raw_content(f"\n' {frame.f_code.co_name=}\n")
            fq_module_text, function_name = self.get_module_path_and_function_name(frame)
            fq_module_parts = tuple(fq_module_text.split('.'))

            # determines whether the call should be traced or not
            if not self.call_filter.should_trace_call(fq_module_parts, function_name, len(self.callers_stack)):
                return None

            # constructs the call
            line_index = frame.f_lineno
            call = CallEnd(fq_module_text, fq_module_parts, function_name, line_index)

            # starts the tracing or handle an intermediary call
            if len(self.callers_stack) == 0:
                self.exporter.on_tracing_start(call)
            else:
                self.exporter.on_start_call(self.callers_stack[-1]._replace(line_index=frame.f_back.f_lineno), call)

            # unflags any error remaining from localtrace without return event
            self.error_to_handle_with_line = None

            # adds the call to the calls stack and returns the call tracing function to detect 'return' or 'exception' events
            self.callers_stack.append(call)

            return self.localtrace

    def localtrace(self, frame, event: str, arg: Any):
        """
        Handler for events happening within a call:
        - 'return' event: ends the current call, removes it from the callers stack

        When an 'exception' occurs:
        - localtrace:exception and exceptiontrace:return have the same line number (localtrace:return is not called) -> propagate the error to the caller
        - localtrace:exception and localtrace:return have the same line number (exceptiontrace:return is not called) -> propagate the error to the caller
        - localtrace:exception and exceptiontrace:return have different line numbers (localtrace:return is not called) -> classic return to the caller

        In all cases:
        - localtrace:exception should flag the error and the line at which it occured (in the tracer)
        - exceptiontrace:exception overrides the previous error (happens when an error is caught and another one is raised in an except block)
        - localtrace:return (when an error is flagged in the tracer) or exceptiontrace:return (there should always be an error in the tracer):
          - if their line numbers are the same -> it is an error propagation
          - if their line numbers are different -> the error has been handled, it is a classic return event
        """

        if event == 'exception':
            # creates the error and flags it so that it can be handled either by the localtrace or exceptiontrace
            error = self.error_from_exception(arg[1])
            self.error_to_handle_with_line = TracedError(error, frame.f_lineno)

            # uses the exception tracing
            return self.exceptiontrace

        elif event == 'return':
            # classic return when the error has been handled internally (in an except block)
            if self.error_to_handle_with_line is None:
                # end of the block code: removes the last caller from the stack
                called_end = self.callers_stack.pop()._replace(line_index=frame.f_lineno)
                self.on_return_or_exit(called_end, arg)
            # propagates the error to the caller
            else:
                error, _ = self.error_to_handle_with_line
                error_called = self.callers_stack.pop()._replace(line_index=frame.f_lineno)
                error_caller = self.callers_stack[-1]._replace(line_index=frame.f_back.f_lineno)
                self.exporter.on_error_propagation(error_called, error_caller, error)

                # unflags the error
                self.error_to_handle_with_line = None

        return self.localtrace

    def exceptiontrace(self, frame, event: str, arg: Any):
        # a new exception enters the frame (re-raised, replaced or wrapped)
        if event == 'exception':
            error = self.error_from_exception(arg[1])
            self.error_to_handle_with_line = TracedError(error, frame.f_lineno)

        elif event == 'return':
            # the error has been internally handled, a classic return occurs
            if self.error_to_handle_with_line is None:
                called_end = self.callers_stack.pop()._replace(line_index=frame.f_lineno)
                self.on_return_or_exit(called_end, arg)
            # handles the flagged error
            else:
                error, line_number_called = self.error_to_handle_with_line
                line_number = frame.f_lineno

                # error propagation
                if line_number == line_number_called:
                    error_called = self.callers_stack.pop()._replace(line_index=line_number)
                    # exits the tracing if there is no caller anymore
                    if len(self.callers_stack) == 0:
                        self.exporter.on_unhandled_error_end(error_called, error)
                    else:
                        error_caller = self.callers_stack[-1]._replace(line_index=frame.f_back.f_lineno)
                        self.exporter.on_error_propagation(error_called, error_caller, error)

                # error was handled, normal return
                else:
                    called_end = self.callers_stack.pop()._replace(line_index=frame.f_lineno)
                    self.on_return_or_exit(called_end, arg)

                # unflags the error
                self.error_to_handle_with_line = None

        return self.exceptiontrace
