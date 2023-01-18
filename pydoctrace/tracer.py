from collections import deque
from pathlib import Path
from sys import settrace
from typing import Any, Callable, List, Tuple

from pydoctrace.domain.sequence import Call, Error
from pydoctrace.exporters import Exporter

# idée complémentaire : dessiner un diagramme de modules avec des liens entre les fonctions qui s'appellent les unes les autres
# -> https://plantuml.com/fr/activity-diagram-beta § Regroupement ou partition
# -> https://plantuml.com/fr/deployment-diagram avec des components ou packages pour les modules


def module_name_from_filepath(script_filepath: str) -> str:
    '''Return a plausible module name for the script_filepath.'''
    # base = os.path.basename(script_filepath)
    # filename, _ = os.path.splitext(base)
    # return filename
    return None if script_filepath is None else Path(script_filepath).stem


class SequenceTracer:
    '''
    Traces the execution of a callable object and pushes events to the given exporter.

    The implementation of the tracing functions are based on the documentation of:
    - sys.settrace: https://docs.python.org/3/library/sys.html#sys.settrace
    - execution frames: https://docs.python.org/3/reference/datamodel.html#frame-objects

    Useful call when debugging: self.exporter.write_raw_content(f"' {event} {frame=} {arg=}\n")
    '''
    def __init__(self, exporter: Exporter):
        self.exporter = exporter
        self.callers_stack: List[Call] = deque()
        self.error_to_handle_with_line: Tuple[Error, int] = None

    def runfunc(self, func: Callable, *args, **kwargs) -> Any:
        '''
        Runs the given function with the given positional and keyword arguments and traces the calls sequence.
        '''

        # ensures that a callable object has been passed
        if func is None or not callable(func):
            raise ValueError('A function or a callable object must be passed to trace its execution')

        # declares the tracing callbacks to trace calls, performs and traces the call, then removes the tracer
        settrace(self.globaltrace)
        try:
            return func(*args, **kwargs)
        finally:
            settrace(None)

    def write_return_or_exit(self, called_end: Call, arg: Any):
        # the calls stack is empty -> end of the tracing
        if len(self.callers_stack) == 0:
            self.exporter.write_tracing_end(called_end, arg)
        # normal return call
        else:
            self.exporter.write_return(called_end, arg)

    def globaltrace(self, frame, event: str, arg: Any):
        '''
        Handler for call events.

        Returns:
        - a custom tracing function to trace the execution of the block
        - None if the execution block should be ignored
        '''

        self.exporter.write_raw_content(f"\n' g:{event} {frame=} {arg=}\n")
        self.exporter.write_raw_content(f"' {frame.f_back=}\n")
        if event == 'call':
            # constructs the call
            fq_module_text: str = frame.f_globals.get('__name__', None)
            if fq_module_text is None:
                fq_module_text = module_name_from_filepath(frame.f_globals.get('__file__', None))
            line_index = frame.f_lineno
            function_name = frame.f_code.co_name
            call = Call(fq_module_text, tuple(fq_module_text.split('.')), function_name, line_index)

            # starts the tracing or handle an intermediary call
            if len(self.callers_stack) == 0:
                self.exporter.write_tracing_start(call)
            else:
                self.exporter.write_start_call(self.callers_stack[-1]._replace(line_index=frame.f_back.f_lineno), call)

            # adds the call to the calls stack and returns the call tracing function to detect 'return' or 'exception' events
            self.callers_stack.append(call)

            return self.localtrace

    def localtrace(self, frame, event: str, arg: Any):
        '''
        Handler for events happening within a call:
        - 'return' event: ends the current call, removes it from the callers stack

        When an 'exception' occurs:
        - localtrace:exception and exceptiontrace:return have the same line number (localtrace:return is not called) -> propagate the error to the caller
        - localtrace:exception and localtrace:return have the same line number (exceptiontrace:return is not called) -> propagate the error to the caller
        - localtrace:exception and exceptiontrace:return have different line numbers (localtrace:return is not called) -> classic return to the caller

        In all cases:
        - localtrace:exception should flag the error and the line at which it occured (in the tracer)
        - localtrace:return (when an error is flagged in the tracer) or exceptiontrace:return (there should always be an error in the tracer):
          - if their line numbers are the same -> it is an error propagation
          - if their line numbers are different -> the error has been handled, it is a classic return event
        '''

        self.exporter.write_raw_content(f"\n' l:{event} {frame=} {arg=}\n")
        self.exporter.write_raw_content(f"' {frame.f_back=}\n")
        self.exporter.write_raw_content(f"' {self.error_to_handle_with_line=}\n")
        if event == 'exception':
            # creates the error and flags it so that it can be handled either by the localtrace or exceptiontrace
            error_class, exception, _ = arg
            error_args = getattr(exception, 'args', None)
            if error_args is None or len(error_args) == 0:
                error_message = repr(exception)
            else:
                error_message = error_args[0]
            error = Error(error_class.__name__, error_message)

            error = Error(error_class.__name__, getattr(error, 'args', (None, ))[0] or repr(error))
            self.error_to_handle_with_line = error, frame.f_lineno

            # uses the exception tracing
            self.exporter.write_raw_content(f"' l:exc {self.error_to_handle_with_line=}\n")
            return self.exceptiontrace

        elif event == 'return':
            # returns the value or propagates the error if any
            if self.error_to_handle_with_line is None:
                # end of the block code: removes the last caller from the stack
                called_end = self.callers_stack.pop()._replace(line_index=frame.f_lineno)
                self.write_return_or_exit(called_end, arg)

            else:
                error, _ = self.error_to_handle_with_line
                error_called = self.callers_stack.pop()._replace(line_index=frame.f_lineno)
                error_caller = self.callers_stack[-1]._replace(line_index=frame.f_back.f_lineno)
                self.exporter.write_error_propagation(error_called, error_caller, error)

                # unflags the error
                self.error_to_handle_with_line = None

        self.exporter.write_raw_content(f"' l:ret {self.error_to_handle_with_line=}\n")
        return self.localtrace

    def exceptiontrace(self, frame, event: str, arg: Any):
        self.exporter.write_raw_content(f"\n' e:{event} {frame=} {arg=}\n")
        self.exporter.write_raw_content(f"' {frame.f_back=}\n")
        self.exporter.write_raw_content(f"' {self.error_to_handle_with_line=}\n")
        if event == 'return':
            if self.error_to_handle_with_line is None:
                self.exporter.write_raw_content("' e:ret without error\n")
            else:
                # handles the flagged error
                error, line_number_called = self.error_to_handle_with_line
                line_number = frame.f_lineno

                # error propagation
                self.exporter.write_raw_content(f"' e:ret {line_number=} {line_number_called=}\n")
                if line_number == line_number_called:
                    error_called = self.callers_stack.pop()._replace(line_index=line_number)
                    # exits the tracing if there is no caller anymore
                    if len(self.callers_stack) == 0:
                        self.exporter.write_unhandled_error_end(error_called, error)
                    else:
                        error_caller = self.callers_stack[-1]._replace(line_index=frame.f_back.f_lineno)
                        self.exporter.write_error_propagation(error_called, error_caller, error)

                    # unflags the error
                    self.error_to_handle_with_line = None

                # error was handled, normal return
                else:
                    called_end = self.callers_stack.pop()._replace(line_index=frame.f_lineno)
                    self.write_return_or_exit(called_end, arg)

        self.exporter.write_raw_content(f"' e:ret {self.error_to_handle_with_line=}\n")
        return self.exceptiontrace
