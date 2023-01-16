from contextlib import contextmanager
from io import TextIOBase
from typing import Any, Iterator

from pydoctrace.domain.sequence import Call, Error


class Exporter:
    '''
    Base class for sequence diagram exporters.
    Extend it to to support various export formats.
    '''
    def __init__(self, io_sink: TextIOBase):
        self.io_sink = io_sink

    def write_header(self, start_module: str, start_func_name: str):
        '''
        Writes the header of the sequence diagram file.
        This method is supposed to be called only once during an export process.
        '''
        raise NotImplementedError()

    def write_raw_content(self, raw_content: str):
        '''
        Writes the given raw content to the sink.
        This is not to be used directly.
        '''
        self.io_sink.write(raw_content)

    def write_tracing_start(self, called: Call):
        '''
        Writes the diagram content leading to the first call (the decorated function).
        This may be a no-operation
        '''
        raise NotImplementedError()

    def write_start_call(self, caller: Call, called: Call):
        '''
        Writes the diagram content corresponding to a call between:
        - a caller: the block of code being executed
        - a called: a block of code being called
        These blocks of code are functions or methods.
        '''
        raise NotImplementedError()

    def format_arg_value(self, arg: Any) -> str:
        '''
        Formats a value being included in the diagram contents.
        Typically, a value returned by a function.
        Special care must be taken for the None value.
        '''
        raise NotImplementedError()

    def write_error_propagation(self, error_called: Call, error_caller: Call, error: Error):
        '''
        Writes the diagram contents corresponding to an error propagating
        between the called (which raised or propagated the error) and its caller
        '''
        raise NotImplementedError()

    def write_return(self, called: Call, caller: Call, arg: Any):
        '''
        Writes the diagram contents corresponding to a value returned
        by a called block of code to a caller block of code.
        '''
        raise NotImplementedError()

    def write_tracing_end(self, called: Call, arg: Any):
        '''
        Special case of write_return when the last executed function returns a value.
        '''
        raise NotImplementedError()

    def write_unhandled_error_end(self, called: Call, error: Error):
        '''
        Special case of write_tracing_end when an error was not handled by an except block.
        '''
        raise NotImplementedError()

    def write_footer(self):
        '''
        Writes the footer of the sequence diagram file.
        This method is supposed to be called only once during an export process.
        '''
        raise NotImplementedError()

    @staticmethod
    @contextmanager
    def export_manager_manager(export_file_path: str) -> Iterator['Exporter']:
        '''
        This factory function is meant to be used as a context manager to provide
        an exporter instance usable during the lifetime of the export context.

        The lifetime of the exporter instance is bound to the one of the context, which often
        involves a file handler resource (the export file being written) that is closed at
        the end of the context.
        '''
        raise NotImplementedError()
