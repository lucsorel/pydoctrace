from contextlib import contextmanager
from functools import wraps
from typing import Callable, Iterator

from pydoctrace.exporters import Context
from pydoctrace.exporters.plantuml.component import PlantUMLComponentExporter
from pydoctrace.exporters.plantuml.sequence import PlantUMLSequenceExporter
from pydoctrace.tracer import ExecutionTracer


@contextmanager
def tracing_context_factory(context: Context) -> Iterator[ExecutionTracer]:
    with context.exporter_class.export_manager_factory(context.export_file_path) as exporter:
        # initializes the diagram file
        exporter.on_header(context.start_module, context.start_function_name)

        tracer = ExecutionTracer(exporter)
        try:
            yield tracer
        finally:
            # finalizes the sequence diagram file
            exporter.on_footer()


def trace_to_sequence_puml(function_to_trace: Callable):
    '''
    Decorates a function in order to trace its execution as a sequence diagram.
    '''
    @wraps(function_to_trace)
    def traceable_func(*args, **kwargs):
        # initializes the tracing context
        function_to_trace_name = getattr(function_to_trace, '__name__', '__main__')
        function_to_trace_module = getattr(function_to_trace, '__module__', '__root__')
        # exports to PlantUML by default
        export_file_path = f'{function_to_trace_name}-sequence.puml'
        context = Context(PlantUMLSequenceExporter, export_file_path, function_to_trace_module, function_to_trace_name)

        # runs the decorated function in a tracing context
        with tracing_context_factory(context) as execution_tracer:
            return execution_tracer.runfunc(function_to_trace, *args, **kwargs)

    return traceable_func


def trace_to_component_puml(function_to_trace: Callable):
    '''
    Decorates a function in order to trace its execution as a component diagram.
    '''
    @wraps(function_to_trace)
    def traceable_func(*args, **kwargs):
        # initializes the tracing context
        function_to_trace_name = getattr(function_to_trace, '__name__', '__main__')
        function_to_trace_module = getattr(function_to_trace, '__module__', '__root__')
        # exports to PlantUML by default
        export_file_path = f'{function_to_trace_name}-component.puml'
        context = Context(PlantUMLComponentExporter, export_file_path, function_to_trace_module, function_to_trace_name)

        # runs the decorated function in a tracing context
        with tracing_context_factory(context) as execution_tracer:
            return execution_tracer.runfunc(function_to_trace, *args, **kwargs)

    return traceable_func
