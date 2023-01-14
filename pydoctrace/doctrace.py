from contextlib import contextmanager, redirect_stdout
from functools import wraps
from trace import Trace
from typing import Callable


class TraceParser:
    def __init__(self, output_file):
        self.output_file = output_file

    def write(self, traceline: str):
        if len(traceline) > 0:
            self.output_file.write(f"' {traceline}")


@contextmanager
def trace_and_parse_to_filepath(filepath: str, function_name: str):
    with open(filepath, 'w', encoding='utf8') as traces_file:
        traces_file.write(f'@startuml {function_name}\n')
        traces_file.write(f'participant {function_name}\n')

        parser = TraceParser(traces_file)
        with redirect_stdout(parser):
            yield Trace(count=False)

        traces_file.write('@enduml\n')


def trace_to_puml(func_to_trace: Callable):
    '''
    Decorates a function to trace its execution as a sequence diagram.
    '''
    @wraps(func_to_trace)
    def traceable_func(*args, **kwargs):
        func_to_trace_name = getattr(func_to_trace, '__name__', '__main__')
        with trace_and_parse_to_filepath(f'{func_to_trace_name}.puml', func_to_trace_name) as tracer:
            return tracer.runfunc(func_to_trace, *args, **kwargs)

    return traceable_func
