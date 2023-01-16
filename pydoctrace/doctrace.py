from contextlib import contextmanager
from functools import wraps
from typing import Callable, Iterator

from pydoctrace.domain.context import Context
from pydoctrace.exporters.plantuml import PlantUMLExporter
from pydoctrace.tracer import SequenceTracer


@contextmanager
def trace_parse_export(context: Context) -> Iterator[SequenceTracer]:
    with context.exporter_class.export_manager_manager(context.export_file_path) as exporter:
        # initializes the diagram file
        exporter.write_header(context.start_module, context.start_function_name)

        tracer = SequenceTracer(exporter)
        try:
            yield tracer
        finally:
            # finalizes the sequence diagram file
            exporter.write_footer()


def trace_to_puml(function_to_trace: Callable):
    '''
    Decorates a function in order to trace its execution as a sequence diagram.
    '''
    @wraps(function_to_trace)
    def traceable_func(*args, **kwargs):
        # initializes the tracing context
        function_to_trace_name = getattr(function_to_trace, '__name__', '__main__')
        function_to_trace_module = getattr(function_to_trace, '__module__', '__root__')
        # exports to PlantUML by default
        export_file_path = f'{function_to_trace_name}.puml'
        context = Context(PlantUMLExporter, export_file_path, function_to_trace_module, function_to_trace_name)

        # runs the decorated function in a tracing context
        with trace_parse_export(context) as tracer:
            return tracer.runfunc(function_to_trace, *args, **kwargs)

    return traceable_func
